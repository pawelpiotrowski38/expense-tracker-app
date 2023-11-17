from datetime import date, datetime, timedelta
from calendar import monthrange
from functools import partial
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, InvalidOperation
from forex_python.converter import CurrencyRates
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtSql import QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QPushButton, QMessageBox, QFileDialog
from pandas import DataFrame


class AccountFunctions:

    def addAccount(self):
        addAccMsg = QMessageBox()
        addAccMsg.setWindowTitle("Warning")
        addAccMsg.setIcon(QMessageBox.Warning)
        if self.thread.isRunning():
            addAccMsg.setText("The total amount owned is being calculated!")
            addAccMsg.exec()
            return
        characters = "!\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"

        name = self.topLeftAccountsNameEntry.text()
        if len(name) < 3:
            addAccMsg.setText("Name must be at least 3 characters long!")
            addAccMsg.exec()
            return
        elif any(char in characters for char in name):
            addAccMsg.setText("Name can only contain letters, digits and underscores!")
            addAccMsg.exec()
            return

        addAccountQuery = QSqlQuery()
        addAccountQuery.prepare("SELECT name FROM accounts WHERE name = :name AND userID = :userID")
        addAccountQuery.bindValue(":name", name)
        addAccountQuery.bindValue(":userID", self.userID)
        addAccountQuery.exec()
        if addAccountQuery.next():
            addAccMsg.setText("An account with that name already exists!")
            addAccMsg.exec()
            addAccountQuery.finish()
            return
        try:
            cAmount = Decimal(self.topLeftAccountsAmountEntry.text()).quantize(self.fractional, ROUND_HALF_UP)
            iAmount = Decimal(self.topLeftAccountsAmountEntry.text()).quantize(self.fractional, ROUND_HALF_UP)
        except InvalidOperation:
            addAccMsg.setText("Amount must be a number!")
            addAccMsg.exec()
            addAccountQuery.finish()
            return
        currency = self.topLeftAccountsCurrencyEntry.currentText()[:3]
        notes = self.topLeftAccountsNotesEntry.toPlainText()
        if len(notes) > 100:
            addAccMsg.setText("Notes length cannot be greater than 100 characters.")
            addAccMsg.exec()
            return
        synch = 0

        addAccountQuery.prepare("SELECT COUNT(:name) FROM accounts WHERE userID = :userID")
        addAccountQuery.bindValue(":name", name)
        addAccountQuery.bindValue(":userID", self.userID)
        addAccountQuery.exec()
        if addAccountQuery.next():
            position = addAccountQuery.value(0) + 1
        else:
            return

        addAccountQuery.prepare(
            f"INSERT INTO accounts (name, currency, currAmount, initAmount, notes, position, synch, userID) "
            f"VALUES (:name, '{currency}', {cAmount}, {iAmount}, :notes, {position}, {synch}, {self.userID})")
        addAccountQuery.bindValue(":name", name)
        addAccountQuery.bindValue(":notes", notes)
        if not addAccountQuery.exec():
            print('blad')
        addAccountQuery.finish()

        self.fillAccountsTable()
        self.fillAmountOwned()
        self.fillAccountsComboBox()
        self.fillSummaryPanel(self.theme)

    def deleteAccount(self):
        deleteAccMsg = QMessageBox()
        deleteAccMsg.setWindowTitle("Warning")
        deleteAccMsg.setIcon(QMessageBox.Warning)

        if self.rightAccountsPanelTable.currentIndex().isValid():
            indexes = self.rightAccountsPanelTable.selectionModel().selectedRows()
            if not indexes:
                deleteAccMsg.setText("Account is not selected!")
                deleteAccMsg.exec()
                return None
            else:
                deleteAccMsg.setWindowTitle("Confirm")
                deleteAccMsg.setIcon(QMessageBox.Question)
                deleteAccMsg.setText(
                    "The account and all related transactions will be deleted. \nDo you want to continue?")
                yesButton = QPushButton("Yes")
                noButton = QPushButton("No")
                deleteAccMsg.addButton(yesButton, QMessageBox.YesRole)
                deleteAccMsg.addButton(noButton, QMessageBox.NoRole)
                deleteAccMsg.exec()
                if deleteAccMsg.clickedButton() == yesButton:
                    if self.thread.isRunning():
                        threadRunningMsg = QMessageBox()
                        threadRunningMsg.setWindowTitle("Warning")
                        threadRunningMsg.setIcon(QMessageBox.Warning)
                        threadRunningMsg.setText("The total amount owned is being calculated!")
                        threadRunningMsg.exec()
                        return
                    tableModelAccounts = self.rightAccountsPanelTable.model()
                    rows = []
                    for index in sorted(indexes):
                        rows.append(index.row())
                    rows.reverse()
                    deleteAccountQuery = QSqlQuery()
                    deleteJobQuery = QSqlQuery()
                    for row in rows:
                        name = tableModelAccounts.data(tableModelAccounts.index(row, 0))
                        position = tableModelAccounts.data(tableModelAccounts.index(row, 5))
                        if not deleteAccountQuery.exec(
                                f"SELECT accountID FROM accounts WHERE name = '{name}' AND userID = {self.userID}"):
                            print(deleteAccountQuery.lastError().databaseText())
                            return -1
                        if deleteAccountQuery.next():
                            accountID = deleteAccountQuery.value(0)
                        else:
                            return -1
                        deleteAccountQuery.exec(
                            f"UPDATE accounts SET position = position - 1 WHERE userID = {self.userID} AND position > {position}")
                        deleteAccountQuery.prepare(
                            "DELETE FROM expenses WHERE accountID = :accountID AND userID = :userID")
                        deleteAccountQuery.bindValue(":accountID", accountID)
                        deleteAccountQuery.bindValue(":userID", self.userID)
                        deleteAccountQuery.exec()
                        deleteAccountQuery.prepare(
                            "DELETE FROM income WHERE accountID = :accountID AND userID = :userID")
                        deleteAccountQuery.bindValue(":accountID", accountID)
                        deleteAccountQuery.bindValue(":userID", self.userID)
                        deleteAccountQuery.exec()
                        deleteAccountQuery.prepare(
                            "DELETE FROM transfers WHERE (accountFromID = :accountFromID OR accountToID = :accountToID) AND userID = :userID")
                        deleteAccountQuery.bindValue(":accountFromID", accountID)
                        deleteAccountQuery.bindValue(":accountToID", accountID)
                        deleteAccountQuery.bindValue(":userID", self.userID)
                        if not deleteAccountQuery.exec():
                            print(deleteAccountQuery.lastError().databaseText())

                        deleteAccountQuery.prepare(
                            "SELECT name FROM jobs WHERE accountID = :accountID AND userID = :userID")
                        deleteAccountQuery.bindValue(":accountID", accountID)
                        deleteAccountQuery.bindValue(":userID", self.userID)
                        deleteAccountQuery.exec()
                        while deleteAccountQuery.next():
                            jobName = deleteAccountQuery.value(0)
                            deleteJobQuery.prepare("DELETE FROM jobs WHERE name = :jobName AND userID = :userID")
                            deleteJobQuery.bindValue(":jobName", jobName)
                            deleteJobQuery.bindValue(":userID", self.userID)
                            deleteJobQuery.exec()

                            jobName = jobName.replace("'", "''")
                            statusJobName = jobName + '_status'
                            deleteJobQuery.exec(f"USE msdb ; "
                                                f"EXEC dbo.sp_delete_job @job_name = N'{jobName}', @delete_unused_schedule = 1 ; "
                                                f"EXEC dbo.sp_delete_job @job_name = N'{statusJobName}', @delete_unused_schedule = 1 ; "
                                                f"USE Baza ;")
                        tableModelAccounts.removeRow(row)

                    deleteJobQuery.finish()
                    deleteAccountQuery.finish()
                    tableModelAccounts.select()
                    self.fillAccountsComboBox()
                    self.fillTransactionTable()
                    self.fillTransfersTable()
                    self.fillAmountOwned()
                    self.fillSummaryPanel(self.theme)
                    self.fillDailyCharts(self.theme)
                    self.fillJobsTable()
        else:
            deleteAccMsg.setText("Account is not selected!")
            deleteAccMsg.exec()
            return None

    def editAccount(self):
        editAccMsg = QMessageBox()
        editAccMsg.setWindowTitle("Warning")
        editAccMsg.setIcon(QMessageBox.Warning)

        from editWindows import EditAccountWindow
        self.editAccountWindow = EditAccountWindow(self, self.userID)

        if self.rightAccountsPanelTable.currentIndex().isValid():
            indexes = self.rightAccountsPanelTable.selectionModel().selectedRows()
            if not indexes:
                editAccMsg.setText("Account is not selected!")
                editAccMsg.exec()
                return None
            self.editAccountWindow.show()
            tableModelAccounts = self.rightAccountsPanelTable.model()
            for index in sorted(indexes):
                row = index.row()
                name = tableModelAccounts.data(tableModelAccounts.index(row, 0))
                currency = tableModelAccounts.data(tableModelAccounts.index(row, 1))
                currencyName = currency + ' - ' + self.codes.get_currency_name(currency)
                currAmount = Decimal(tableModelAccounts.data(tableModelAccounts.index(row, 2))).quantize(
                    self.fractional,
                    ROUND_HALF_UP)
                initAmount = Decimal(tableModelAccounts.data(tableModelAccounts.index(row, 3))).quantize(
                    self.fractional,
                    ROUND_HALF_UP)
                position = tableModelAccounts.data(tableModelAccounts.index(row, 5))
                notes = tableModelAccounts.data(tableModelAccounts.index(row, 4))
                synch = tableModelAccounts.data(tableModelAccounts.index(row, 6))
                self.editAccountWindow.editAccountNameEntry.setText(name)
                self.editAccountWindow.editAccountCurrencyEntry.setCurrentText(currencyName)
                self.editAccountWindow.editAccountAmountEntry.setText(str(initAmount))
                self.editAccountWindow.editAccountPositionEntry.setValue(int(position))
                self.editAccountWindow.editAccountNotesEntry.setPlainText(notes)

                self.editAccountWindow.editAccountEditButton.clicked.connect(
                    partial(self.editAc, name, currency, initAmount, currAmount, position))

            tableModelAccounts.select()
        else:
            editAccMsg.setText("Account is not selected!")
            editAccMsg.exec()
            return None

    def editAc(self, name, currency, initAmount, currAmount, position):
        editAccMsg = QMessageBox()
        editAccMsg.setWindowTitle("Warning")
        editAccMsg.setIcon(QMessageBox.Warning)
        if self.thread.isRunning():
            editAccMsg.setText("The total amount owned is being calculated!")
            editAccMsg.exec()
            return
        characters = "!\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"

        updateAccountQuery = QSqlQuery()
        rates = CurrencyRates()

        newName = self.editAccountWindow.editAccountNameEntry.text()
        if newName != name:
            updateAccountQuery.prepare("SELECT name FROM accounts WHERE name = :newName AND userID = :userID")
            updateAccountQuery.bindValue(":newName", newName)
            updateAccountQuery.bindValue(":userID", self.userID)
            updateAccountQuery.exec()
            if updateAccountQuery.next():
                editAccMsg.setText("Account with that name already exists!")
                editAccMsg.exec()
                updateAccountQuery.finish()
                return
            elif len(newName) < 3:
                editAccMsg.setText("Name has to be at least 3 characters long.")
                editAccMsg.exec()
                return
            elif any(char in characters for char in newName):
                editAccMsg.setText("Name can contain only letters, digits and underscores!")
                editAccMsg.exec()
                return

        newCurrency = self.editAccountWindow.editAccountCurrencyEntry.currentText()[:3]
        try:
            newInitAmount = Decimal(self.editAccountWindow.editAccountAmountEntry.text()).quantize(self.fractional,
                                                                                                   ROUND_HALF_UP)
        except InvalidOperation:
            editAccMsg.setText("Amount must be a number.")
            editAccMsg.exec()
            updateAccountQuery.finish()
            return
        notes = self.editAccountWindow.editAccountNotesEntry.toPlainText()
        if len(notes) > 100:
            editAccMsg.setText("Notes length cannot be greater than 100 characters.")
            editAccMsg.exec()
            return

        newPosition = self.editAccountWindow.editAccountPositionEntry.value()
        synch = 0
        difference = initAmount - newInitAmount
        newCurrAmount = currAmount - difference

        if not updateAccountQuery.exec(
                f"SELECT accountID FROM accounts WHERE name = '{name}' AND userID = {self.userID}"):
            print(updateAccountQuery.lastError().databaseText())
            return -1
        if updateAccountQuery.next():
            accountID = updateAccountQuery.value(0)
        else:
            return -1

        if newPosition < position:
            updateAccountQuery.exec(
                f"UPDATE accounts SET position = position+1 WHERE userID = {self.userID} AND position >= {newPosition} AND position < {position};")
        if newPosition > position:
            updateAccountQuery.exec(
                f"UPDATE accounts SET position = position-1 WHERE userID = {self.userID} AND position > {position} AND position <= {newPosition};")
        updateAccountQuery.prepare(
            f"UPDATE accounts SET name = :newName, currency = '{newCurrency}', currAmount = {newCurrAmount}, initAmount = {newInitAmount}, notes = :notes, position = {newPosition}, synch = {synch} "
            f"WHERE accountID = :accountID AND userID = {self.userID};")
        updateAccountQuery.bindValue(":newName", newName)
        updateAccountQuery.bindValue(":notes", notes)
        updateAccountQuery.bindValue(":accountID", accountID)
        updateAccountQuery.exec()

        if newCurrency != currency:
            exList = {}
            inList = {}
            jobList = {}

            updateAccountQuery.prepare(
                "SELECT transactionID, originValue FROM expenses WHERE accountID = :accountID AND userID = :userID")
            updateAccountQuery.bindValue(":accountID", accountID)
            updateAccountQuery.bindValue(":userID", self.userID)
            updateAccountQuery.exec()
            while updateAccountQuery.next():
                exList[updateAccountQuery.value(0)] = Decimal(updateAccountQuery.value(1)).quantize(self.fractional,
                                                                                                    ROUND_HALF_UP)

            updateAccountQuery.prepare(
                "SELECT transactionID, originValue FROM income WHERE accountID = :accountID AND userID = :userID")
            updateAccountQuery.bindValue(":accountID", accountID)
            updateAccountQuery.bindValue(":userID", self.userID)
            updateAccountQuery.exec()
            while updateAccountQuery.next():
                inList[updateAccountQuery.value(0)] = Decimal(updateAccountQuery.value(1)).quantize(self.fractional,
                                                                                                    ROUND_HALF_UP)

            updateAccountQuery.prepare(
                "SELECT jobID, originValue FROM jobs WHERE accountID = :accountID AND userID = :userID")
            updateAccountQuery.bindValue(":accountID", accountID)
            updateAccountQuery.bindValue(":userID", self.userID)
            updateAccountQuery.exec()
            while updateAccountQuery.next():
                jobList[updateAccountQuery.value(0)] = Decimal(updateAccountQuery.value(1)).quantize(self.fractional,
                                                                                                     ROUND_HALF_UP)

            if newCurrency != self.currencyCode:
                rate = Decimal(rates.get_rate(newCurrency, self.currencyCode))

            for key, value in exList.items():
                originValue = value
                if newCurrency != self.currencyCode:
                    convertedValue = (originValue * rate).quantize(self.fractional, ROUND_HALF_UP)
                else:
                    convertedValue = originValue
                amount = str(originValue) + ' ' + self.editAccountWindow.editAccountSymbolLabel.text()
                updateAccountQuery.prepare(
                    f"UPDATE expenses SET amount = :amount, value = {convertedValue}, currency = '{newCurrency}' WHERE transactionID = {key};")
                updateAccountQuery.bindValue(":amount", amount)
                updateAccountQuery.exec()
            for key, value in inList.items():
                originValue = value
                if newCurrency != self.currencyCode:
                    convertedValue = (originValue * rate).quantize(self.fractional, ROUND_HALF_UP)
                else:
                    convertedValue = originValue
                amount = str(originValue) + ' ' + self.editAccountWindow.editAccountSymbolLabel.text()
                updateAccountQuery.prepare(
                    f"UPDATE income SET amount = :amount, value = {convertedValue}, currency = '{newCurrency}' WHERE transactionID = {key};")
                updateAccountQuery.bindValue(":amount", amount)
                updateAccountQuery.exec()
            for key, value in jobList.items():
                updateAccountQuery.exec(f"SELECT name, type_t, categoryID FROM jobs WHERE jobID = {key};")
                if updateAccountQuery.next():
                    name = updateAccountQuery.value(0)
                    name = name.replace("'", "''")
                    type_t = updateAccountQuery.value(1)
                    categoryID = updateAccountQuery.value(2)
                if type_t == 'Expense':
                    job_transaction_type = 'expenses'
                    updateAccountValue = value * (-1)
                elif type_t == 'Income':
                    job_transaction_type = 'income'
                    updateAccountValue = value
                step_name1 = name + '_step1'
                step_name2 = name + '_step2'
                originValue = value
                if newCurrency != self.currencyCode:
                    convertedValue = (originValue * rate).quantize(self.fractional, ROUND_HALF_UP)
                else:
                    convertedValue = originValue
                amount = str(originValue) + ' ' + self.editAccountWindow.editAccountSymbolLabel.text()
                updateAccountQuery.prepare(f"UPDATE jobs SET value = :amount WHERE jobID = {key};")
                updateAccountQuery.bindValue(":amount", amount)
                updateAccountQuery.exec()

                updateJobQuery = QSqlQuery()
                query = f"""USE msdb ;
    EXEC sp_update_jobstep
        @step_id = 1,
        @job_name = N'{name}',  
        @step_name = N'{step_name1}',  
        @subsystem = N'TSQL',  
        @command = N'INSERT INTO Baza.dbo.{job_transaction_type} (amount,categoryID,accountID,date_t,notes,value,originValue,userID,currency) VALUES ("{amount}", "{categoryID}", {accountID}, CONVERT(date,getdate()), "{notes}", {convertedValue}, {value}, "{self.userID}", "{newCurrency}");';
    USE Baza ;"""
                if not updateJobQuery.exec(query):
                    print(updateJobQuery.lastError().databaseText())

                updateJobQuery.finish()

        self.fillSummaryPanel(self.theme)
        self.fillDailyCharts(self.theme)

        updateAccountQuery.finish()
        self.fillAccountsComboBox()
        self.fillAccountsTable()
        self.fillTransactionTable()
        self.fillJobsTable()
        self.fillAmountOwned()
        self.fillSummaryPanel(self.theme)
        self.editAccountWindow.close()
