from datetime import date, datetime, timedelta
from calendar import monthrange
from functools import partial
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, InvalidOperation
from forex_python.converter import CurrencyRates
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtSql import QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QPushButton, QMessageBox, QFileDialog
from pandas import DataFrame


class CategoryFunctions:

    def editCategories(self, userID):
        from editWindows import EditCategoriesWindow
        self.editCategoriesWindow = EditCategoriesWindow(self, userID)
        self.editCategoriesWindow.show()
        # self.fillCategoriesComboBox()

        self.editCategoriesWindow.expenseRadioButton.isChecked()

        self.editCategoriesWindow.editCategoriesAddButton.clicked.connect(
            lambda: self.addCategory(self.editCategoriesWindow.expenseRadioButton.isChecked(),
                                     self.editCategoriesWindow.incomeRadioButton.isChecked(), "Add"))
        self.editCategoriesWindow.editCategoriesEditButton.clicked.connect(
            lambda: self.editCategory(self.editCategoriesWindow.expenseRadioButton.isChecked(),
                                      self.editCategoriesWindow.incomeRadioButton.isChecked(),
                                      self.editCategoriesWindow.editCategoriesComboBox.currentText(), "Edit"))
        self.editCategoriesWindow.editCategoriesDeleteButton.clicked.connect(
            lambda: self.deleteCategory(self.editCategoriesWindow.expenseRadioButton.isChecked(),
                                        self.editCategoriesWindow.incomeRadioButton.isChecked()))

    def addCategory(self, exStat, inStat, title):
        addCatMsg = QMessageBox()
        addCatMsg.setWindowTitle("Warning")
        addCatMsg.setIcon(QMessageBox.Warning)
        characters = "!\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"

        from editWindows import AddCategoryWindow
        self.addCategoryWindow = AddCategoryWindow(self, title)
        self.addCategoryWindow.show()

        def add():
            catType = self.addCategoryWindow.addCategoryTypeEntry.currentText()
            name = self.addCategoryWindow.addCategoryNameEntry.text()
            if len(name) < 3:
                addCatMsg.setText("Name must be at least 3 characters long.")
                addCatMsg.exec()
                return
            elif any(char in characters for char in name):
                addCatMsg.setText("Name can only contain letters, digits and underscores!")
                addCatMsg.exec()
                return

            addCategoryQuery = QSqlQuery()
            if catType == "Expense":
                addCategoryQuery.prepare("SELECT name FROM categories WHERE name = :name AND categoryType = 'expenses' AND userID = :userID")
            else:
                addCategoryQuery.prepare("SELECT name FROM categories WHERE name = :name AND categoryType = 'income' AND userID = :userID")
            addCategoryQuery.bindValue(":name", name)
            addCategoryQuery.bindValue(":userID", self.userID)
            addCategoryQuery.exec()
            if addCategoryQuery.next():
                addCatMsg.setText("Category with that name already exists!")
                addCatMsg.exec()
                return

            if catType == 'Expense':
                addCategoryQuery.exec(f"SELECT COUNT(name) FROM categories WHERE categoryType = 'expenses' AND userID = {self.userID}")
            else:
                addCategoryQuery.exec(f"SELECT COUNT(name) FROM categories WHERE categoryType = 'income' AND userID = {self.userID}")
            if addCategoryQuery.next():
                position = addCategoryQuery.value(0) + 1

            if catType == 'Expense':
                addCategoryQuery.exec(f"INSERT INTO categories (name, categoryType, position, userID) VALUES ('{name}', 'expenses', {position}, {self.userID})")
            else:
                addCategoryQuery.exec(f"INSERT INTO categories (name, categoryType, position, userID) VALUES ('{name}', 'income', {position}, {self.userID})")

            self.con.commit()

            if exStat:
                self.editCategoriesWindow.expenseRadioButton.setAutoExclusive(False)
                self.editCategoriesWindow.expenseRadioButton.setChecked(False)
                self.editCategoriesWindow.modelCatE.clear()
                self.editCategoriesWindow.expenseRadioButton.setChecked(True)
                self.editCategoriesWindow.expenseRadioButton.setAutoExclusive(True)
            elif inStat:
                self.editCategoriesWindow.incomeRadioButton.setAutoExclusive(False)
                self.editCategoriesWindow.incomeRadioButton.setChecked(False)
                self.editCategoriesWindow.modelCatI.clear()
                self.editCategoriesWindow.incomeRadioButton.setChecked(True)
                self.editCategoriesWindow.incomeRadioButton.setAutoExclusive(True)

            if self.topLeftTransactionsExpenseRadioButton.isChecked():
                self.topLeftTransactionsTrType.setExclusive(False)
                self.topLeftTransactionsExpenseRadioButton.setAutoExclusive(False)
                self.topLeftTransactionsExpenseRadioButton.setChecked(False)
                self.topLeftTransactionsCategoryEntry.model().clear()
                self.topLeftTransactionsExpenseRadioButton.setChecked(True)
                self.topLeftTransactionsExpenseRadioButton.setAutoExclusive(True)
                self.topLeftTransactionsTrType.setExclusive(True)
            elif self.topLeftTransactionsIncomeRadioButton.isChecked():
                self.topLeftTransactionsTrType.setExclusive(False)
                self.topLeftTransactionsIncomeRadioButton.setAutoExclusive(False)
                self.topLeftTransactionsIncomeRadioButton.setChecked(False)
                self.topLeftTransactionsCategoryEntry.model().clear()
                self.topLeftTransactionsIncomeRadioButton.setChecked(True)
                self.topLeftTransactionsIncomeRadioButton.setAutoExclusive(True)
                self.topLeftTransactionsTrType.setExclusive(True)

            if self.recurringExpenseRadioButton.isChecked():
                self.recurringTrType.setExclusive(False)
                self.recurringExpenseRadioButton.setAutoExclusive(False)
                self.recurringExpenseRadioButton.setChecked(False)
                self.recurringCategoryEntry.model().clear()
                self.recurringExpenseRadioButton.setChecked(True)
                self.recurringExpenseRadioButton.setAutoExclusive(True)
                self.recurringTrType.setExclusive(True)
            elif self.recurringIncomeRadioButton.isChecked():
                self.recurringTrType.setExclusive(False)
                self.recurringIncomeRadioButton.setAutoExclusive(False)
                self.recurringIncomeRadioButton.setChecked(False)
                self.recurringCategoryEntry.model().clear()
                self.recurringIncomeRadioButton.setChecked(True)
                self.recurringIncomeRadioButton.setAutoExclusive(True)
                self.recurringTrType.setExclusive(True)

            if self.rightTransactionsExpenseRadioButton.isChecked():
                self.filtersTrType.setExclusive(False)
                self.rightTransactionsExpenseRadioButton.setAutoExclusive(False)
                self.rightTransactionsExpenseRadioButton.setChecked(False)
                self.rightTransactionsFilterCategoryComboBox.model().clear()
                self.rightTransactionsExpenseRadioButton.setChecked(True)
                self.rightTransactionsExpenseRadioButton.setAutoExclusive(True)
                self.filtersTrType.setExclusive(True)
            elif self.rightTransactionsIncomeRadioButton.isChecked():
                self.filtersTrType.setExclusive(False)
                self.rightTransactionsIncomeRadioButton.setAutoExclusive(False)
                self.rightTransactionsIncomeRadioButton.setChecked(False)
                self.rightTransactionsFilterCategoryComboBox.model().clear()
                self.rightTransactionsIncomeRadioButton.setChecked(True)
                self.rightTransactionsIncomeRadioButton.setAutoExclusive(True)
                self.filtersTrType.setExclusive(True)

            self.addCategoryWindow.close()

        self.addCategoryWindow.addCategoryAddButton.clicked.connect(add)

    def editCategory(self, exStat, inStat, oldName, title):
        editCatMsg = QMessageBox()
        editCatMsg.setWindowTitle("Warning")
        editCatMsg.setIcon(QMessageBox.Warning)
        characters = "!\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"

        if oldName and exStat:
            temp = 'expenses'
        elif oldName and inStat:
            temp = 'income'
        else:
            editCatMsg.setText("Category is not selected!")
            editCatMsg.exec()
            return

        editCategoryQuery = QSqlQuery()
        editCategoryQuery.exec(f"SELECT position FROM categories WHERE name = '{oldName}' AND categoryType = '{temp}' AND userID = {self.userID}")
        if editCategoryQuery.next():
            oldPosition = editCategoryQuery.value(0)

        from editWindows import EditCategoryWindow
        self.editCategoryWindow = EditCategoryWindow(self, title, temp)
        self.editCategoryWindow.show()
        self.editCategoryWindow.editCategoryNameEntry.setText(oldName)
        self.editCategoryWindow.editCategoryPositionEntry.setValue(oldPosition)

        def edit(temp, oldName, oldPosition):
            newName = self.editCategoryWindow.editCategoryNameEntry.text()
            newPosition = self.editCategoryWindow.editCategoryPositionEntry.value()
            if newName == oldName and newPosition == oldPosition:
                return

            if not newName == oldName:
                if len(newName) < 3:
                    editCatMsg.setText("Name must be at least 3 characters long.")
                    editCatMsg.exec()
                    return
                elif any(char in characters for char in newName):
                    editCatMsg.setText("Name can only contain letters, digits and undescores!")
                    editCatMsg.exec()
                    return
                editCategoryQuery.prepare("SELECT name FROM categories WHERE name = :name AND categoryType = :catType AND userID = :userID")
                editCategoryQuery.bindValue(":name", newName)
                editCategoryQuery.bindValue(":catType", temp)
                editCategoryQuery.bindValue(":userID", self.userID)
                editCategoryQuery.exec()
                if editCategoryQuery.next():
                    editCatMsg.setText("A category with that name already exists!")
                    editCatMsg.exec()
                    return

            if newPosition < oldPosition:
                editCategoryQuery.exec(
                    f"UPDATE categories SET position = position+1 WHERE categoryType = '{temp}' AND userID = {self.userID} AND position >= {newPosition} AND position < {oldPosition}")
            if newPosition > oldPosition:
                editCategoryQuery.exec(
                    f"UPDATE categories SET position = position-1 WHERE categoryType = '{temp}' AND userID = {self.userID} AND position > {oldPosition} AND position <= {newPosition}")

            editCategoryQuery.prepare(f"UPDATE categories SET name = :newName, position = :position WHERE name = :oldName AND categoryType = :catType AND userID = :userID")
            editCategoryQuery.bindValue(":newName", newName)
            editCategoryQuery.bindValue(":position", newPosition)
            editCategoryQuery.bindValue(":oldName", oldName)
            editCategoryQuery.bindValue(":catType", temp)
            editCategoryQuery.bindValue(":userID", self.userID)
            editCategoryQuery.exec()

            self.con.commit()
            self.fillTransactionTable()
            self.fillCategoriesComboBoxB()

            if temp == 'expenses':
                self.editCategoriesWindow.expenseRadioButton.setAutoExclusive(False)
                self.editCategoriesWindow.expenseRadioButton.setChecked(False)
                self.editCategoriesWindow.modelCatE.clear()
                self.editCategoriesWindow.expenseRadioButton.setChecked(True)
                self.editCategoriesWindow.expenseRadioButton.setAutoExclusive(True)
            else:
                self.editCategoriesWindow.incomeRadioButton.setAutoExclusive(False)
                self.editCategoriesWindow.incomeRadioButton.setChecked(False)
                self.editCategoriesWindow.modelCatI.clear()
                self.editCategoriesWindow.incomeRadioButton.setChecked(True)
                self.editCategoriesWindow.incomeRadioButton.setAutoExclusive(True)

            if self.topLeftTransactionsExpenseRadioButton.isChecked():
                self.topLeftTransactionsTrType.setExclusive(False)
                self.topLeftTransactionsExpenseRadioButton.setAutoExclusive(False)
                self.topLeftTransactionsExpenseRadioButton.setChecked(False)
                self.topLeftTransactionsCategoryEntry.model().clear()
                self.topLeftTransactionsExpenseRadioButton.setChecked(True)
                self.topLeftTransactionsExpenseRadioButton.setAutoExclusive(True)
                self.topLeftTransactionsTrType.setExclusive(True)
            elif self.topLeftTransactionsIncomeRadioButton.isChecked():
                self.topLeftTransactionsTrType.setExclusive(False)
                self.topLeftTransactionsIncomeRadioButton.setAutoExclusive(False)
                self.topLeftTransactionsIncomeRadioButton.setChecked(False)
                self.topLeftTransactionsCategoryEntry.model().clear()
                self.topLeftTransactionsIncomeRadioButton.setChecked(True)
                self.topLeftTransactionsIncomeRadioButton.setAutoExclusive(True)
                self.topLeftTransactionsTrType.setExclusive(True)

            if self.recurringExpenseRadioButton.isChecked():
                self.recurringTrType.setExclusive(False)
                self.recurringExpenseRadioButton.setAutoExclusive(False)
                self.recurringExpenseRadioButton.setChecked(False)
                self.recurringCategoryEntry.model().clear()
                self.recurringExpenseRadioButton.setChecked(True)
                self.recurringExpenseRadioButton.setAutoExclusive(True)
                self.recurringTrType.setExclusive(True)
            elif self.recurringIncomeRadioButton.isChecked():
                self.recurringTrType.setExclusive(False)
                self.recurringIncomeRadioButton.setAutoExclusive(False)
                self.recurringIncomeRadioButton.setChecked(False)
                self.recurringCategoryEntry.model().clear()
                self.recurringIncomeRadioButton.setChecked(True)
                self.recurringIncomeRadioButton.setAutoExclusive(True)
                self.recurringTrType.setExclusive(True)

            if self.rightTransactionsExpenseRadioButton.isChecked():
                self.filtersTrType.setExclusive(False)
                self.rightTransactionsExpenseRadioButton.setAutoExclusive(False)
                self.rightTransactionsExpenseRadioButton.setChecked(False)
                self.rightTransactionsFilterCategoryComboBox.model().clear()
                self.rightTransactionsExpenseRadioButton.setChecked(True)
                self.rightTransactionsExpenseRadioButton.setAutoExclusive(True)
                self.filtersTrType.setExclusive(True)
            elif self.rightTransactionsIncomeRadioButton.isChecked():
                self.filtersTrType.setExclusive(False)
                self.rightTransactionsIncomeRadioButton.setAutoExclusive(False)
                self.rightTransactionsIncomeRadioButton.setChecked(False)
                self.rightTransactionsFilterCategoryComboBox.model().clear()
                self.rightTransactionsIncomeRadioButton.setChecked(True)
                self.rightTransactionsIncomeRadioButton.setAutoExclusive(True)
                self.filtersTrType.setExclusive(True)

            self.editCategoryWindow.close()

        self.editCategoryWindow.editCategoryButton.clicked.connect(lambda: edit(temp, oldName, oldPosition))

    def deleteCategory(self, exStat, inStat):
        deleteCatMsg = QMessageBox()
        name = self.editCategoriesWindow.editCategoriesComboBox.currentText()
        deleteCatQuery = QSqlQuery()

        def delete(categoryType):
            deleteCatMsg.setWindowTitle("Confirm")
            deleteCatMsg.setIcon(QMessageBox.Question)
            deleteCatMsg.setText("The category will be deleted. \nDo you want to continue?")
            yesButton = QPushButton("Yes")
            noButton = QPushButton("No")
            deleteCatMsg.addButton(yesButton, QMessageBox.YesRole)
            deleteCatMsg.addButton(noButton, QMessageBox.NoRole)
            deleteCatMsg.exec()
            if deleteCatMsg.clickedButton() == yesButton:
                deleteCatQuery.exec(f"SELECT position FROM categories WHERE name = '{name}' AND categoryType = '{categoryType}' AND userID = {self.userID}")
                if deleteCatQuery.next():
                    position = deleteCatQuery.value(0)
                deleteCatQuery.exec(f"UPDATE categories SET position = position - 1 WHERE categoryType = '{categoryType}' AND userID = {self.userID} AND position > {position}")
                deleteCatQuery.exec(f"DELETE FROM categories WHERE name = '{name}' AND categoryType = '{categoryType}' AND userID = {self.userID}")
            else:
                return

        if name and self.editCategoriesWindow.expenseRadioButton.isChecked():
            delete('expenses')
        elif name and self.editCategoriesWindow.incomeRadioButton.isChecked():
            delete('income')
        else:
            deleteCatMsg.setWindowTitle("Warning")
            deleteCatMsg.setIcon(QMessageBox.Warning)
            deleteCatMsg.setText("Category is not selected!")
            deleteCatMsg.exec()
            return

        self.con.commit()
        if exStat:
            self.editCategoriesWindow.expenseRadioButton.setAutoExclusive(False)
            self.editCategoriesWindow.expenseRadioButton.setChecked(False)
            self.editCategoriesWindow.modelCatE.clear()
            self.editCategoriesWindow.expenseRadioButton.setChecked(True)
            self.editCategoriesWindow.expenseRadioButton.setAutoExclusive(True)
        elif inStat:
            self.editCategoriesWindow.incomeRadioButton.setAutoExclusive(False)
            self.editCategoriesWindow.incomeRadioButton.setChecked(False)
            self.editCategoriesWindow.modelCatI.clear()
            self.editCategoriesWindow.incomeRadioButton.setChecked(True)
            self.editCategoriesWindow.incomeRadioButton.setAutoExclusive(True)

        if self.topLeftTransactionsExpenseRadioButton.isChecked():
            self.topLeftTransactionsTrType.setExclusive(False)
            self.topLeftTransactionsExpenseRadioButton.setAutoExclusive(False)
            self.topLeftTransactionsExpenseRadioButton.setChecked(False)
            self.topLeftTransactionsCategoryEntry.model().clear()
            self.topLeftTransactionsExpenseRadioButton.setChecked(True)
            self.topLeftTransactionsExpenseRadioButton.setAutoExclusive(True)
            self.topLeftTransactionsTrType.setExclusive(True)
        elif self.topLeftTransactionsIncomeRadioButton.isChecked():
            self.topLeftTransactionsTrType.setExclusive(False)
            self.topLeftTransactionsIncomeRadioButton.setAutoExclusive(False)
            self.topLeftTransactionsIncomeRadioButton.setChecked(False)
            self.topLeftTransactionsCategoryEntry.model().clear()
            self.topLeftTransactionsIncomeRadioButton.setChecked(True)
            self.topLeftTransactionsIncomeRadioButton.setAutoExclusive(True)
            self.topLeftTransactionsTrType.setExclusive(True)

        if self.recurringExpenseRadioButton.isChecked():
            self.recurringTrType.setExclusive(False)
            self.recurringExpenseRadioButton.setAutoExclusive(False)
            self.recurringExpenseRadioButton.setChecked(False)
            self.recurringCategoryEntry.model().clear()
            self.recurringExpenseRadioButton.setChecked(True)
            self.recurringExpenseRadioButton.setAutoExclusive(True)
            self.recurringTrType.setExclusive(True)
        elif self.recurringIncomeRadioButton.isChecked():
            self.recurringTrType.setExclusive(False)
            self.recurringIncomeRadioButton.setAutoExclusive(False)
            self.recurringIncomeRadioButton.setChecked(False)
            self.recurringCategoryEntry.model().clear()
            self.recurringIncomeRadioButton.setChecked(True)
            self.recurringIncomeRadioButton.setAutoExclusive(True)
            self.recurringTrType.setExclusive(True)

        if self.rightTransactionsExpenseRadioButton.isChecked():
            self.filtersTrType.setExclusive(False)
            self.rightTransactionsExpenseRadioButton.setAutoExclusive(False)
            self.rightTransactionsExpenseRadioButton.setChecked(False)
            self.rightTransactionsFilterCategoryComboBox.model().clear()
            self.rightTransactionsExpenseRadioButton.setChecked(True)
            self.rightTransactionsExpenseRadioButton.setAutoExclusive(True)
            self.filtersTrType.setExclusive(True)
        elif self.rightTransactionsIncomeRadioButton.isChecked():
            self.filtersTrType.setExclusive(False)
            self.rightTransactionsIncomeRadioButton.setAutoExclusive(False)
            self.rightTransactionsIncomeRadioButton.setChecked(False)
            self.rightTransactionsFilterCategoryComboBox.model().clear()
            self.rightTransactionsIncomeRadioButton.setChecked(True)
            self.rightTransactionsIncomeRadioButton.setAutoExclusive(True)
            self.filtersTrType.setExclusive(True)
