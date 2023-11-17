from datetime import date, datetime, timedelta
from calendar import monthrange
from functools import partial
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, InvalidOperation
from forex_python.converter import CurrencyRates
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtSql import QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QPushButton, QMessageBox, QFileDialog
from pandas import DataFrame


class TransactionFunctions:

    def addTransaction(self):
        addTrMsg = QMessageBox()
        addTrMsg.setWindowTitle("Warning")
        addTrMsg.setIcon(QMessageBox.Warning)

        def add(tableName, factor):
            try:
                transactionValue = Decimal(self.topLeftTransactionsValueEntry.text()).quantize(self.fractional,
                                                                                               ROUND_HALF_UP)
                if transactionValue <= 0:
                    raise InvalidOperation
            except InvalidOperation:
                addTrMsg.setText("Amount must be a number!")
                addTrMsg.exec()
                return -1
            transactionAmount = str(transactionValue) + ' ' + self.topLeftTransactionsSymbolLabel.text()
            transactionCategory = self.topLeftTransactionsCategoryEntry.currentText()
            transactionAccount = self.topLeftTransactionsAccountEntry.currentText()
            if not transactionCategory:
                addTrMsg.setText("Category is not selected!")
                addTrMsg.exec()
                return -1
            if not transactionAccount:
                addTrMsg.setText("Account is not selected!")
                addTrMsg.exec()
                return -1
            transactionDate = self.topLeftTransactionsDateEntry.date().toPyDate()
            transactionNotes = self.topLeftTransactionsNotesEntry.toPlainText()
            if len(transactionNotes) > 100:
                addTrMsg.setText("Notes length cannot be greater than 100 characters.")
                addTrMsg.exec()
                return -1

            addTransactionQuery = QSqlQuery()
            addTransactionQuery.prepare("SELECT categoryID FROM categories WHERE name = :name AND categoryType = :tableName AND userID = :userID")
            addTransactionQuery.bindValue(":name", transactionCategory)
            addTransactionQuery.bindValue(":tableName", tableName)
            addTransactionQuery.bindValue(":userID", self.userID)
            if not addTransactionQuery.exec():
                print(addTransactionQuery.lastError().databaseText())
                return -1
            if addTransactionQuery.next():
                transactionCategoryID = addTransactionQuery.value(0)
            else:
                return -1
            addTransactionQuery.prepare("SELECT accountID FROM accounts WHERE name = :name AND userID = :userID")
            addTransactionQuery.bindValue(":name", transactionAccount)
            addTransactionQuery.bindValue(":userID", self.userID)
            if not addTransactionQuery.exec():
                print(addTransactionQuery.lastError().databaseText())
                return -1
            if addTransactionQuery.next():
                transactionAccountID = addTransactionQuery.value(0)
            else:
                return -1

            addTransactionQuery.prepare("SELECT currency FROM accounts WHERE name = :name AND userID = :userID")
            addTransactionQuery.bindValue(":name", transactionAccount)
            addTransactionQuery.bindValue(":userID", self.userID)
            if not addTransactionQuery.exec():
                addTrMsg.setText("Database error!")
                addTrMsg.setDetailedText(addTransactionQuery.lastError().text())
                addTrMsg.exec()
                addTransactionQuery.finish()
                return -1
            if addTransactionQuery.next():
                transactionAccountCurrency = addTransactionQuery.value(0)
            else:
                return -1

            if transactionAccountCurrency != self.currencyCode:
                convertedTransactionValue = (
                    self.rates.convert(transactionAccountCurrency, self.currencyCode, transactionValue)).quantize(
                    self.fractional, ROUND_HALF_UP)
            else:
                convertedTransactionValue = transactionValue

            addTransactionQuery.prepare(
                f"INSERT INTO {tableName} (amount, transactionDate, notes, value, originValue, currency, userID, accountID, categoryID) "
                f"VALUES (:amount, '{transactionDate}', :notes, {convertedTransactionValue}, {transactionValue}, :currency, :userID, :accountID, :categoryID)")
            addTransactionQuery.bindValue(":amount", transactionAmount)
            addTransactionQuery.bindValue(":notes", transactionNotes)
            addTransactionQuery.bindValue(":currency", transactionAccountCurrency)
            addTransactionQuery.bindValue(":userID", self.userID)
            addTransactionQuery.bindValue(":accountID", transactionAccountID)
            addTransactionQuery.bindValue(":categoryID", transactionCategoryID)
            if not addTransactionQuery.exec():
                addTrMsg.setText("Database error!")
                addTrMsg.setDetailedText(addTransactionQuery.lastError().text())
                addTrMsg.exec()
                addTransactionQuery.finish()
                return -1

            addTransactionQuery.prepare("SELECT currAmount FROM accounts WHERE name = :name AND userID = :userID")
            addTransactionQuery.bindValue(":name", transactionAccount)
            addTransactionQuery.bindValue(":userID", self.userID)
            if not addTransactionQuery.exec():
                addTrMsg.setText("Database error!")
                addTrMsg.setDetailedText(addTransactionQuery.lastError().text())
                addTrMsg.exec()
                addTransactionQuery.finish()
                return -1
            if addTransactionQuery.next():
                accAmount = Decimal(addTransactionQuery.value(0))
                accAmountUpdated = accAmount - (factor * transactionValue)
                addTransactionQuery.prepare(
                    f"UPDATE accounts SET currAmount = {accAmountUpdated} WHERE name = :name AND userID = :userID")
                addTransactionQuery.bindValue(":name", transactionAccount)
                addTransactionQuery.bindValue(":userID", self.userID)
                if not addTransactionQuery.exec():
                    addTrMsg.setText("Database error!")
                    addTrMsg.setDetailedText(addTransactionQuery.lastError().text())
                    addTrMsg.exec()
                    addTransactionQuery.finish()
                    return -1
            addTransactionQuery.finish()

        if self.topLeftTransactionsExpenseRadioButton.isChecked():
            if add("expenses", 1) == -1:
                return
        elif self.topLeftTransactionsIncomeRadioButton.isChecked():
            if add("income", -1) == -1:
                return
        else:
            addTrMsg.setText("Type of transaction is not selected!")
            addTrMsg.exec()
            return

        self.clearTransactionInfo()
        self.fillTransactionTable()
        self.fillAmountOwned()
        self.fillSummaryPanel(self.theme)
        self.fillAccountsTable()
        self.fillDailyCharts(self.theme)
        self.fillBudgetsCharts()

    def deleteTransaction(self):
        deleteTrMsg = QMessageBox()
        deleteTrMsg.setWindowTitle("Info")
        deleteTrMsg.setIcon(QMessageBox.Warning)

        def delete(table, model, factor):
            indexes = table.selectionModel().selectedRows()
            if not indexes:
                deleteTrMsg.setText("Transaction is not selected!")
                deleteTrMsg.exec()
                return
            else:
                deleteTrMsg.setWindowTitle("Confirm")
                deleteTrMsg.setIcon(QMessageBox.Question)
                deleteTrMsg.setText("The transaction will be deleted. Do you want to continue?")
                yesButton = QPushButton("Yes")
                noButton = QPushButton("No")
                deleteTrMsg.addButton(yesButton, QMessageBox.YesRole)
                deleteTrMsg.addButton(noButton, QMessageBox.NoRole)
                deleteTrMsg.exec()
                if deleteTrMsg.clickedButton() == yesButton:
                    rows = []
                    for index in sorted(indexes):
                        rows.append(index.row())
                    rows.reverse()
                    for row in rows:
                        transactionValue = Decimal(model.data(model.index(row, 6))).quantize(self.fractional,
                                                                                             ROUND_HALF_UP)
                        transactionAccount = model.data(model.index(row, 2))
                        deleteTransactionQuery = QSqlQuery()
                        deleteTransactionQuery.prepare(
                            "SELECT currAmount FROM accounts WHERE name = :name AND userID = :userID")
                        deleteTransactionQuery.bindValue(":name", transactionAccount)
                        deleteTransactionQuery.bindValue(":userID", self.userID)
                        if not deleteTransactionQuery.exec():
                            deleteTrMsg.setText("Database error!")
                            deleteTrMsg.setDetailedText(deleteTransactionQuery.lastError().text())
                            deleteTrMsg.exec()
                            deleteTransactionQuery.finish()
                            return -1
                        if deleteTransactionQuery.next():
                            transactionAccountAmount = Decimal(deleteTransactionQuery.value(0))
                        else:
                            return -1
                        newTransactionAccountAmount = transactionAccountAmount + factor * transactionValue
                        deleteTransactionQuery.prepare(
                            f"UPDATE accounts SET currAmount = {newTransactionAccountAmount} WHERE name = :name AND userID = :userID")
                        deleteTransactionQuery.bindValue(":name", transactionAccount)
                        deleteTransactionQuery.bindValue(":userID", self.userID)
                        deleteTransactionQuery.exec()
                        deleteTransactionQuery.finish()

                        model.removeRow(row)
                        model.select()
                        self.con.commit()
                        self.fillAmountOwned()
                        self.fillSummaryPanel(self.theme)
                        self.fillAccountsTable()
                        self.fillDailyCharts(self.theme)
                        self.fillBudgetsCharts()

        if self.rightTransactionsTableExpenses.currentIndex().isValid():
            delete(self.rightTransactionsTableExpenses, self.rightTransactionsTableExpenses.model(), 1)
        elif self.rightTransactionsTableIncome.currentIndex().isValid():
            delete(self.rightTransactionsTableIncome, self.rightTransactionsTableIncome.model(), -1)
        else:
            deleteTrMsg.setText("Transaction is not selected!")
            deleteTrMsg.exec()

    def editTransaction(self):
        editTrMsg = QMessageBox()
        editTrMsg.setWindowTitle("Warning")
        editTrMsg.setIcon(QMessageBox.Warning)

        from editWindows import EditTransactionWindow
        self.editTransactionWindow = EditTransactionWindow(self)

        def edit(table, tableModel, tableName, isExpense):
            indexes = table.selectionModel().selectedRows()
            if not indexes:
                editTrMsg.setText("Transaction is not selected!")
                editTrMsg.exec()
                return
            self.editTransactionWindow.show()
            for index in sorted(indexes):
                row = index.row()
                transactionValue = Decimal(tableModel.data(tableModel.index(row, 6))).quantize(self.fractional,
                                                                                               ROUND_HALF_UP)
                transactionCategory = tableModel.data(tableModel.index(row, 1))
                transactionAccount = tableModel.data(tableModel.index(row, 2))
                transactionDate = tableModel.data(tableModel.index(row, 3))
                transactionNotes = tableModel.data(tableModel.index(row, 4))
                originTransactionValue = Decimal(tableModel.data(tableModel.index(row, 6))).quantize(self.fractional,
                                                                                                     ROUND_HALF_UP)
                transactionID = tableModel.data(tableModel.index(row, 8))

                year = int(transactionDate[:4])
                month = int(transactionDate[5:7])
                day = int(transactionDate[8:])
                transactionDate = QDate(year, month, day)

                self.catModel = QSqlTableModel()
                self.catModel.setTable(tableName)
                self.catModel.setFilter(f"userID = {self.userID}")
                self.catModel.select()
                self.editTransactionWindow.editTransactionCategoryEntry.setModel(self.catModel)
                self.editTransactionWindow.editTransactionCategoryEntry.setModelColumn(self.catModel.fieldIndex("name"))

                self.modelAcc = QSqlTableModel()
                self.modelAcc.setTable("accounts")
                self.modelAcc.setFilter(f"userID = {self.userID}")
                self.modelAcc.select()
                self.editTransactionWindow.editTransactionAccountEntry.setModel(self.modelAcc)
                self.editTransactionWindow.editTransactionAccountEntry.setModelColumn(self.modelAcc.fieldIndex("name"))

                self.editTransactionWindow.editTransactionAmountEntry.setText(str(transactionValue))
                self.editTransactionWindow.editTransactionCategoryEntry.setCurrentText(transactionCategory)
                self.editTransactionWindow.editTransactionAccountEntry.setCurrentText(transactionAccount)
                self.editTransactionWindow.editTransactionDateEntry.setDate(transactionDate)
                self.editTransactionWindow.editTransactionNotesEntry.setPlainText(transactionNotes)

                expense = isExpense
                self.editTransactionWindow.editTransactionEditButton.clicked.connect(
                    partial(self.editTr, transactionAccount, expense, transactionValue, originTransactionValue,
                            transactionID))

            tableModel.select()

        if self.rightTransactionsTableExpenses.currentIndex().isValid() and self.rightTransactionsTabExpenses.isVisible():
            edit(self.rightTransactionsTableExpenses, self.rightTransactionsTableExpenses.model(), "categories", True)
        elif self.rightTransactionsTableIncome.currentIndex().isValid() and self.rightTransactionsTabIncome.isVisible():
            edit(self.rightTransactionsTableIncome, self.rightTransactionsTableIncome.model(), "categories", False)
        else:
            editTrMsg.setText("Transaction is not selected!")
            editTrMsg.exec()
            return

    def editTr(self, acc, expense, val, originVal, transactionID):
        editTrMsg = QMessageBox()
        editTrMsg.setWindowTitle("Warning")
        editTrMsg.setIcon(QMessageBox.Warning)
        rates = CurrencyRates()

        try:
            newTransactionValue = Decimal(self.editTransactionWindow.editTransactionAmountEntry.text()).quantize(
                self.fractional, ROUND_HALF_UP)
            if newTransactionValue <= 0:
                raise InvalidOperation
        except InvalidOperation:
            editTrMsg.setText("Amount must be a number!")
            editTrMsg.exec()
            return
        newTransactionCategory = self.editTransactionWindow.editTransactionCategoryEntry.currentText()
        newTransactionAccount = self.editTransactionWindow.editTransactionAccountEntry.currentText()
        if expense:
            categoryType = 'expenses'
        else:
            categoryType = 'income'
        editTransactionQuery = QSqlQuery()
        if not editTransactionQuery.exec(
                f"SELECT categoryID FROM categories WHERE name = '{newTransactionCategory}' AND categoryType = '{categoryType}' AND userID = {self.userID}"):
            print(editTransactionQuery.lastError().databaseText())
            return -1
        if editTransactionQuery.next():
            newTransactionCategoryID = editTransactionQuery.value(0)
        else:
            return -1
        if not editTransactionQuery.exec(
                f"SELECT accountID FROM accounts WHERE name = '{newTransactionAccount}' AND userID = {self.userID}"):
            print(editTransactionQuery.lastError().databaseText())
            return -1
        if editTransactionQuery.next():
            newTransactionAccountID = editTransactionQuery.value(0)
        else:
            return -1

        newTransactionDate = self.editTransactionWindow.editTransactionDateEntry.date().toPyDate()
        newTransactionNotes = self.editTransactionWindow.editTransactionNotesEntry.toPlainText()
        if len(newTransactionNotes) > 100:
            editTrMsg.setText("Notes length cannot be greater than 100 characters.")
            editTrMsg.exec()
            return -1

        editTransactionQuery.prepare("SELECT currency FROM accounts WHERE name = :acc")
        editTransactionQuery.bindValue(":acc", acc)
        if not editTransactionQuery.exec():
            return -1
        if editTransactionQuery.next():
            oldAccountCurrency = editTransactionQuery.value(0)
        else:
            return -1

        editTransactionQuery.prepare("SELECT currency FROM accounts WHERE name = :newAcc")
        editTransactionQuery.bindValue(":newAcc", newTransactionAccount)
        if not editTransactionQuery.exec():
            return -1
        if editTransactionQuery.next():
            newAccountCurrency = editTransactionQuery.value(0)
        else:
            return -1

        newTransactionAmount = str(
            newTransactionValue) + ' ' + self.editTransactionWindow.editTransactionSymbolLabel.text()

        if oldAccountCurrency == newAccountCurrency:
            if newAccountCurrency != self.currencyCode:
                convertedTransactionValue = rates.convert(newAccountCurrency, self.currencyCode, newTransactionValue)
            else:
                convertedTransactionValue = newTransactionValue

            if expense:
                editTransactionQuery.prepare(f"UPDATE expenses "
                                             f"SET amount = '{newTransactionAmount}', categoryID = :newCatID, accountID = :newAccID, transactionDate = '{newTransactionDate}', notes = :newNotes, value = {convertedTransactionValue}, originValue = {newTransactionValue}, currency = '{newAccountCurrency}' "
                                             f"WHERE transactionID = {transactionID} AND userID = {self.userID}")
                editTransactionQuery.bindValue(":newCatID", newTransactionCategoryID)
                editTransactionQuery.bindValue(":newAccID", newTransactionAccountID)
                editTransactionQuery.bindValue(":newNotes", newTransactionNotes)
                if not editTransactionQuery.exec():
                    print(editTransactionQuery.lastQuery())
                    return -1
            else:
                editTransactionQuery.prepare(f"UPDATE income "
                                             f"SET amount = '{newTransactionAmount}', categoryID = :newCatID, accountID = :newAccID, transactionDate = '{newTransactionDate}', notes = :newNotes, value = {convertedTransactionValue}, originValue = {newTransactionValue}, currency = '{newAccountCurrency}' "
                                             f"WHERE transactionID = {transactionID} AND userID = {self.userID}")
                editTransactionQuery.bindValue(":newCatID", newTransactionCategoryID)
                editTransactionQuery.bindValue(":newAccID", newTransactionAccountID)
                editTransactionQuery.bindValue(":newNotes", newTransactionNotes)
                if not editTransactionQuery.exec():
                    print(editTransactionQuery.lastQuery())
                    return -1

            editTransactionQuery.prepare("SELECT currAmount FROM accounts WHERE name = :acc AND userID = :userID")
            editTransactionQuery.bindValue(":acc", acc)
            editTransactionQuery.bindValue(":userID", self.userID)
            editTransactionQuery.exec()
            if editTransactionQuery.next():
                accountAmount = Decimal(editTransactionQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP)
            else:
                return
            difference = newTransactionValue - val

            if newTransactionAccount == acc:
                if expense:
                    accountNewAmount = accountAmount - difference
                else:
                    accountNewAmount = accountAmount + difference

                editTransactionQuery.prepare(
                    f"UPDATE accounts SET currAmount = '{accountNewAmount}' WHERE name = :acc AND userID = :userID")
                editTransactionQuery.bindValue(":acc", acc)
                editTransactionQuery.bindValue(":userID", self.userID)
                editTransactionQuery.exec()
            else:
                editTransactionQuery.prepare(
                    "SELECT currAmount FROM accounts WHERE name = :newAcc AND userID = :userID")
                editTransactionQuery.bindValue(":newAcc", newTransactionAccount)
                editTransactionQuery.bindValue(":userID", self.userID)
                editTransactionQuery.exec()
                if editTransactionQuery.next():
                    newAccountAmount = Decimal(editTransactionQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP)
                else:
                    return

                if expense:
                    newCurrAmount = accountAmount + val
                    editTransactionQuery.prepare(
                        f"UPDATE accounts SET currAmount = '{newCurrAmount}' WHERE name = :acc AND userID = :userID")
                    editTransactionQuery.bindValue(":acc", acc)
                    editTransactionQuery.bindValue(":userID", self.userID)
                    editTransactionQuery.exec()
                    newCurrAmount = newAccountAmount - newTransactionValue
                    editTransactionQuery.prepare(
                        f"UPDATE accounts SET currAmount = '{newCurrAmount}' WHERE name = :newAcc AND userID = :userID")
                    editTransactionQuery.bindValue(":newAcc", newTransactionAccount)
                    editTransactionQuery.bindValue(":userID", self.userID)
                    editTransactionQuery.exec()
                else:
                    newCurrAmount = accountAmount - val
                    editTransactionQuery.prepare(
                        f"UPDATE accounts SET currAmount = '{newCurrAmount}' WHERE name = :acc AND userID = :userID")
                    editTransactionQuery.bindValue(":acc", acc)
                    editTransactionQuery.bindValue(":userID", self.userID)
                    editTransactionQuery.exec()
                    newCurrAmount = newAccountAmount + newTransactionValue
                    editTransactionQuery.prepare(
                        f"UPDATE accounts SET currAmount = '{newCurrAmount}' WHERE name = :newAcc AND userID = :userID")
                    editTransactionQuery.bindValue(":newAcc", newTransactionAccount)
                    editTransactionQuery.bindValue(":userID", self.userID)
                    editTransactionQuery.exec()
        else:
            if newAccountCurrency != self.currencyCode:
                convertedValue = rates.convert(newAccountCurrency, self.currencyCode, newTransactionValue)
            else:
                convertedValue = newTransactionValue

            if expense:
                editTransactionQuery.prepare(f"UPDATE expenses "
                                             f"SET amount = '{newTransactionAmount}', categoryID = :newCatID, accountID = :newAccID, transactionDate = '{newTransactionDate}', notes = :newNotes, value = {convertedValue}, originValue = {newTransactionValue}, currency = '{newAccountCurrency}' "
                                             f"WHERE transactionID = '{transactionID}' AND userID = {self.userID}")
                editTransactionQuery.bindValue(":newCatID", newTransactionCategoryID)
                editTransactionQuery.bindValue(":newAccID", newTransactionAccountID)
                editTransactionQuery.bindValue(":newNotes", newTransactionNotes)
                if not editTransactionQuery.exec():
                    print(editTransactionQuery.lastQuery())
                    return -1
            else:
                editTransactionQuery.prepare(f"UPDATE income "
                                             f"SET amount = '{newTransactionAmount}', categoryID = :newCatID, accountID = :newAccID, transactionDate = '{newTransactionDate}', notes = :newNotes, value = {convertedValue}, originValue = {newTransactionValue}, currency = '{newAccountCurrency}' "
                                             f"WHERE transactionID = '{transactionID}' AND userID = {self.userID}")
                editTransactionQuery.bindValue(":newCatID", newTransactionCategoryID)
                editTransactionQuery.bindValue(":newAccID", newTransactionAccountID)
                editTransactionQuery.bindValue(":newNotes", newTransactionNotes)
                if not editTransactionQuery.exec():
                    print(editTransactionQuery.lastQuery())
                    return -1

            editTransactionQuery.prepare("SELECT currAmount FROM accounts WHERE name = :acc AND userID = :userID")
            editTransactionQuery.bindValue(":acc", acc)
            editTransactionQuery.bindValue(":userID", self.userID)
            editTransactionQuery.exec()
            if editTransactionQuery.next():
                accountAmount = Decimal(editTransactionQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP)
            else:
                return
            # difference = newVal - val

            editTransactionQuery.prepare("SELECT currAmount FROM accounts WHERE name = :newAcc AND userID = :userID")
            editTransactionQuery.bindValue(":newAcc", newTransactionAccount)
            editTransactionQuery.bindValue(":userID", self.userID)
            editTransactionQuery.exec()
            if editTransactionQuery.next():
                newAccAmount = Decimal(editTransactionQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP)
            else:
                return
            if expense:
                newCurrAmount = accountAmount + originVal
                editTransactionQuery.prepare(
                    f"UPDATE accounts SET currAmount = '{newCurrAmount}' WHERE name = :acc AND userID = :userID")
                editTransactionQuery.bindValue(":acc", acc)
                editTransactionQuery.bindValue(":userID", self.userID)
                editTransactionQuery.exec()
                newCurrAmount = newAccAmount - newTransactionValue
                editTransactionQuery.prepare(
                    f"UPDATE accounts SET currAmount = '{newCurrAmount}' WHERE name = :newAcc AND userID = :userID")
                editTransactionQuery.bindValue(":newAcc", newTransactionAccount)
                editTransactionQuery.bindValue(":userID", self.userID)
                editTransactionQuery.exec()
            else:
                newCurrAmount = accountAmount - originVal
                editTransactionQuery.prepare(
                    f"UPDATE accounts SET currAmount = '{newCurrAmount}' WHERE name = :acc AND userID = :userID")
                editTransactionQuery.bindValue(":acc", acc)
                editTransactionQuery.bindValue(":userID", self.userID)
                editTransactionQuery.exec()
                newCurrAmount = newAccAmount + newTransactionValue
                editTransactionQuery.prepare(
                    f"UPDATE accounts SET currAmount = '{newCurrAmount}' WHERE name = :newAcc AND userID = :userID")
                editTransactionQuery.bindValue(":newAcc", newTransactionAccount)
                editTransactionQuery.bindValue(":userID", self.userID)
                editTransactionQuery.exec()

        editTransactionQuery.finish()

        self.con.commit()
        self.fillAccountsTable()
        self.fillTransactionTable()
        self.fillAmountOwned()
        self.fillSummaryPanel(self.theme)
        self.fillDailyCharts(self.theme)
        self.fillBudgetsCharts()
        self.editTransactionWindow.close()

    def exportTransactions(self):
        exportMsg = QMessageBox()
        exportMsg.setWindowTitle("Warning")
        exportMsg.setIcon(QMessageBox.Warning)

        columnList = []
        for j in range(5):
            columnList.append(self.rightTransactionsTableExpenses.model().headerData(j, Qt.Horizontal))
        columnList.append("Currency")

        df = DataFrame(columns=columnList)

        if self.rightTransactionsTabExpenses.isVisible():
            rowNumber = self.rightTransactionsTableExpenses.model().rowCount()
            if rowNumber == 0:
                exportMsg.setText("Expenses table is empty!")
                exportMsg.exec()
                return
            for row in range(rowNumber):
                for col in range(5):
                    df.at[row, columnList[col]] = self.rightTransactionsTableExpenses.model().index(row, col).data()
                df.at[row, "Currency"] = self.rightTransactionsTableExpenses.model().index(row, 7).data()

        elif self.rightTransactionsTabIncome.isVisible():
            rowNumber = self.rightTransactionsTableIncome.model().rowCount()
            if rowNumber == 0:
                exportMsg.setText("Income table is empty!")
                exportMsg.exec()
                return
            for row in range(rowNumber):
                for col in range(5):
                    df.at[row, columnList[col]] = self.rightTransactionsTableIncome.model().index(row, col).data()
                df.at[row, "Currency"] = self.rightTransactionsTableIncome.model().index(row, 7).data()

        fileDialog = QFileDialog()
        filePath = fileDialog.getSaveFileName(filter="csv(*.csv)")
        if not filePath[0]:
            return
        print(df)
        df.to_csv(filePath[0], index=False)

    def importTransactions(self, userID, currency, connection):
        from importWindow import ImportWindow
        self.importWindow = ImportWindow(self, userID, currency, connection)
        self.importWindow.setWindowTitle("Import transactions")
        self.importWindow.show()
