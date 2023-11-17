from datetime import date, datetime, timedelta
from calendar import monthrange
from functools import partial
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, InvalidOperation
from forex_python.converter import CurrencyRates
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtSql import QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QPushButton, QMessageBox, QFileDialog
from pandas import DataFrame


class BudgetFunctions:

    def addBudget(self):
        addBudgetMsg = QMessageBox()
        addBudgetMsg.setWindowTitle("Warning")
        addBudgetMsg.setIcon(QMessageBox.Warning)
        characters = "!\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"

        name = self.topLeftBudgetsNameEntry.text()
        if len(name) < 3:
            addBudgetMsg.setText("Name must be at least 3 characters long!")
            addBudgetMsg.exec()
            return
        elif any(char in characters for char in name):
            addBudgetMsg.setText("Name can only contain letters, digits and underscores!")
            addBudgetMsg.exec()
            return

        addBudgetQuery = QSqlQuery()
        addBudgetQuery.prepare("SELECT name FROM budgets WHERE name = :name AND userID = :userID")
        addBudgetQuery.bindValue(":name", name)
        addBudgetQuery.bindValue(":userID", self.userID)
        addBudgetQuery.exec()
        if addBudgetQuery.next():
            addBudgetMsg.setText("A budget with that name already exists!")
            addBudgetMsg.exec()
            addBudgetQuery.finish()
            return
        try:
            amount = Decimal(self.topLeftBudgetsAmountEntry.text()).quantize(self.fractional, ROUND_HALF_UP)
            if amount <= 0:
                raise InvalidOperation
        except InvalidOperation:
            addBudgetMsg.setText("Amount must be a number!")
            addBudgetMsg.exec()
            addBudgetQuery.finish()
            return
        category = self.topLeftBudgetsCategoryEntry.currentText()
        if not category == "All":
            if not addBudgetQuery.exec(
                    f"SELECT categoryID FROM categories WHERE name = '{category}' AND categoryType = 'expenses' AND userID = {self.userID}"):
                print(addBudgetQuery.lastError().databaseText())
                return -1
            if addBudgetQuery.next():
                categoryID = addBudgetQuery.value(0)
            else:
                return -1
        else:
            categoryID = 0
        budgetType = self.topLeftBudgetsTypeEntry.currentText()
        if budgetType == "One-time":
            frequency = "n/a"
            jobName = "n/a"
            startDate = self.topLeftBudgetsStartDateEntry.date().toPyDate()
            endDate = self.topLeftBudgetsEndDateEntry.date().toPyDate()
        elif budgetType == "Periodic":
            frequency = self.topLeftBudgetsFrequencyEntry.currentText()
            jobName = "budgets_" + self.login + "_" + name
            if frequency == "Monthly":
                currentYear = datetime.today().year
                currentMonth = datetime.today().month
                daysOfCurrentMonth = monthrange(currentYear, currentMonth)
                firstDay = date(currentYear, currentMonth, 1)
                lastDay = date(currentYear, currentMonth, daysOfCurrentMonth[1])
                startDate = firstDay.strftime('%Y-%m-%d')
                jobStartDate = firstDay.strftime('%Y%m%d')
                endDate = lastDay.strftime('%Y-%m-%d')
                freqType = 16
                freqInterval = 1
                freqRecurrenceFactor = 1
                activeStartDate = jobStartDate
                stepStartDate = "CAST(DATEADD(mm, DATEDIFF(mm, 0, GETDATE()), 0) AS DATE)"
                stepEndDate = "CAST(DATEADD(dd, -1, DATEADD(mm, DATEDIFF(mm, 0, GETDATE()) + 1, 0)) AS DATE)"
            elif frequency == "Yearly":
                currentYear = datetime.today().year
                firstDay = date(currentYear, 1, 1)
                lastDay = date(currentYear, 12, 31)
                startDate = firstDay.strftime('%Y-%m-%d')
                jobStartDate = firstDay.strftime('%Y%m%d')
                endDate = lastDay.strftime('%Y-%m-%d')
                freqType = 16
                freqInterval = 1
                freqRecurrenceFactor = 12
                activeStartDate = jobStartDate
                stepStartDate = "CAST(DATEADD(yy, DATEDIFF(yy, 0, GETDATE()), 0) AS DATE)"
                stepEndDate = "CAST(DATEADD(yy, DATEDIFF(yy, 0, GETDATE()) + 1, -1) AS DATE)"
            elif frequency == "Weekly":
                currentDate = datetime.today()
                firstDay = currentDate - timedelta(days=currentDate.weekday())
                lastDay = firstDay + timedelta(days=6)
                startDate = firstDay.strftime('%Y-%m-%d')
                jobStartDate = firstDay.strftime('%Y%m%d')
                endDate = lastDay.strftime('%Y-%m-%d')
                freqType = 8
                freqInterval = 2
                freqRecurrenceFactor = 1
                activeStartDate = jobStartDate
                stepStartDate = "CAST(DATEADD(wk, datediff(wk, 0, GETDATE()), 0) AS DATE)"
                stepEndDate = "CAST(DATEADD(wk, DATEDIFF(wk, 6, GETDATE()), 6 + 7) AS DATE)"

        notes = self.topLeftBudgetsNotesEntry.toPlainText()
        if len(notes) > 100:
            addBudgetMsg.setText("Notes length cannot be greater than 100 characters.")
            addBudgetMsg.exec()
            return

        addBudgetQuery.prepare(
            f"INSERT INTO budgets (name, amount, categoryID, type, frequency, notes, jobName, userID) "
            f"VALUES (:name, {amount}, {categoryID}, '{budgetType}', '{frequency}', :notes, :jobName, {self.userID})")
        addBudgetQuery.bindValue(":name", name)
        addBudgetQuery.bindValue(":notes", notes)
        addBudgetQuery.bindValue(":jobName", jobName)
        if not addBudgetQuery.exec():
            print(addBudgetQuery.lastError().databaseText())
            return -1

        if not addBudgetQuery.exec(f"SELECT MAX(budgetID) FROM budgets WHERE userID = {self.userID}"):
            print(addBudgetQuery.lastError().databaseText())
            return -1
        if addBudgetQuery.next():
            budgetID = addBudgetQuery.value(0)
        else:
            return -1

        if not addBudgetQuery.exec(f"INSERT INTO budgetEntries (startDate, endDate, budgetID, userID) "
                                   f"VALUES ('{startDate}', '{endDate}', {budgetID}, {self.userID})"):
            print(addBudgetQuery.lastError().databaseText())
            return -1

        if budgetType == "Periodic":
            jobStepName = jobName + "_step"
            jobScheduleName = jobName + "_schedule"
            jobName = jobName.replace("'", "''")
            jobStepName = jobStepName.replace("'", "''")
            jobScheduleName = jobScheduleName.replace("'", "''")

            query = f"""USE msdb ;
    EXEC dbo.sp_add_job  
        @job_name = N'{jobName}' ;
    EXEC sp_add_jobstep  
        @job_name = N'{jobName}',  
        @step_name = N'{jobStepName}',  
        @subsystem = N'TSQL',  
        @command = N'INSERT INTO Baza.dbo.budgetEntries (startDate, endDate, budgetID, userID) VALUES ({stepStartDate}, {stepEndDate}, {budgetID}, {self.userID});',
        @on_success_action = 1,
        @retry_attempts = 0,  
        @retry_interval = 0 ;
    EXEC dbo.sp_add_schedule  
        @schedule_name = N'{jobScheduleName}',
        @enabled = 1,
        @freq_type = {freqType},
        @freq_interval = {freqInterval}, 
        @freq_relative_interval = 0, 
        @freq_recurrence_factor = {freqRecurrenceFactor},
        @active_start_date = {activeStartDate},
        @active_end_date = 99991231,
        @active_start_time = 0,
        @active_end_time = 235959 ;  
    EXEC sp_attach_schedule  
        @job_name = N'{jobName}',  
        @schedule_name = N'{jobScheduleName}';
    EXEC dbo.sp_add_jobserver  
        @job_name = N'{jobName}';
    USE Baza ;"""

            if not addBudgetQuery.exec(query):
                print(addBudgetQuery.lastError().databaseText())

        self.con.commit()
        self.fillBudgetsTable()
        self.fillBudgetsCharts()

    def editBudget(self):
        editBudgetMsg = QMessageBox()
        editBudgetMsg.setWindowTitle("Warning")
        editBudgetMsg.setIcon(QMessageBox.Warning)

        from editWindows import EditBudgetWindow
        self.editBudgetWindow = EditBudgetWindow(self, self.userID)

        if self.bottomLeftBudgetsPanelTable.currentIndex().isValid():
            indexes = self.bottomLeftBudgetsPanelTable.selectionModel().selectedRows()
            if not indexes:
                editBudgetMsg.setText("Budget is not selected!")
                editBudgetMsg.exec()
                return None
            tableModelBudgets = self.bottomLeftBudgetsPanelTable.model()
            self.editBudgetWindow.show()
            for index in sorted(indexes):
                row = index.row()
                name = tableModelBudgets.data(tableModelBudgets.index(row, 0))
                amount = Decimal(tableModelBudgets.data(tableModelBudgets.index(row, 1))).quantize(self.fractional,
                                                                                                   ROUND_HALF_UP)
                category = tableModelBudgets.data(tableModelBudgets.index(row, 2))
                if not category == 0:
                    selectCategoryQuery = QSqlQuery()
                    selectCategoryQuery.exec(f"SELECT name FROM categories WHERE categoryID = {category}")
                    if selectCategoryQuery.next():
                        categoryName = selectCategoryQuery.value(0)
                else:
                    categoryName = "All"
                budgetType = tableModelBudgets.data(tableModelBudgets.index(row, 3))
                frequency = tableModelBudgets.data(tableModelBudgets.index(row, 4))
                notes = tableModelBudgets.data(tableModelBudgets.index(row, 5))
                jobName = tableModelBudgets.data(tableModelBudgets.index(row, 6))
                budgetID = tableModelBudgets.data(tableModelBudgets.index(row, 7))
                if budgetType == "One-time":
                    selectDatesQuery = QSqlQuery()
                    selectDatesQuery.exec(f"SELECT startDate, endDate FROM budgetEntries WHERE budgetID = {budgetID}")
                    if selectDatesQuery.next():
                        startDate = selectDatesQuery.value(0)
                        endDate = selectDatesQuery.value(1)
                        year = int(startDate[:4])
                        month = int(startDate[5:7])
                        day = int(startDate[8:])
                        startDate = QDate(year, month, day)
                        year = int(endDate[:4])
                        month = int(endDate[5:7])
                        day = int(endDate[8:])
                        endDate = QDate(year, month, day)
                        self.editBudgetWindow.editBudgetStartDateEntry.setDate(startDate)
                        self.editBudgetWindow.editBudgetEndDateEntry.setDate(endDate)
                else:
                    self.editBudgetWindow.editBudgetStartDateEntry.setDate(date.today())
                    self.editBudgetWindow.editBudgetEndDateEntry.setDate(date.today())
                    self.editBudgetWindow.editBudgetStartDateEntry.setDisabled(True)
                    self.editBudgetWindow.editBudgetEndDateEntry.setDisabled(True)
                self.editBudgetWindow.editBudgetNameEntry.setText(name)
                self.editBudgetWindow.editBudgetAmountEntry.setText(str(amount))
                self.editBudgetWindow.editBudgetSymbolLabel.setText(self.currency)
                self.editBudgetWindow.editBudgetCategoryEntry.setCurrentText(categoryName)
                self.editBudgetWindow.editBudgetNotesEntry.setPlainText(notes)

                self.editBudgetWindow.editBudgetEditButton.clicked.connect(partial(self.editBg, budgetID, name, jobName, budgetType))

            tableModelBudgets.select()
        else:
            editBudgetMsg.setText("Budget is not selected!")
            editBudgetMsg.exec()
            return None

    def editBg(self, budgetID, oldName, jobName, budgetType):
        editBudgetMsg = QMessageBox()
        editBudgetMsg.setWindowTitle("Warning")
        editBudgetMsg.setIcon(QMessageBox.Warning)
        characters = "!\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"

        updateBudgetQuery = QSqlQuery()

        newName = self.editBudgetWindow.editBudgetNameEntry.text()
        if not newName == oldName:
            if len(newName) < 3:
                editBudgetMsg.setText("Name must be at least 3 characters long.")
                editBudgetMsg.exec()
                return
            elif any(char in characters for char in newName):
                editBudgetMsg.setText("Name can only contain letters, digits and underscores!")
                editBudgetMsg.exec()
                return

            updateBudgetQuery.prepare("SELECT name FROM budgets WHERE name = :newName AND userID = :userID")
            updateBudgetQuery.bindValue(":newName", newName)
            updateBudgetQuery.bindValue(":userID", self.userID)
            if updateBudgetQuery.exec():
                if updateBudgetQuery.next():
                    editBudgetMsg.setText("Account with that name already exists!")
                    editBudgetMsg.exec()
                    updateBudgetQuery.finish()
                    return
        try:
            newAmount = Decimal(self.editBudgetWindow.editBudgetAmountEntry.text()).quantize(self.fractional, ROUND_HALF_UP)
            if newAmount <= 0:
                raise InvalidOperation
        except InvalidOperation:
            editBudgetMsg.setText("Amount must be a number!")
            editBudgetMsg.exec()
            updateBudgetQuery.finish()
            return
        newCategory = self.editBudgetWindow.editBudgetCategoryEntry.currentText()
        if not newCategory == "All":
            if not updateBudgetQuery.exec(
                    f"SELECT categoryID FROM categories WHERE name = '{newCategory}' AND categoryType = 'expenses' AND userID = {self.userID}"):
                print(updateBudgetQuery.lastError().databaseText())
                return
            if updateBudgetQuery.next():
                newCategoryID = updateBudgetQuery.value(0)
            else:
                return
        else:
            newCategoryID = 0
        if budgetType == "One-time":
            newStartDate = self.editBudgetWindow.editBudgetStartDateEntry.date().toPyDate()
            newEndDate = self.editBudgetWindow.editBudgetEndDateEntry.date().toPyDate()
        notes = self.editBudgetWindow.editBudgetNotesEntry.toPlainText()
        if len(notes) > 100:
            editBudgetMsg.setText("Notes length cannot be greater than 100 characters.")
            editBudgetMsg.exec()
            return

        updateBudgetQuery.prepare(
            f"UPDATE budgets SET name = :newName, amount = {newAmount}, categoryID = {newCategoryID}, notes = :notes "
            f"WHERE budgetID = {budgetID} AND userID = {self.userID}")
        updateBudgetQuery.bindValue(":newName", newName)
        updateBudgetQuery.bindValue(":notes", notes)
        if not updateBudgetQuery.exec():
            print(updateBudgetQuery.lastError().databaseText())
        if budgetType == "One-time":
            if not updateBudgetQuery.exec(f"UPDATE budgetEntries SET startDate = '{newStartDate}', endDate = '{newEndDate}' WHERE budgetID = {budgetID}"):
                print(updateBudgetQuery.lastError().databaseText())

        updateBudgetQuery.finish()
        self.con.commit()
        self.fillBudgetsTable()
        self.fillBudgetsCharts()
        self.editBudgetWindow.close()

    def deleteBudget(self):
        deleteBudgetMsg = QMessageBox()
        deleteBudgetMsg.setWindowTitle("Warning")
        deleteBudgetMsg.setIcon(QMessageBox.Warning)

        if self.bottomLeftBudgetsPanelTable.currentIndex().isValid():
            indexes = self.bottomLeftBudgetsPanelTable.selectionModel().selectedRows()
            if not indexes:
                deleteBudgetMsg.setText("Budget is not selected!")
                deleteBudgetMsg.exec()
                return None
            else:
                deleteBudgetMsg.setWindowTitle("Confirm")
                deleteBudgetMsg.setIcon(QMessageBox.Question)
                deleteBudgetMsg.setText("The budget will be deleted. \nDo you want to continue?")
                yesButton = QPushButton("Yes")
                noButton = QPushButton("No")
                deleteBudgetMsg.addButton(yesButton, QMessageBox.YesRole)
                deleteBudgetMsg.addButton(noButton, QMessageBox.NoRole)
                deleteBudgetMsg.exec()
                if deleteBudgetMsg.clickedButton() == yesButton:
                    deleteBudgetQuery = QSqlQuery()
                    tableModelBudgets = self.bottomLeftBudgetsPanelTable.model()
                    rows = []
                    for index in sorted(indexes):
                        rows.append(index.row())
                    rows.reverse()
                    for row in rows:
                        budgetID = tableModelBudgets.data(tableModelBudgets.index(row, 7))
                        deleteBudgetQuery.prepare(f"SELECT type, jobName FROM budgets WHERE budgetID = :budgetID")
                        deleteBudgetQuery.bindValue(":budgetID", budgetID)
                        if deleteBudgetQuery.exec():
                            if deleteBudgetQuery.next():
                                budgetType = deleteBudgetQuery.value(0)
                                jobName = deleteBudgetQuery.value(1)
                            else:
                                return -1
                        else:
                            return -1
                        if budgetType == "Periodic":
                            jobName = jobName.replace("'", "''")
                            deleteBudgetQuery.exec(f"USE msdb ; "
                                                   f"EXEC dbo.sp_delete_job @job_name = N'{jobName}', @delete_unused_schedule = 1 ; "
                                                   f"USE Baza ;")

                        deleteBudgetQuery.prepare(f"DELETE FROM budgetEntries WHERE budgetID = :budgetID")
                        deleteBudgetQuery.bindValue(":budgetID", budgetID)
                        if deleteBudgetQuery.exec():
                            tableModelBudgets.removeRow(row)

                    tableModelBudgets.select()
                    self.fillBudgetsTable()
                    self.fillBudgetsCharts()
        else:
            deleteBudgetMsg.setText("Budget is not selected!")
            deleteBudgetMsg.exec()
            return None
