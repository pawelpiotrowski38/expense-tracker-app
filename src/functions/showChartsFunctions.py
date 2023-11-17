from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from PyQt5.QtChart import QChart, QPieSeries, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSlice
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPainter, QFont, QBrush, QColor
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QMessageBox, QScrollBar


class ShowChartsFunctions:
        
    def showReportCategory(self):
        """Metoda wyświetlająca wykres z podziałem na kategorie"""
        reportMsg = QMessageBox()
        reportMsg.setWindowTitle("Warning")
        reportMsg.setIcon(QMessageBox.Warning)
        
        if self.isChartShown:
            self.rightReportsPanelVLayout.removeWidget(self.chartView)
            if self.isScrollShown:
                self.rightReportsPanelVLayout.removeWidget(self.scrollbar)
            self.chart = QChart()
        
        dateFrom = self.topLeftReportsFromEntry.date().toPyDate()
        dateTo = self.topLeftReportsToEntry.date().toPyDate()
        if dateFrom > dateTo:
            reportMsg.setText("Start date cannot be later than end date!")
            reportMsg.exec()
            return

        catList = []
        exList = []
        inList = []

        titleFont = QFont('Arial')
        titleFont.setPixelSize(15)
        axisFont = QFont('Arial')
        axisFont.setPixelSize(15)

        def drawReport(tableName, color, dateFrom, dateTo, catList, exList, inList, titleFont, axisFont, currency):
            """Metoda rysująca wykres"""
            reportQuery = QSqlQuery()
            reportWhileQuery = QSqlQuery()
            
            reportQuery.exec(f"SELECT categoryID, name from categories WHERE categoryType = '{tableName}' AND userID = {self.userID}")
            while reportQuery.next():
                tempCategoryID = reportQuery.value(0)
                tempCategoryName = reportQuery.value(1)

                if self.topLeftReportsAcCheck.isChecked():
                    if dateFrom == dateTo:
                        reportWhileQuery.exec(f"SELECT SUM(value) FROM {tableName} "
                                              f"WHERE categoryID = {tempCategoryID} AND transactionDate = '{dateFrom}' AND userID = {self.userID}")
                    else:
                        reportWhileQuery.exec(f"SELECT SUM(value) FROM {tableName} "
                                              f"WHERE categoryID = {tempCategoryID} AND transactionDate BETWEEN '{dateFrom}' AND '{dateTo}' AND userID = {self.userID}")
                else:
                    account = self.topLeftReportsAccountEntry.currentText()
                    if not account:
                        reportMsg.setText("Account is not selected!")
                        reportMsg.exec()
                        reportQuery.finish()
                        reportWhileQuery.finish()
                        return
                    if not reportWhileQuery.exec(f"SELECT accountID FROM accounts WHERE name = '{account}' AND userID = {self.userID}"):
                        print(reportWhileQuery.lastError().databaseText())
                        return -1
                    if reportWhileQuery.next():
                        accountID = reportWhileQuery.value(0)
                    else:
                        return -1

                    if dateFrom == dateTo:
                        reportWhileQuery.exec(f"SELECT SUM(value) FROM {tableName} "
                                              f"WHERE categoryID = {tempCategoryID} AND accountID = {accountID} AND transactionDate = '{dateFrom}' AND userID = {self.userID}")
                    else:
                        reportWhileQuery.exec(f"SELECT SUM(value) FROM {tableName} "
                                              f"WHERE categoryID = {tempCategoryID} AND accountID = {accountID} AND transactionDate BETWEEN '{dateFrom}' AND '{dateTo}' AND userID = {self.userID}")
                if reportWhileQuery.next():
                    tempEx = reportWhileQuery.value(0)
                    if tempEx == 0:
                        continue
                    else:
                        exList.append(tempEx)
                catList.append(tempCategoryName)
            reportQuery.finish()
            reportWhileQuery.finish()
                
            if self.topLeftReportsTypeEntry.currentText() == 'Bar chart':               
                barSet = QBarSet(tableName.capitalize())
                barSet.setColor(color)
                barSet.append(exList)
                barSet.setLabelColor(Qt.black)
                
                barSeries = QBarSeries()
                barSeries.append(barSet)
                if len(catList) > 3:
                    barSeries.setBarWidth(0.7)
                else:
                    barSeries.setBarWidth(0.4)

                self.chart.addSeries(barSeries)
                self.chart.setTitleFont(titleFont)         
                self.chart.setTitle(tableName.capitalize() + ' from ' + str(dateFrom) + ' to ' + str(dateTo))
                self.chart.setAnimationOptions(QChart.SeriesAnimations)
                self.chart.legend().setVisible(False)

                axisX = QBarCategoryAxis()
                axisX.setLabelsFont(axisFont)
                axisX.append(catList)
                self.chart.addAxis(axisX, Qt.AlignBottom)
                barSeries.attachAxis(axisX)

                axisY = QValueAxis()
                axisY.setTitleText('Value (' + currency + ')')
                axisY.setLabelFormat("%.2f")
                axisY.setLabelsFont(axisFont)
                self.chart.addAxis(axisY, Qt.AlignLeft)
                barSeries.attachAxis(axisY)

                if self.theme:
                    axisX.setLabelsBrush(QBrush(QColor(228, 231, 235, 255)))
                    axisY.setLabelsBrush(QBrush(QColor(228, 231, 235, 255)))
                    axisY.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))

                def barHovered(status, index, bars):
                    """Metoda wyświetlająca wartość słupka po najechaniu na niego kursorem"""
                    if status:
                        self.chart.setToolTip("{:.2f}".format(bars.at(index)) + " " + currency)
                    else:
                        self.chart.setToolTip("")

                barSeries.hovered.connect(barHovered)

                self.chartView = QChartView(self.chart)
                self.chartView.setRenderHint(QPainter.Antialiasing)
                self.rightReportsPanelVLayout.addWidget(self.chartView)
                self.isChartShown = True
                
            else:             
                pieSeries = QPieSeries()
                pieSeries.setPieSize(0.9)
                
                for i in range(len(catList)):
                    pieSlice = QPieSlice(str(catList[i]), exList[i])
                    pieSeries.append(pieSlice)
                    
                it = 0
                for slice in pieSeries.slices():
                    slice.setLabel(str(catList[it]))
                    if len(pieSeries.slices()) == 1:
                        slice.setBorderWidth(-1)
                    it += 1

                self.chart.addSeries(pieSeries)
                self.chart.createDefaultAxes()
                self.chart.setAnimationOptions(QChart.SeriesAnimations)
                self.chart.setTitleFont(titleFont)
                self.chart.setTitle(tableName.capitalize() + ' from ' + str(dateFrom) + ' to ' + str(dateTo))
 
                self.chart.legend().setVisible(True)
                self.chart.legend().setFont(axisFont)
                self.chart.legend().setAlignment(Qt.AlignRight)
                
                it = 0
                for i in pieSeries.slices():
                    self.chart.legend().markers(pieSeries)[it].setLabel((str(catList[it]) + ', ' + "{:.2f}".format(i.value()) + ' ' + currency + ' ' + "{:.2f}".format(100*i.percentage()) + '%'))
                    it += 1
                
                self.chartView = QChartView(self.chart)
                self.chartView.setRenderHint(QPainter.Antialiasing)
 
                self.rightReportsPanelVLayout.addWidget(self.chartView)
                self.isChartShown = True

                def sliceHovered(pieSlice, state):
                    """Metoda wyróżniająca wycinek koła i wyświetlająca nazwę kateogrii po najechaniu na niego kursorem"""
                    pieSlice.setExplodeDistanceFactor(0.075)
                    pieSlice.setExploded(True)
                    self.chart.setToolTip(pieSlice.label())
                    if not state or len(pieSeries.slices()) == 1:
                        pieSlice.setExploded(False)
                        self.chart.setToolTip("")

                pieSeries.hovered.connect(sliceHovered)
            if self.theme:
                self.chart.setBackgroundBrush(QBrush(QColor(27, 29, 30, 255)))
                self.chart.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))
                self.chart.legend().setLabelColor(QColor(228, 231, 235, 255))
                self.chartView.setBackgroundBrush(QBrush(QColor(27, 29, 30, 255)))
            else:
                self.chart.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
                self.chartView.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
        
        if self.topLeftReportsExRadioButton.isChecked():
            drawReport('expenses', Qt.red, dateFrom, dateTo, catList, exList, inList, titleFont, axisFont, self.currency)
            
        elif self.topLeftReportsInRadioButton.isChecked():
            drawReport('income', Qt.darkGreen, dateFrom, dateTo, catList, exList, inList, titleFont, axisFont, self.currency)
    
        elif self.topLeftReportsBothRadioButton.isChecked():
            reportInQuery = QSqlQuery()
            reportExQuery = QSqlQuery()
            sumIncome = sumExpenses = 0

            if self.topLeftReportsAcCheck.isChecked():
                if dateFrom == dateTo:
                    reportInQuery.exec(f"SELECT SUM(value) FROM income WHERE transactionDate = '{dateTo}' AND userID = {self.userID}")
                    reportExQuery.exec(f"SELECT SUM(value) FROM expenses WHERE transactionDate = '{dateTo}' AND userID = {self.userID}")
                else:
                    reportInQuery.exec(f"SELECT SUM(value) FROM income WHERE transactionDate BETWEEN '{dateFrom}' AND '{dateTo}' AND userID = {self.userID}")
                    reportExQuery.exec(f"SELECT SUM(value) FROM expenses WHERE transactionDate BETWEEN '{dateFrom}' AND '{dateTo}' AND userID = {self.userID}")
            else:
                account = self.topLeftReportsAccountEntry.currentText()
                if not account:
                    reportMsg.setText("Account is not selected!")
                    reportMsg.exec()
                    reportInQuery.finish()
                    reportExQuery.finish()
                    return
                if not reportExQuery.exec(f"SELECT accountID FROM accounts WHERE name = '{account}' AND userID = {self.userID}"):
                    print(reportExQuery.lastError().databaseText())
                    return -1
                if reportExQuery.next():
                    accountID = reportExQuery.value(0)
                else:
                    return -1

                if dateFrom == dateTo:
                    reportInQuery.exec(f"SELECT SUM(value) FROM income WHERE accountID = {accountID} AND transactionDate = '{dateTo}' AND userID = {self.userID}")
                    reportExQuery.exec(f"SELECT SUM(value) FROM expenses WHERE accountID = {accountID} AND transactionDate = '{dateTo}' AND userID = {self.userID}")
                else:
                    reportInQuery.exec(f"SELECT SUM(value) FROM income WHERE accountID = {accountID} AND transactionDate BETWEEN '{dateFrom}' AND '{dateTo}' AND userID = {self.userID}")
                    reportExQuery.exec(f"SELECT SUM(value) FROM expenses WHERE accountID = {accountID} AND transactionDate BETWEEN '{dateFrom}' AND '{dateTo}' AND userID = {self.userID}")

            if reportInQuery.next():
                sumIncome = reportInQuery.value(0)
            if reportExQuery.next():
                sumExpenses = reportExQuery.value(0)

            reportInQuery.finish()
            reportExQuery.finish()

            if self.topLeftReportsTypeEntry.currentText() == 'Bar chart':
                incomeBarSet = QBarSet('Income')
                incomeBarSet.setColor(Qt.darkGreen)
                incomeBarSet.setLabelColor(Qt.black)
                expenseBarSet = QBarSet('Expenses')
                expenseBarSet.setColor(Qt.red)
                expenseBarSet.setLabelColor(Qt.black)
            
                incomeBarSet.append([sumIncome])
                expenseBarSet.append([sumExpenses])

                barSeries = QBarSeries()
                barSeries.setBarWidth(0.5)
                barSeries.append(incomeBarSet)
                barSeries.append(expenseBarSet)

                self.chart.addSeries(barSeries)
                self.chart.setTitle('Income and expenses from ' + str(dateFrom) + ' to ' + str(dateTo))
                self.chart.setTitleFont(titleFont)
                self.chart.setAnimationOptions(QChart.SeriesAnimations)
                self.chart.legend().setVisible(True)
                self.chart.legend().setFont(axisFont)
                self.chart.legend().setAlignment(Qt.AlignBottom)

                axisLabels = (['', ''])

                axisX = QBarCategoryAxis()
                axisX.append(axisLabels)
                axisX.setLabelsFont(axisFont)
                self.chart.addAxis(axisX, Qt.AlignBottom)
                barSeries.attachAxis(axisX)

                axisY = QValueAxis()
                axisY.setTitleText('Value (' + self.currency + ')')
                axisY.setLabelFormat("%.2f")
                axisY.setLabelsFont(axisFont)
                self.chart.addAxis(axisY, Qt.AlignLeft)
                barSeries.attachAxis(axisY)

                if self.theme:
                    axisX.setLabelsBrush(QBrush(QColor(228, 231, 235, 255)))
                    axisY.setLabelsBrush(QBrush(QColor(228, 231, 235, 255)))
                    axisY.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))

                def barHovered(status, index, bars):
                    """Metoda wyświetlająca wartość słupka po najechaniu na niego kursorem"""
                    if status:
                        self.chart.setToolTip("{:.2f}".format(bars.at(index)) + " " + self.currency)
                    else:
                        self.chart.setToolTip("")

                barSeries.hovered.connect(barHovered)

                self.chartView = QChartView(self.chart)
                self.chartView.setRenderHint(QPainter.Antialiasing)
                self.rightReportsPanelVLayout.addWidget(self.chartView)
                self.isChartShown = True

            else:                
                pieSeries = QPieSeries()
                pieSeries.setPieSize(0.9)
                if not sumIncome == 0:
                    pieSlice = pieSeries.append('Income', sumIncome)
                    pieSlice.setColor(Qt.darkGreen)
                    pieSlice.setBorderWidth(-1)
                if not sumExpenses == 0:
                    pieSlice = pieSeries.append('Expenses', sumExpenses)
                    pieSlice.setColor(Qt.red)
                    pieSlice.setBorderWidth(-1)

                self.chart.addSeries(pieSeries)
                self.chart.createDefaultAxes()
                self.chart.setAnimationOptions(QChart.SeriesAnimations)
                self.chart.setTitleFont(titleFont)
                self.chart.setTitle('Income and expenses from ' + str(dateFrom) + ' to ' + str(dateTo))
 
                self.chart.legend().setVisible(True)
                self.chart.legend().setFont(axisFont)
                self.chart.legend().setAlignment(Qt.AlignRight)

                it = 0
                for i in pieSeries.slices():
                    sliceLabel = i.label()
                    self.chart.legend().markers(pieSeries)[it].setLabel(sliceLabel + ', ' + "{:.2f}".format(i.value()) + ' ' + self.currency + ', ' + "{:.2f}".format(100*i.percentage()) + '%')
                    it += 1
                
                self.chartView = QChartView(self.chart)
                self.chartView.setRenderHint(QPainter.Antialiasing)
                self.rightReportsPanelVLayout.addWidget(self.chartView)
                self.isChartShown = True

                def sliceHovered(pieSlice, state):
                    """Metoda wyróżniająca wycinek koła i wyświetlająca nazwę kateogrii po najechaniu na niego kursorem"""
                    pieSlice.setExplodeDistanceFactor(0.075)
                    pieSlice.setExploded(True)
                    if not state or len(pieSeries.slices()) == 1:
                        pieSlice.setExploded(False)

                pieSeries.hovered.connect(sliceHovered)
            if self.theme:
                self.chart.setBackgroundBrush(QBrush(QColor(27, 29, 30, 255)))
                self.chart.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))
                self.chart.legend().setLabelColor(QColor(228, 231, 235, 255))
                self.chartView.setBackgroundBrush(QBrush(QColor(27, 29, 30, 255)))
            else:
                self.chart.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
                self.chartView.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))

        else:
            reportMsg.setText("Type is not selected!")
            reportMsg.exec()
            return

    def showReportTime(self):
        """Metoda wyświetlająca wykres czasowy"""
        reportMsg = QMessageBox()
        reportMsg.setWindowTitle("Warning")
        reportMsg.setIcon(QMessageBox.Warning)
        
        if self.isChartShown:
            self.rightReportsPanelVLayout.removeWidget(self.chartView)
            if self.isScrollShown:
                self.rightReportsPanelVLayout.removeWidget(self.scrollbar)
            self.chart = QChart()

        dateFrom = self.bottomLeftReportsFromEntry.date().toPyDate()
        dateTo = self.bottomLeftReportsToEntry.date().toPyDate()

        timeList = []
        exList = []
        inList = []

        titleFont = QFont('Arial')
        titleFont.setPixelSize(15)
        axisFont = QFont('Arial')
        axisFont.setPixelSize(15)

        def drawReport(self, table_name, color, dateFrom, dateTo, timeList, exList, inList, titleFont, axisFont, currency):
            """Metoda rysująca wykres"""
            selectSumQuery = QSqlQuery()
            if dateFrom == dateTo and self.bottomLeftReportsDaysRadioButton.isChecked():
                self.range = 0
                if self.bottomLeftReportsAcCheck.isChecked():
                    selectSumQuery.exec(f"SELECT SUM(value) FROM {table_name} WHERE transactoinDate = '{dateFrom}' AND userID = {self.userID}")
                else:
                    account = self.bottomLeftReportsAccountEntry.currentText()
                    if not account:
                        reportMsg.setText("Account is not selected!")
                        reportMsg.exec()
                        return
                    if not selectSumQuery.exec(
                            f"SELECT accountID FROM accounts WHERE name = '{account}' AND userID = {self.userID}"):
                        print(selectSumQuery.lastError().databaseText())
                        return -1
                    if selectSumQuery.next():
                        accountID = selectSumQuery.value(0)
                    else:
                        return -1
                    selectSumQuery.exec(f"SELECT SUM(value) FROM {table_name} WHERE accountID = {accountID} AND transactoinDate = '{dateFrom}' AND userID = {self.userID}")
                while selectSumQuery.next():
                    exList.append(Decimal(selectSumQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
                    day_str = str(dateFrom)
                    timeList.append(day_str[5:])
            else:
                if self.bottomLeftReportsDaysRadioButton.isChecked():
                    if dateFrom > dateTo:
                        reportMsg.setText("Start date cannot be later than end date!")
                        reportMsg.exec()
                        return
                    self.range = 7
                    delta = dateTo - dateFrom
                    for i in range(delta.days + 1):
                        day = dateFrom + timedelta(days=i)
                        if self.bottomLeftReportsAcCheck.isChecked():
                            selectSumQuery.exec(f"SELECT SUM(value) FROM {table_name} WHERE transactionDate = '{day}' AND userID = {self.userID}")
                        else:
                            account = self.bottomLeftReportsAccountEntry.currentText()
                            if not account:
                                reportMsg.setText("Account is not selected!")
                                reportMsg.exec()
                                return
                            if not selectSumQuery.exec(f"SELECT accountID FROM accounts WHERE name = '{account}' AND userID = {self.userID}"):
                                print(selectSumQuery.lastError().databaseText())
                                return -1
                            if selectSumQuery.next():
                                accountID = selectSumQuery.value(0)
                            else:
                                return -1
                            selectSumQuery.exec(f"SELECT SUM(value) FROM {table_name} WHERE accountID = {accountID} AND transactionDate = '{day}' AND userID = {self.userID}")
                        while selectSumQuery.next():
                            exList.append(Decimal(selectSumQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
                            day_str = str(day)
                            timeList.append(day_str[5:])
                else:
                    self.range = 6
                    delta = (dateTo.year - dateFrom.year) * 12 + (dateTo.month - dateFrom.month)
                    if delta < 0:
                        reportMsg.setText("Start date cannot be later than end date!")
                        reportMsg.exec()
                        return
                    tempDate = dateFrom.replace(day=1)
                    for i in range(delta + 1):
                        if self.bottomLeftReportsAcCheck.isChecked():
                            selectSumQuery.exec(f"SELECT SUM(value) FROM {table_name} "
                                                f"WHERE transactionDate >= '{tempDate}' AND transactionDate < DATEADD(month, 1, '{tempDate}') AND userID = {self.userID}")
                        else:
                            account = self.bottomLeftReportsAccountEntry.currentText()
                            if not account:
                                reportMsg.setText("Account is not selected!")
                                reportMsg.exec()
                                return
                            if not selectSumQuery.exec(f"SELECT accountID FROM accounts WHERE name = '{account}' AND userID = {self.userID}"):
                                print(selectSumQuery.lastError().databaseText())
                                return -1
                            if selectSumQuery.next():
                                accountID = selectSumQuery.value(0)
                            else:
                                return -1
                            selectSumQuery.exec(f"SELECT SUM(value) FROM {table_name} "
                                                f"WHERE accountID = {accountID} AND transactionDate >= '{tempDate}' AND transactionDate < DATEADD(month, 1, '{tempDate}') AND userID = {self.userID}")
                        while selectSumQuery.next():
                            exList.append(Decimal(selectSumQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
                            month_str = str(tempDate)
                            timeList.append(month_str[:7])
                        tempDate = tempDate + relativedelta(months=1)
                
            set0 = QBarSet(table_name.capitalize())               
            set0.setColor(color)            
            set0.append(exList)
            set0.setLabelColor(Qt.black)

            self.series = QBarSeries()
            self.series.setBarWidth(0.7)
            self.series.append(set0)

            self.chart.addSeries(self.series)           
            self.chart.setTitleFont(titleFont)
            if self.bottomLeftReportsDaysRadioButton.isChecked():
                self.chart.setTitle(table_name.capitalize() + ' from ' + str(dateFrom) + ' to ' + str(dateTo))
            else:
                dF = str(dateFrom)
                dT = str(dateTo)
                self.chart.setTitle(table_name.capitalize() + ' from ' + str(dF[:7]) + ' to ' + str(dT[:7]))
            #self.chart.setAnimationOptions(QChart.SeriesAnimations)
            self.chart.legend().setVisible(False)

            self.asd = timeList

            axisX = QBarCategoryAxis()
            axisX.append(timeList)
            axisX.setTitleText('Date')
            axisX.setLabelsFont(axisFont)
            self.chart.addAxis(axisX, Qt.AlignBottom)
            self.series.attachAxis(axisX)

            axisY = QValueAxis()
            axisY.setLabelsFont(axisFont)
            axisY.setTitleText('Value (' + currency + ')')
            axisY.setLabelFormat("%.2f")
            self.chart.addAxis(axisY, Qt.AlignLeft)
            self.series.attachAxis(axisY)

            def barHovered(status, index, bars):
                """Metoda wyświetlająca wartość słupka po najechaniu na niego kursorem"""
                if status:
                    self.chart.setToolTip("{:.2f}".format(bars.at(index)) + " " + self.currency)
                else:
                    self.chart.setToolTip("")

            self.series.hovered.connect(barHovered)

            self.chartView = QChartView(self.chart)
            if self.theme:
                self.chart.setBackgroundBrush(QBrush(QColor(27, 29, 30, 255)))
                self.chart.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))
                axisX.setLabelsBrush(QBrush(QColor(228, 231, 235, 255)))
                axisX.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))
                axisY.setLabelsBrush(QBrush(QColor(228, 231, 235, 255)))
                axisY.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))
                self.chartView.setBackgroundBrush(QBrush(QColor(27, 29, 30, 255)))
            else:
                self.chart.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
                self.chartView.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
            self.chartView.setRenderHint(QPainter.Antialiasing)
            self.rightReportsPanelVLayout.addWidget(self.chartView)

            if len(timeList) > self.range and self.range > 0:
                self.scrollbar = QScrollBar(Qt.Horizontal, valueChanged=self.onAxisSliderMoved, pageStep=self.range)
                self.scrollbar.setMinimum(0)
                self.scrollbar.setMaximum(len(timeList)-self.range)
                self.scrollbar.valueChanged.connect(self.onAxisSliderMoved)
                self.rightReportsPanelVLayout.addWidget(self.scrollbar)
                self.onAxisSliderMoved(self.scrollbar.value())
                self.isScrollShown = True
      
            self.isChartShown = True
 
        if self.bottomLeftReportsExRadioButton.isChecked():
            drawReport(self, 'expenses', Qt.red, dateFrom, dateTo, timeList, exList, inList, titleFont, axisFont, self.currency)
            
        elif self.bottomLeftReportsInRadioButton.isChecked():
            drawReport(self, 'income', Qt.darkGreen, dateFrom, dateTo, timeList, exList, inList, titleFont, axisFont, self.currency)

        elif self.bottomLeftReportsBothRadioButton.isChecked():
            if dateFrom == dateTo:
                self.range = 0
                if self.bottomLeftReportsAcCheck.isChecked():
                    selectExQuery = QSqlQuery(f"SELECT SUM(value) FROM expenses WHERE transactionDate = '{dateFrom}' AND userID = {self.userID}")
                    selectInQuery = QSqlQuery(f"SELECT SUM(value) FROM income WHERE transactionDate = '{dateFrom}' AND userID = {self.userID}")
                else:
                    account = self.bottomLeftReportsAccountEntry.currentText()
                    if not account:
                        reportMsg.setText("Account is not selected!")
                        reportMsg.exec()
                        return
                    selectAccountIDQuery = QSqlQuery()
                    if not selectAccountIDQuery.exec(f"SELECT accountID FROM accounts WHERE name = '{account}' AND userID = {self.userID}"):
                        print(selectAccountIDQuery.lastError().databaseText())
                        return -1
                    if selectAccountIDQuery.next():
                        accountID = selectAccountIDQuery.value(0)
                    else:
                        return -1
                    selectExQuery = QSqlQuery(f"SELECT SUM(value) FROM expenses WHERE accountID = {accountID} AND transactionDate = '{dateFrom}' AND userID = {self.userID}")
                    selectInQuery = QSqlQuery(f"SELECT SUM(value) FROM income WHERE accountID = {accountID} AND transactionDate = '{dateFrom}' AND userID = {self.userID}")
                while selectExQuery.next():
                    exList.append(Decimal(selectExQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
                while selectInQuery.next():
                    inList.append(Decimal(selectInQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
                day_str = str(dateFrom)
                timeList.append(day_str[5:])
            else:
                if self.bottomLeftReportsDaysRadioButton.isChecked():
                    self.range = 5
                    delta = dateTo - dateFrom
                    for i in range(delta.days + 1):
                        day = dateFrom + timedelta(days=i)
                        if self.bottomLeftReportsAcCheck.isChecked():
                            selectExQuery = QSqlQuery(f"SELECT SUM(value) FROM expenses WHERE transactionDate = '{day}' AND userID = {self.userID}")
                            selectInQuery = QSqlQuery(f"SELECT SUM(value) FROM income WHERE transactionDate = '{day}' AND userID = {self.userID}")
                        else:
                            account = self.bottomLeftReportsAccountEntry.currentText()
                            if not account:
                                reportMsg.setText("Account is not selected!")
                                reportMsg.exec()
                                return
                            selectAccountIDQuery = QSqlQuery()
                            if not selectAccountIDQuery.exec(f"SELECT accountID FROM accounts WHERE name = '{account}' AND userID = {self.userID}"):
                                print(selectAccountIDQuery.lastError().databaseText())
                                return -1
                            if selectAccountIDQuery.next():
                                accountID = selectAccountIDQuery.value(0)
                            else:
                                return -1
                            selectExQuery = QSqlQuery(f"SELECT SUM(value) FROM expenses WHERE accountID = {accountID} AND transactionDate = '{day}' AND userID = {self.userID}")
                            selectInQuery = QSqlQuery(f"SELECT SUM(value) FROM income WHERE accountID = {accountID} AND transactionDate = '{day}' AND userID = {self.userID}")
                        while selectExQuery.next():
                            exList.append(Decimal(selectExQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
                        while selectInQuery.next():
                            inList.append(Decimal(selectInQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
                        day_str = str(day)
                        timeList.append(day_str[5:])
                else:
                    self.range = 4
                    delta = (dateTo.year - dateFrom.year) * 12 + (dateTo.month - dateFrom.month)
                    tempDate = dateFrom.replace(day=1)
                    for i in range(delta + 1):
                        if self.bottomLeftReportsAcCheck.isChecked():
                            selectExQuery = QSqlQuery(f"SELECT SUM(value) FROM expenses "
                                                      f"WHERE transactionDate >= '{tempDate}' AND transactionDate < DATEADD(month, 1, '{tempDate}') AND userID = {self.userID}")
                            selectInQuery = QSqlQuery(f"SELECT SUM(value) FROM income "
                                                      f"WHERE transactionDate >= '{tempDate}' AND transactionDate < DATEADD(month, 1, '{tempDate}') AND userID = {self.userID}")
                        else:
                            account = self.bottomLeftReportsAccountEntry.currentText()
                            if not account:
                                reportMsg.setText("Account is not selected!")
                                reportMsg.exec()
                                return
                            selectAccountIDQuery = QSqlQuery()
                            if not selectAccountIDQuery.exec(f"SELECT accountID FROM accounts WHERE name = '{account}' AND userID = {self.userID}"):
                                print(selectAccountIDQuery.lastError().databaseText())
                                return -1
                            if selectAccountIDQuery.next():
                                accountID = selectAccountIDQuery.value(0)
                            else:
                                return -1
                            selectExQuery = QSqlQuery(f"SELECT SUM(value) FROM expenses "
                                                      f"WHERE accountID = {accountID} AND transactionDate >= '{tempDate}' AND transactionDate < DATEADD(month, 1, '{tempDate}') AND userID = {self.userID}")
                            selectInQuery = QSqlQuery(f"SELECT SUM(value) FROM income "
                                                      f"WHERE accountID = {accountID} AND transactionDate >= '{tempDate}' AND transactionDate < DATEADD(month, 1, '{tempDate}') AND userID = {self.userID}")
                        while selectExQuery.next():
                            exList.append(Decimal(selectExQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
                        while selectInQuery.next():
                            inList.append(Decimal(selectInQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
                        month_str = str(tempDate)
                        timeList.append(month_str[:7])
                        tempDate = tempDate + relativedelta(months=1)

            set0 = QBarSet('Income')
            set0.setColor(Qt.darkGreen)
            set0.setLabelColor(Qt.black)
            set1 = QBarSet('Expenses')
            set1.setColor(Qt.red)
            set1.setLabelColor(Qt.black)
            
            set0.append(inList)
            set1.append(exList)

            self.series = QBarSeries()
            self.series.setBarWidth(0.7)
            self.series.append(set0)
            self.series.append(set1)

            self.chart.addSeries(self.series)
            self.chart.setTitleFont(titleFont)
            if self.bottomLeftReportsDaysRadioButton.isChecked():
                self.chart.setTitle('Income and expenses from ' + str(dateFrom) + ' to ' + str(dateTo))
            else:
                dF = str(dateFrom)
                dT = str(dateTo)
                self.chart.setTitle('Income ans expenses from ' + str(dF[:7]) + ' to ' + str(dT[:7]))
            self.chart.legend().setVisible(False)

            self.asd = timeList

            axisX = QBarCategoryAxis()
            axisX.append(timeList)
            axisX.setTitleText('Date')
            axisX.setLabelsFont(axisFont)
            self.chart.addAxis(axisX, Qt.AlignBottom)
            self.series.attachAxis(axisX)

            axisY = QValueAxis()
            axisY.setTitleText('Value (' + self.currency + ')')
            axisY.setLabelFormat("%.2f")
            axisY.setLabelsFont(axisFont)
            self.chart.addAxis(axisY, Qt.AlignLeft)
            self.series.attachAxis(axisY)

            def barHovered(status, index, bars):
                """Metoda wyświetlająca wartość słupka po najechaniu na niego kursorem"""
                if status:
                    self.chart.setToolTip("{:.2f}".format(bars.at(index)) + " " + self.currency)
                else:
                    self.chart.setToolTip("")

            self.series.hovered.connect(barHovered)

            self.chartView = QChartView(self.chart)
            if self.theme:
                self.chart.setBackgroundBrush(QBrush(QColor(27, 29, 30, 255)))
                self.chart.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))
                axisX.setLabelsBrush(QBrush(QColor(228, 231, 235, 255)))
                axisX.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))
                axisY.setLabelsBrush(QBrush(QColor(228, 231, 235, 255)))
                axisY.setTitleBrush(QBrush(QColor(228, 231, 235, 255)))
                self.chartView.setBackgroundBrush(QBrush(QColor(27, 29, 30, 255)))
            else:
                self.chart.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
                self.chartView.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
            self.chartView.setRenderHint(QPainter.Antialiasing)
            self.rightReportsPanelVLayout.addWidget(self.chartView)

            if len(timeList) > self.range and self.range > 0:
                self.scrollbar = QScrollBar(Qt.Horizontal, valueChanged=self.onAxisSliderMoved, pageStep=self.range)
                self.scrollbar.setMinimum(0)
                self.scrollbar.setMaximum(len(timeList)-self.range)
                self.scrollbar.valueChanged.connect(self.onAxisSliderMoved)
                self.rightReportsPanelVLayout.addWidget(self.scrollbar)
                self.onAxisSliderMoved(self.scrollbar.value())
                self.isScrollShown = True

            self.isChartShown = True
        else:
            reportMsg.setText("Type is not selected!")
            reportMsg.exec()
            return

    def adjust_axes(self, valueMin, valueMax):
        """Metoda ustawiająca zakres osi x przy przesuwaniu wykresu"""
        self.chart.axisX(self.series).setRange(valueMin, valueMax)

    def onAxisSliderMoved(self, value):
        """Metoda obliczjąca zakres osi x przy przesuwaniu wykresu"""
        l1 = self.asd[0 + value]
        l2 = self.asd[(self.range - 1) + value]
        self.adjust_axes(l1, l2)
