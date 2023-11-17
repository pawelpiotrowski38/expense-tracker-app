import time
from datetime import datetime
from functools import partial
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from PyQt5.QtChart import QChart, QPieSeries, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSlice
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QPainter, QFont, QBrush, QColor, QIcon
from PyQt5.QtSql import QSqlQuery, QSqlTableModel, QSqlRelation, QSqlRelationalTableModel
from PyQt5.QtWidgets import QPushButton, QLabel, QGridLayout, QFrame


class FillChartsFunctions:

    def __init__(self):
        super().__init__()

    def fillBudgetsCharts(self):
        def clearLayout(layout):
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                    else:
                        clearLayout(item.layout())

        if self.areBudgetsChartsShown:
            clearLayout(self.rightBudgetsPanelVLayout)
        selectBudgetsQuery = QSqlQuery()
        budgetsID = []
        selectBudgetsQuery.exec(f"SELECT budgetID FROM budgets WHERE userID = {self.userID}")
        while selectBudgetsQuery.next():
            budgetsID.append(selectBudgetsQuery.value(0))

        nameLabels = []
        emptyLabels1 = []
        categoryLabels = []
        amountLabels = []
        remainAmountLabels = []
        emptyLabels2 = []
        gridLayouts = []
        gridLayouts2 = []
        leftArrowButtons = []
        rightArrowButtons = []
        emptyLabels3 = []
        budgetEntriesID = []
        lines = []

        for i in range(len(budgetsID)):
            nameLabel = QLabel("")
            nameLabels.append(nameLabel)
            emptyLabel1 = QLabel("")
            emptyLabels1.append(emptyLabel1)
            categoryLabel = QLabel("")
            categoryLabels.append(categoryLabel)
            amountLabel = QLabel("")
            amountLabels.append(amountLabel)
            remainAmountLabel = QLabel("")
            remainAmountLabels.append(remainAmountLabel)
            emptyLabel2 = QLabel("")
            emptyLabels2.append(emptyLabel2)
            gridLayout = QGridLayout()
            # gridLayout.setRowMinimumHeight(0, 150)
            gridLayout.setColumnMinimumWidth(0, 250)
            gridLayouts.append(gridLayout)
            gridLayout2 = QGridLayout()
            gridLayout2.setRowMinimumHeight(0, 160)
            gridLayout2.setColumnMinimumWidth(0, 160)
            gridLayouts2.append(gridLayout2)
            leftArrowButton = QPushButton()
            leftArrowButton.setMinimumWidth(40)
            leftArrowButton.setIcon(QIcon('icons/leftArrow.png'))
            leftArrowButtons.append(leftArrowButton)
            rightArrowButton = QPushButton()
            rightArrowButton.setMinimumWidth(40)
            rightArrowButton.setIcon(QIcon('icons/rightArrow.png'))
            rightArrowButtons.append(rightArrowButton)
            emptyLabel3 = QLabel("     ")
            emptyLabels3.append(emptyLabel3)
            horizontalLine = QFrame()
            horizontalLine.setFrameShape(QFrame.HLine)
            horizontalLine.setFrameShadow(QFrame.Sunken)
            lines.append(horizontalLine)

        def draw(entryAmount, amount):
            remainAmount = amount - entryAmount

            pieSeries = QPieSeries()
            pieSeries.setPieSize(1.0)
            pieSeries.setHoleSize(0.5)

            pieSlice = QPieSlice("entryAmount", entryAmount)
            if (entryAmount / amount) * 100 < 80:
                pieSlice.setColor(Qt.darkGreen)
                pieSlice.setBorderColor(Qt.darkGreen)
            elif 80 <= (entryAmount / amount) * 100 <= 100:
                pieSlice.setColor(QColor(255, 130, 1))
                pieSlice.setBorderColor(QColor(255, 130, 1))
            else:
                pieSlice.setColor(Qt.red)
                pieSlice.setBorderColor(Qt.red)
            pieSeries.append(pieSlice)
            if remainAmount >= 0:
                pieSlice = QPieSlice("remainAmount", remainAmount)
                pieSlice.setColor(Qt.darkGray)
                pieSlice.setBorderColor(Qt.darkGray)
                pieSeries.append(pieSlice)

            chart = QChart()
            chart.addSeries(pieSeries)
            chart.createDefaultAxes()
            chart.setBackgroundBrush(QBrush(QColor("transparent")))
            chart.legend().setVisible(False)

            chartView = QChartView(chart)
            chartView.setRenderHint(QPainter.Antialiasing)

            return chartView

        def changeBudgetChart(direction, position):
            changeChartQuery = QSqlQuery()
            if changeChartQuery.exec(
                    f"SELECT budgetID, amount, categoryID, type FROM budgets ORDER BY budgetID OFFSET {position} ROWS FETCH NEXT 1 ROWS ONLY"):
                if changeChartQuery.next():
                    budgetID = changeChartQuery.value(0)
                    amount = Decimal(changeChartQuery.value(1)).quantize(self.fractional, ROUND_HALF_UP)
                    categoryID = changeChartQuery.value(2)
                    type = changeChartQuery.value(3)
                else:
                    return
                if type == "One-time":
                    return
            else:
                print(changeChartQuery.lastError().databaseText())
                return

            entries = []
            if changeChartQuery.exec(f"SELECT budgetEntryID FROM budgetEntries WHERE budgetID = {budgetID}"):
                while changeChartQuery.next():
                    entries.append(changeChartQuery.value(0))
            else:
                print(changeChartQuery.lastError().databaseText())

            if len(entries) == 1:
                return
            else:
                for i in range(len(entries)):
                    if entries[i] == budgetEntriesID[position] and direction == "left":
                        try:
                            if i - 1 == -1:
                                raise IndexError
                            budgetEntriesID[position] = entries[i - 1]
                            if changeChartQuery.exec(
                                    f"SELECT startDate, endDate FROM budgetEntries WHERE budgetEntryID = {budgetEntriesID[position]}"):
                                if changeChartQuery.next():
                                    newStartDate = changeChartQuery.value(0)
                                    newEndDate = changeChartQuery.value(1)
                                else:
                                    return
                            else:
                                return
                            if categoryID == 0:
                                if not changeChartQuery.exec(f"SELECT SUM(value) FROM expenses "
                                                             f"WHERE transactionDate BETWEEN '{newStartDate}' AND '{newEndDate}' AND userID = {self.userID}"):
                                    print(changeChartQuery.lastError().databaseText())
                                if changeChartQuery.next():
                                    newEntryAmount = Decimal(changeChartQuery.value(0)).quantize(self.fractional,
                                                                                                 ROUND_HALF_UP)
                            else:
                                if not changeChartQuery.exec(f"SELECT SUM(value) FROM expenses "
                                                             f"WHERE categoryID = {categoryID} AND transactionDate BETWEEN '{newStartDate}' AND '{newEndDate}' AND userID = {self.userID}"):
                                    print(changeChartQuery.lastError().databaseText())
                                if changeChartQuery.next():
                                    newEntryAmount = Decimal(changeChartQuery.value(0)).quantize(self.fractional,
                                                                                                 ROUND_HALF_UP)
                                else:
                                    return
                            break
                        except IndexError:
                            return
                    elif entries[i] == budgetEntriesID[position] and direction == "right":
                        try:
                            budgetEntriesID[position] = entries[i + 1]
                            if changeChartQuery.exec(
                                    f"SELECT startDate, endDate FROM budgetEntries WHERE budgetEntryID = {budgetEntriesID[position]}"):
                                if changeChartQuery.next():
                                    newStartDate = changeChartQuery.value(0)
                                    newEndDate = changeChartQuery.value(1)
                                else:
                                    return
                            else:
                                return
                            if categoryID == 0:
                                if not changeChartQuery.exec(f"SELECT SUM(value) FROM expenses "
                                                             f"WHERE transactionDate BETWEEN '{newStartDate}' AND '{newEndDate}' AND userID = {self.userID}"):
                                    print(changeChartQuery.lastError().databaseText())
                                if changeChartQuery.next():
                                    newEntryAmount = Decimal(changeChartQuery.value(0)).quantize(self.fractional,
                                                                                                 ROUND_HALF_UP)
                            else:
                                if not changeChartQuery.exec(f"SELECT SUM(value) FROM expenses "
                                                             f"WHERE categoryID = {categoryID} AND transactionDate BETWEEN '{newStartDate}' AND '{newEndDate}' AND userID = {self.userID}"):
                                    print(changeChartQuery.lastError().databaseText())
                                if changeChartQuery.next():
                                    newEntryAmount = Decimal(changeChartQuery.value(0)).quantize(self.fractional,
                                                                                                 ROUND_HALF_UP)
                                else:
                                    return
                            break
                        except IndexError:
                            return
                gridLayouts2[position].removeWidget(chartViews[position])
                chartViews[position] = draw(newEntryAmount, amount)
                gridLayouts2[position].addWidget(chartViews[position], 0, 0)
                nameLabels[position].setText(name + ", from " + newStartDate + " to " + newEndDate)
                amountLabels[position].setText(
                    str(newEntryAmount) + " " + self.currency + " / " + str(amount) + " " + self.currency + ", " + str(
                        round((newEntryAmount / amount), 2) * 100) + "%")
                remainAmountLabels[position].setText(
                    "Remaining amount: " + str(amount - newEntryAmount) + " " + self.currency)

        it = 0
        chartViews = []
        for budgetID in budgetsID:
            selectBudgetsQuery.exec(
                f"SELECT name, amount, categoryID, type, frequency FROM budgets WHERE budgetID = {budgetID}")
            if selectBudgetsQuery.next():
                name = selectBudgetsQuery.value(0)
                amount = Decimal(selectBudgetsQuery.value(1)).quantize(self.fractional, ROUND_HALF_UP)
                categoryID = selectBudgetsQuery.value(2)
            if not categoryID == 0:
                if not selectBudgetsQuery.exec(f"SELECT name FROM categories WHERE categoryID = {categoryID}"):
                    print(selectBudgetsQuery.lastError().databaseText())
                    return -1
                if selectBudgetsQuery.next():
                    category = selectBudgetsQuery.value(0)
                else:
                    return -1
            if not selectBudgetsQuery.exec(f"SELECT MAX(budgetEntryID) FROM budgetEntries WHERE budgetID = {budgetID}"):
                print(selectBudgetsQuery.lastError().databaseText())
            if selectBudgetsQuery.next():
                budgetEntryID = selectBudgetsQuery.value(0)
            if not selectBudgetsQuery.exec(
                    f"SELECT startDate, endDate FROM budgetEntries WHERE budgetEntryID = {budgetEntryID}"):
                print(selectBudgetsQuery.lastError().databaseText())
            if selectBudgetsQuery.next():
                startDate = selectBudgetsQuery.value(0)
                endDate = selectBudgetsQuery.value(1)

            if categoryID == 0:
                categoryLabels[it].setText("All categories")
                if not selectBudgetsQuery.exec(f"SELECT SUM(value) FROM expenses "
                                               f"WHERE transactionDate BETWEEN '{startDate}' AND '{endDate}' AND userID = {self.userID}"):
                    print(selectBudgetsQuery.lastError().databaseText())
                if selectBudgetsQuery.next():
                    entryAmount = Decimal(selectBudgetsQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP)
            else:
                categoryLabels[it].setText("Category: " + category)
                if not selectBudgetsQuery.exec(f"SELECT SUM(value) FROM expenses "
                                               f"WHERE categoryID = {categoryID} AND transactionDate BETWEEN '{startDate}' AND '{endDate}' AND userID = {self.userID}"):
                    print(selectBudgetsQuery.lastError().databaseText())
                if selectBudgetsQuery.next():
                    entryAmount = Decimal(selectBudgetsQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP)

            chartViews.append(draw(entryAmount, amount))

            budgetEntriesID.append(budgetEntryID)
            nameLabels[it].setText(name + ", from " + startDate + " to " + endDate)
            amountLabels[it].setText(
                str(entryAmount) + " " + self.currency + " / " + str(amount) + " " + self.currency + ", " + str(
                    round(entryAmount / amount * 100, 2)) + "%")
            remainAmountLabels[it].setText("Remaining amount: " + str(amount - entryAmount) + " " + self.currency)

            gridLayouts[it].addWidget(emptyLabels1[it], 0, 0)
            gridLayouts[it].addWidget(categoryLabels[it], 1, 0)
            gridLayouts[it].addWidget(amountLabels[it], 2, 0)
            gridLayouts[it].addWidget(remainAmountLabels[it], 3, 0)
            gridLayouts[it].addWidget(emptyLabels2[it], 4, 0)
            gridLayouts[it].addWidget(leftArrowButtons[it], 1, 1, 2, 1)
            gridLayouts[it].addWidget(rightArrowButtons[it], 1, 2, 2, 1)
            gridLayouts2[it].addWidget(chartViews[it], 0, 0)
            gridLayouts2[it].addLayout(gridLayouts[it], 0, 1)
            gridLayouts2[it].addWidget(emptyLabels3[it], 0, 2)
            leftArrowButtons[it].clicked.connect(partial(changeBudgetChart, "left", it))
            rightArrowButtons[it].clicked.connect(partial(changeBudgetChart, "right", it))

            self.rightBudgetsPanelVLayout.addSpacing(10)
            self.rightBudgetsPanelVLayout.addWidget(nameLabels[it], alignment=Qt.AlignCenter)
            self.rightBudgetsPanelVLayout.addLayout(gridLayouts2[it])
            if not budgetID == budgetsID[-1] or len(budgetsID) == 1 or len(budgetsID) == 2:
                self.rightBudgetsPanelVLayout.addWidget(lines[it])
            it += 1
        if len(budgetsID) == 1:
            self.rightBudgetsPanelVLayout.addSpacing(340)
        if len(budgetsID) == 2:
            self.rightBudgetsPanelVLayout.addSpacing(130)

        self.scrollArea.setWidget(self.rightBudgetsPanel)
        self.areBudgetsChartsShown = True

    def fillSummaryPanel(self, theme):
        sumIncomeQuery = QSqlQuery()
        if not sumIncomeQuery.exec(f"SELECT SUM(value) FROM income WHERE userID = {self.userID}"):
            return
        if not sumIncomeQuery.next():
            return
        sumExpensesQuery = QSqlQuery()
        if not sumExpensesQuery.exec(f"SELECT SUM(value) FROM expenses WHERE userID = {self.userID}"):
            return
        if not sumExpensesQuery.next():
            return
        if sumIncomeQuery.value(0) is not None:
            sumIncome = Decimal(sumIncomeQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP)
            self.bottomLeftTransactionsIncomeValue.setText(str(sumIncome))
            self.bottomLeftTransactionsIncomeValue.setStyleSheet("font-size: 16px; color:green")
        else:
            self.bottomLeftTransactionsIncomeValue.setText("0")
        if sumExpensesQuery.value(0) is not None:
            sumExpenses = Decimal(sumExpensesQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP)
            self.bottomLeftTransactionsExpensesValue.setText(str(sumExpenses))
            self.bottomLeftTransactionsExpensesValue.setStyleSheet("font-size: 16px; color:red")
        else:
            self.bottomLeftTransactionsExpensesValue.setText("0")
        if sumIncomeQuery.value(0) is not None or sumExpensesQuery.value(0) is not None:
            total = Decimal(self.bottomLeftTransactionsIncomeValue.text()) - Decimal(
                self.bottomLeftTransactionsExpensesValue.text())
            if total < 0:
                self.bottomLeftTransactionsTotalValue.setStyleSheet("font-size: 16px; color:red")
            else:
                self.bottomLeftTransactionsTotalValue.setStyleSheet("font-size: 16px; color:green")
            self.bottomLeftTransactionsTotalValue.setText(str(total) + " " + self.currency)
        else:
            self.bottomLeftTransactionsTotalValue.setText('0 ' + self.currency)
        self.bottomLeftTransactionsIncomeValue.setText(
            self.bottomLeftTransactionsIncomeValue.text() + " " + self.currency)
        self.bottomLeftTransactionsExpensesValue.setText(
            self.bottomLeftTransactionsExpensesValue.text() + " " + self.currency)
        sumIncomeQuery.finish()
        sumExpensesQuery.finish()

        month1 = datetime.now()
        month2 = datetime.now() - relativedelta(months=1)
        month3 = datetime.now() - relativedelta(months=2)
        month4 = datetime.now() - relativedelta(months=3)

        months = [month1, month2, month3, month4]
        dates = []

        for i in months:
            dates.append(format(i, '%B %Y'))

        self.secondHomeLabel1.setText(dates[0])
        self.secondHomeLabel2.setText(dates[1])
        self.secondHomeLabel3.setText(dates[2])
        self.secondHomeLabel4.setText(dates[3])

        incomeList = []
        expensesList = []

        def draw(inList, exList, chart):
            pieSeries = QPieSeries()
            pieSlice = pieSeries.append('Income', inList)
            pieSlice.setColor(Qt.darkGreen)
            pieSlice.setBorderColor(Qt.darkGreen)
            pieSlice = pieSeries.append('Expenses', exList)
            pieSlice.setColor(Qt.red)
            pieSlice.setBorderColor(Qt.red)
            if inList == 0:
                pieSlice.setBorderColor(Qt.red)
            if exList == 0:
                pieSlice.setBorderColor(Qt.darkGreen)
            if inList == 0 and exList == 0:
                pieSlice = pieSeries.append('', 1)
                pieSlice.setBorderColor(Qt.darkGray)
                pieSlice.setColor(Qt.darkGray)
            pieSeries.setPieSize(1.0)
            pieSeries.setHoleSize(0.5)

            chart.addSeries(pieSeries)
            chart.createDefaultAxes()
            if theme:
                chart.setBackgroundBrush(QBrush(QColor(44, 45, 50, 255)))
            else:
                chart.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
            chart.legend().setVisible(False)

            chartView = QChartView(chart)
            chartView.setRenderHint(QPainter.Antialiasing)
            if theme:
                chartView.setBackgroundBrush(QBrush(QColor(44, 45, 50, 255)))
            else:
                chartView.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
            chartView.setGeometry(0, 0, 500, 500)
            chartView.setAlignment(Qt.AlignLeft)

            return chartView

        selectExQuery = QSqlQuery()
        selectInQuery = QSqlQuery()
        for i in range(len(months)):
            tempDate = (str(months[i].replace(day=1)))[:10]
            selectExQuery.exec(
                f"SELECT SUM(value) FROM expenses WHERE transactionDate >= '{tempDate}' AND transactionDate < DATEADD(month, 1, '{tempDate}') AND userID = {self.userID}")
            selectInQuery.exec(
                f"SELECT SUM(value) FROM income WHERE transactionDate >= '{tempDate}' AND transactionDate < DATEADD(month, 1, '{tempDate}') AND userID = {self.userID}")
            while selectExQuery.next():
                expensesList.append(Decimal(selectExQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
            while selectInQuery.next():
                incomeList.append(Decimal(selectInQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))

        chartViewes = []
        for i in range(len(months)):
            tmp = draw(incomeList[i], expensesList[i], self.chartsList[i])
            chartViewes.append(tmp)

        self.secondHomeLabel12.setText(str(incomeList[0]) + " " + self.currency)
        self.secondHomeLabel12.setStyleSheet(f"font-family: '{self.fontName}'; font-size: 16px; color:darkGreen")
        self.secondHomeLabel14.setText(str(expensesList[0]) + " " + self.currency)
        self.secondHomeLabel14.setStyleSheet(f"font-family: '{self.fontName}'; font-size: 16px; color:red")
        self.secondHomeLabel16.setText(str(incomeList[0] - expensesList[0]) + ' ' + self.currency)
        if (incomeList[0] - expensesList[0]) < 0:
            self.secondHomeLabel16.setStyleSheet(f"font-family: '{self.fontName}'; font-size: 16px; color:red")
        else:
            self.secondHomeLabel16.setStyleSheet(f"font-family: '{self.fontName}'; font-size: 16px; color:darkGreen")
        self.secondHomeLabel22.setText(str(incomeList[1]) + " " + self.currency)
        self.secondHomeLabel22.setStyleSheet("font-size: 16px; color:darkGreen")
        self.secondHomeLabel24.setText(str(expensesList[1]) + " " + self.currency)
        self.secondHomeLabel24.setStyleSheet("font-size: 16px; color:red")
        self.secondHomeLabel26.setText(str(incomeList[1] - expensesList[1]) + ' ' + self.currency)
        if (incomeList[1] - expensesList[1]) < 0:
            self.secondHomeLabel26.setStyleSheet("font-size: 16px; color:red")
        else:
            self.secondHomeLabel26.setStyleSheet("font-size: 16px; color:darkGreen")
        self.secondHomeLabel32.setText(str(incomeList[2]) + " " + self.currency)
        self.secondHomeLabel32.setStyleSheet("font-size: 16px; color:darkGreen")
        self.secondHomeLabel34.setText(str(expensesList[2]) + " " + self.currency)
        self.secondHomeLabel34.setStyleSheet("font-size: 16px; color:red")
        self.secondHomeLabel36.setText(str(incomeList[2] - expensesList[2]) + ' ' + self.currency)
        if (incomeList[2] - expensesList[2]) < 0:
            self.secondHomeLabel36.setStyleSheet("font-size: 16px; color:red")
        else:
            self.secondHomeLabel36.setStyleSheet("font-size: 16px; color:darkGreen")
        self.secondHomeLabel42.setText(str(incomeList[3]) + " " + self.currency)
        self.secondHomeLabel42.setStyleSheet("font-size: 16px; color:darkGreen")
        self.secondHomeLabel44.setText(str(expensesList[3]) + " " + self.currency)
        self.secondHomeLabel44.setStyleSheet("font-size: 16px; color:red")
        self.secondHomeLabel46.setText(str(incomeList[3] - expensesList[3]) + ' ' + self.currency)
        if (incomeList[3] - expensesList[3]) < 0:
            self.secondHomeLabel46.setStyleSheet("font-size: 16px; color:red")
        else:
            self.secondHomeLabel46.setStyleSheet("font-size: 16px; color:darkGreen")

        self.secondHomePanelGridLayout1.addWidget(chartViewes[0], 1, 0)
        self.secondHomePanelGridLayout2.addWidget(chartViewes[1], 1, 0)
        self.secondHomePanelGridLayout3.addWidget(chartViewes[2], 1, 0)
        self.secondHomePanelGridLayout4.addWidget(chartViewes[3], 1, 0)

    def fillDailyCharts(self, theme):
        if self.areDailyChartsShown:
            self.thirdHomePanelMainLayout.removeWidget(self.chartViewEx)
            self.fourthHomePanelMainLayout.removeWidget(self.chartViewIn)
            self.thirdHomeChart = QChart()
            self.fourthHomeChart = QChart()
        days = []
        exList = []
        inList = []
        days.append(str(datetime.now())[:10])
        for i in range(6):
            day = str(datetime.now() - relativedelta(days=(i + 1)))[:10]
            days.append(day)

        selectExQuery = QSqlQuery()
        selectInQuery = QSqlQuery()
        timeList = []
        for i in range(7):
            tempDate = days[i]
            selectExQuery.exec(
                f"SELECT SUM(value) FROM expenses WHERE transactionDate = '{tempDate}' AND userID = {self.userID}")
            selectInQuery.exec(
                f"SELECT SUM(value) FROM income WHERE transactionDate = '{tempDate}' AND userID = {self.userID}")
            while selectExQuery.next():
                exList.append(Decimal(selectExQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
            while selectInQuery.next():
                inList.append(selectInQuery.value(0))
            timeList.append(days[i][5:])
        timeList.reverse()
        
        chartFont = QFont(self.fontt.family())
        chartFont.setPixelSize(self.fontt.pointSize()+1)
        

        def draw(table_name, color, vList, timeList, chart, title, currency, font):
            vList.reverse()
            barSet = QBarSet(table_name.capitalize())
            barSet.setColor(color)
            barSet.append(vList)
            barSet.setLabelColor(Qt.black)
            barSet.setBorderColor(color)

            barSeries = QBarSeries()
            barSeries.setBarWidth(0.6)
            barSeries.append(barSet)

            chart.addSeries(barSeries)
            chart.setTitleFont(font)
            chart.setTitle(title)
            chart.legend().setVisible(False)

            axisX = QBarCategoryAxis()
            axisX.setTitleText('Time')
            axisX.setLabelsFont(font)
            axisX.append(timeList)
            chart.addAxis(axisX, Qt.AlignBottom)
            barSeries.attachAxis(axisX)

            axisY = QValueAxis()
            axisY.setTitleText('Value (' + currency + ')')
            axisY.setLabelFormat("%.2f")
            axisY.setLabelsFont(font)
            chart.addAxis(axisY, Qt.AlignLeft)
            barSeries.attachAxis(axisY)

            if theme:
                chart.setBackgroundBrush(QBrush(QColor(27, 29, 30, 255)))
                chart.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))
                axisX.setLabelsBrush(QBrush(QColor(228, 231, 235, 255)))
                axisX.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))
                axisY.setLabelsBrush(QBrush(QColor(228, 231, 235, 255)))
                axisY.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))
            else:
                chart.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))

            def barHovered(status, index, bars):
                if status:
                    chart.setToolTip("{:.2f}".format(bars.at(index)) + " " + currency)
                else:
                    chart.setToolTip("")

            barSeries.hovered.connect(barHovered)

            chartView = QChartView(chart)
            chartView.setRenderHint(QPainter.Antialiasing)

            return chartView

        self.chartViewEx = draw('expenses', Qt.red, exList, timeList, self.thirdHomeChart,
                                'Daily expenses (last 7 days)', self.currency, chartFont)
        self.chartViewIn = draw('income', Qt.darkGreen, inList, timeList, self.fourthHomeChart,
                                'Daily income (last 7 days)', self.currency, chartFont)
        if theme:
            self.chartViewEx.setBackgroundBrush(QBrush(QColor(27, 29, 30, 255)))
            self.chartViewIn.setBackgroundBrush(QBrush(QColor(27, 29, 30, 255)))
        else:
            self.chartViewEx.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
            self.chartViewIn.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))

        self.thirdHomePanelMainLayout.addWidget(self.chartViewEx)
        self.fourthHomePanelMainLayout.addWidget(self.chartViewIn)

        self.areDailyChartsShown = True
