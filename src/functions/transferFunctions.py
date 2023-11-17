from datetime import date, datetime, timedelta
from calendar import monthrange
from functools import partial
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, InvalidOperation
from forex_python.converter import CurrencyRates
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtSql import QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QPushButton, QMessageBox, QFileDialog
from pandas import DataFrame


class TransferFunctions:

    def addTransfer(self):
        transferMsg = QMessageBox()
        transferMsg.setWindowTitle("Warning")
        transferMsg.setIcon(QMessageBox.Warning)
        if self.thread.isRunning():
            transferMsg.setText("The total amount owned is being calculated!")
            transferMsg.exec()
            return

        fromAccount = self.bottomLeftAccountsFromEntry.currentText()
        toAccount = self.bottomLeftAccountsToEntry.currentText()
        if not fromAccount or not toAccount:
            transferMsg.setText("Account is not selected!")
            transferMsg.exec()
            return
        if fromAccount == toAccount:
            transferMsg.setText("Accounts cannot be the same!")
            transferMsg.exec()
            return
        try:
            amount = Decimal(self.bottomLeftAccountsAmountEntry.text()).quantize(self.fractional, ROUND_HALF_EVEN)
            if amount <= 0:
                raise InvalidOperation
        except InvalidOperation:
            transferMsg.setText("Amount must be a number!")
            transferMsg.exec()
            return

        transferQuery = QSqlQuery()
        if not transferQuery.exec(
                f"SELECT accountID, currency FROM accounts WHERE name = '{fromAccount}' AND userID = {self.userID}"):
            print(transferQuery.lastError().databaseText())
            return -1
        if transferQuery.next():
            fromAccountID = transferQuery.value(0)
            fromCurrency = transferQuery.value(1)
        else:
            return -1
        if not transferQuery.exec(
                f"SELECT accountID,currency FROM accounts WHERE name = '{toAccount}' AND userID = {self.userID}"):
            print(transferQuery.lastError().databaseText())
            return -1
        if transferQuery.next():
            toAccountID = transferQuery.value(0)
            toCurrency = transferQuery.value(1)
        else:
            return -1

        transferDate = self.bottomLeftAccountsDateEntry.date().toPyDate()
        if self.bottomLeftAccountsRateEntry.isEnabled():
            if not self.bottomLeftAccountsRateCheckBox.isChecked():
                try:
                    rate = Decimal(self.bottomLeftAccountsRateEntry.text())
                except InvalidOperation:
                    transferMsg.setText("Rate must be a number!")
                    transferMsg.exec()
                    return
            else:
                rate = self.rates.get_rate(fromCurrency, toCurrency)
        else:
            rate = 0

        transferQuery.exec(f"SELECT currAmount FROM accounts WHERE name = '{fromAccount}' AND userID = '{self.userID}'")
        while transferQuery.next():
            fromAmount = Decimal(transferQuery.value(0))

        transferQuery.exec(f"SELECT currAmount FROM accounts WHERE name = '{toAccount}' AND userID = '{self.userID}'")
        while transferQuery.next():
            toAmount = Decimal(transferQuery.value(0))

        if fromCurrency == toCurrency:
            newFromAmount = fromAmount - amount
            newToAmount = toAmount + amount
            value = amount
        else:
            newFromAmount = fromAmount - amount
            if self.bottomLeftAccountsRateCheckBox.isChecked():
                convertedAmount = (self.rates.convert(fromCurrency, toCurrency, amount)).quantize(self.fractional,
                                                                                                  ROUND_HALF_UP)
            else:
                convertedAmount = amount * rate
            newToAmount = toAmount + convertedAmount
            value = convertedAmount

        strAmount = str(amount) + ' ' + self.codes.get_symbol(fromCurrency)

        transferQuery = QSqlQuery()
        transferQuery.exec(
            f"UPDATE accounts SET currAmount = '{newFromAmount}' WHERE name = '{fromAccount}' AND userID = '{self.userID}'")
        transferQuery.exec(
            f"UPDATE accounts SET currAmount = '{newToAmount}' WHERE name = '{toAccount}' AND userID = '{self.userID}'")
        if not transferQuery.exec(
                f"INSERT INTO transfers (amount, accountFromID, accountToID, transferDate, value, originValue, rate, userID) VALUES ('{strAmount}', {fromAccountID}, {toAccountID}, '{transferDate}', {value}, {amount}, {rate}, {self.userID})"):
            print(transferQuery.lastError().databaseText())
        transferQuery.finish()
        self.con.commit()

        self.fillAccountsTable()
        self.fillTransfersTable()

    def deleteTransfer(self):
        deleteTransferMsg = QMessageBox()
        deleteTransferMsg.setWindowTitle("Warning")
        deleteTransferMsg.setIcon(QMessageBox.Warning)
        if self.bottomRightAccountsPanelTable.currentIndex().isValid():
            indexes = self.bottomRightAccountsPanelTable.selectionModel().selectedRows()
            if not indexes:
                deleteTransferMsg.setText("Transfer is not selected!")
                deleteTransferMsg.exec()
                return None
            else:
                deleteTransferMsg.setWindowTitle("Confirm")
                deleteTransferMsg.setIcon(QMessageBox.Question)
                deleteTransferMsg.setText("The selected transfer will be deleted. \nDo you want to continue?")
                yesButton = QPushButton("Yes")
                noButton = QPushButton("No")
                deleteTransferMsg.addButton(yesButton, QMessageBox.YesRole)
                deleteTransferMsg.addButton(noButton, QMessageBox.NoRole)
                deleteTransferMsg.exec()
                if deleteTransferMsg.clickedButton() == yesButton:
                    if self.thread.isRunning():
                        threadRunningMsg = QMessageBox()
                        threadRunningMsg.setWindowTitle("Warning")
                        threadRunningMsg.setIcon(QMessageBox.Warning)
                        threadRunningMsg.setText("The total amount owned is being calculated!")
                        threadRunningMsg.exec()
                        return
                    tableModelTransfers = self.bottomRightAccountsPanelTable.model()
                    rows = []
                    for index in sorted(indexes):
                        rows.append(index.row())
                    rows.reverse()
                    for row in rows:
                        value = tableModelTransfers.data(tableModelTransfers.index(row, 5))
                        originValue = tableModelTransfers.data(tableModelTransfers.index(row, 6))
                        fromAccount = tableModelTransfers.data(tableModelTransfers.index(row, 1))
                        toAccount = tableModelTransfers.data(tableModelTransfers.index(row, 2))
                        tableModelTransfers.removeRow(row)

                        deleteTransferQuery = QSqlQuery()
                        deleteTransferQuery.exec(
                            f"SELECT currAmount FROM accounts WHERE userID = {self.userID} AND name = '{fromAccount}'")
                        if deleteTransferQuery.next():
                            newAmountFrom = Decimal(deleteTransferQuery.value(0)) + Decimal(originValue)
                            deleteTransferQuery.exec(
                                f"UPDATE accounts SET currAmount = '{newAmountFrom}' WHERE userID = {self.userID} AND name = '{fromAccount}'")
                        deleteTransferQuery.exec(
                            f"SELECT currAmount FROM accounts WHERE userID = {self.userID} AND name = '{toAccount}'")
                        if deleteTransferQuery.next():
                            newAmountTo = Decimal(deleteTransferQuery.value(0)) - Decimal(value)
                            deleteTransferQuery.exec(
                                f"UPDATE accounts SET currAmount = '{newAmountTo}' WHERE userID = {self.userID} AND name = '{toAccount}'")
                        deleteTransferQuery.finish()
                        tableModelTransfers.select()
                        self.fillTransfersTable()
                        self.fillAccountsTable()
                        self.fillSummaryPanel(self.theme)
        else:
            deleteTransferMsg.setText("Transfer is not selected!")
            deleteTransferMsg.exec()
            return None

    def editTransfer(self):
        editTransferMsg = QMessageBox()
        editTransferMsg.setWindowTitle("Warning")
        editTransferMsg.setIcon(QMessageBox.Warning)

        from editWindows import EditTransferWindow
        self.editTransferWindow = EditTransferWindow(self, self.userID)

        if self.bottomRightAccountsPanelTable.currentIndex().isValid():
            indexes = self.bottomRightAccountsPanelTable.selectionModel().selectedRows()
            if not indexes:
                editTransferMsg.setText("Transfer is not selected!")
                editTransferMsg.exec()
                return None
            tableModelTransfers = self.bottomRightAccountsPanelTable.model()
            self.editTransferWindow.show()
            for index in sorted(indexes):
                row = index.row()
                amount = Decimal(tableModelTransfers.data(tableModelTransfers.index(row, 6))).quantize(self.fractional,
                                                                                                       ROUND_HALF_UP)
                rate = Decimal(tableModelTransfers.data(tableModelTransfers.index(row, 7)))
                transferDate = tableModelTransfers.data(tableModelTransfers.index(row, 3))
                accountFrom = tableModelTransfers.data(tableModelTransfers.index(row, 1))
                accountTo = tableModelTransfers.data(tableModelTransfers.index(row, 2))
                transferID = tableModelTransfers.data(tableModelTransfers.index(row, 8))
                value = Decimal(tableModelTransfers.data(tableModelTransfers.index(row, 5)))

                year = int(transferDate[:4])
                month = int(transferDate[5:7])
                day = int(transferDate[8:])
                transferDate = QDate(year, month, day)

                selectCurrencyQuery = QSqlQuery()
                selectCurrencyQuery.exec(f"SELECT currency FROM accounts WHERE name = '{accountFrom}'")
                if selectCurrencyQuery.next():
                    currency = selectCurrencyQuery.value(0)
                    symbol = self.codes.get_symbol(currency)

                self.editTransferWindow.editTransferAmountEntry.setText(str(amount))
                self.editTransferWindow.editTransferSymbolLabel.setText(symbol)
                self.editTransferWindow.editTransferDateEntry.setDate(transferDate)

                self.editTransferWindow.editTransferEditButton.clicked.connect(
                    partial(self.editTf, amount, rate, accountFrom, accountTo, value, transferID))

            tableModelTransfers.select()
        else:
            editTransferMsg.setText("Transfer is not selected!")
            editTransferMsg.exec()
            return None

    def editTf(self, amount, rate, accountFrom, accountTo, value, transferID):
        editTransferMsg = QMessageBox()
        editTransferMsg.setWindowTitle("Warning")
        editTransferMsg.setIcon(QMessageBox.Warning)
        if self.thread.isRunning():
            editTransferMsg.setText("The total amount owned is being calculated!")
            editTransferMsg.exec()
            return

        updateTransferQuery = QSqlQuery()

        try:
            newAmount = Decimal(self.editTransferWindow.editTransferAmountEntry.text()).quantize(self.fractional,
                                                                                                 ROUND_HALF_UP)
            if newAmount <= 0:
                raise InvalidOperation
        except InvalidOperation:
            editTransferMsg.setText("Amount must be a number!")
            editTransferMsg.exec()
            updateTransferQuery.finish()
            return
        newTransferDate = self.editTransferWindow.editTransferDateEntry.date().toPyDate()

        if not updateTransferQuery.exec(
                f"SELECT accountID, currAmount, currency FROM accounts WHERE name = '{accountFrom}' AND userID = {self.userID}"):
            print(updateTransferQuery.lastError().databaseText())
            return -1
        if updateTransferQuery.next():
            accountFromID = updateTransferQuery.value(0)
            accountFromAmount = Decimal(updateTransferQuery.value(1))
            accountFromCurrency = updateTransferQuery.value(2)
        else:
            return -1
        if not updateTransferQuery.exec(
                f"SELECT accountID, currAmount FROM accounts WHERE name = '{accountTo}' AND userID = {self.userID}"):
            print(updateTransferQuery.lastError().databaseText())
            return -1
        if updateTransferQuery.next():
            accountToID = updateTransferQuery.value(0)
            accountToAmount = Decimal(updateTransferQuery.value(1))
        else:
            return -1

        if amount != newAmount:
            symbol = self.codes.get_symbol(accountFromCurrency)
            newAmountString = str(newAmount) + " " + symbol
            difference = amount - newAmount
            newAccountFromAmount = accountFromAmount + difference
            if rate == 0:
                newAccountToAmount = accountToAmount - difference
                updateTransferQuery.exec(
                    f"UPDATE transfers SET amount = '{newAmountString}', transferDate = '{newTransferDate}', originValue = {newAmount}, value = {newAmount} "
                    f"WHERE transferID = {transferID}")
            else:
                difference = (difference * rate).quantize(self.fractional, ROUND_HALF_UP)
                newValue = value - difference
                newAccountToAmount = accountToAmount - difference
                updateTransferQuery.exec(
                    f"UPDATE transfers SET amount = '{newAmountString}', transferDate = '{newTransferDate}', originValue = {newAmount}, value = {newValue} "
                    f"WHERE transferID = {transferID}")
            updateTransferQuery.exec(
                f"UPDATE accounts SET currAmount = {newAccountFromAmount} WHERE accountID = {accountFromID}")
            updateTransferQuery.exec(
                f"UPDATE accounts SET currAmount = {newAccountToAmount} WHERE accountID = {accountToID}")

        else:
            updateTransferQuery.exec(
                f"UPDATE transfers SET transferDate = '{newTransferDate}' WHERE transferID = {transferID}")

        self.con.commit()
        self.fillTransfersTable()
        self.fillAccountsTable()
        self.editTransferWindow.close()
