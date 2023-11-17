from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from PyQt5.QtChart import QChart, QPieSeries, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSlice
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPainter, QFont, QBrush, QColor
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QMessageBox, QScrollBar


class FilterFunctions:

    def showFilters(self):
        """Metoda wyświetlająca filtry"""
        self.rightTransactionsFilterButton.setVisible(False)
        self.filtersGroupBox.setVisible(True)

    def hideFilters(self):
        """Metoda ukrywająca filtry"""
        self.filtersGroupBox.setVisible(False)
        self.rightTransactionsFilterButton.setVisible(True)

    def removeFilters(self):
        """Metoda usuwająca filtry"""
        self.fillTransactionTable()
        self.clearFilters()
        self.filtersGroupBox.setVisible(False)
        self.rightTransactionsFilterButton.setVisible(True)    

    def clearFilters(self):
        """Metoda czyszcząca filtry"""
        self.rightTransactionsFilterAmountCheckbox.setChecked(False)
        self.rightTransactionsFilterCategoryCheckbox.setChecked(False)
        self.rightTransactionsFilterAccountCheckbox.setChecked(False)
        self.rightTransactionsFilterDateCheckbox.setChecked(False)
        self.rightTransactionsFilterAmountFromEntry.setText('')
        self.rightTransactionsFilterAmountToEntry.setText('')
        self.rightTransactionsFilterAccountComboBox.setCurrentIndex(0)
        self.rightTransactionsFilterDateFromEntry.setDate(QDate.currentDate())
        self.rightTransactionsFilterDateToEntry.setDate(QDate.currentDate())
        if self.rightTransactionsExpenseRadioButton.isChecked():
            self.filtersTrType.setExclusive(False)
            self.rightTransactionsExpenseRadioButton.setChecked(False)
            self.rightTransactionsFilterCategoryComboBox.model().clear()
            self.filtersTrType.setExclusive(True)
        if self.rightTransactionsIncomeRadioButton.isChecked():
            self.filtersTrType.setExclusive(False)
            self.rightTransactionsIncomeRadioButton.setChecked(False)
            self.rightTransactionsFilterCategoryComboBox.model().clear()
            self.filtersTrType.setExclusive(True)
        
    def filterTransactions(self):
        """Metoda filtrująca transakcje"""
        filterMsg = QMessageBox()
        filterMsg.setWindowTitle("Warning")
        filterMsg.setIcon(QMessageBox.Warning)

        if self.rightTransactionsExpenseRadioButton.isChecked() or self.rightTransactionsIncomeRadioButton.isChecked():
            print('asd')
            self.fillTransactionTable()

        if self.rightTransactionsExpenseRadioButton.isChecked():
            transactionType = 'expenses'
        elif self.rightTransactionsIncomeRadioButton.isChecked():
            transactionType = 'income'
        else:
            filterMsg.setText("Transaction type is not selected!")
            filterMsg.exec()
            return
        filters = f"{transactionType}.userID = {self.userID}"
        if self.rightTransactionsFilterAmountCheckbox.isChecked():
            try:
                fromAmount = Decimal(self.rightTransactionsFilterAmountFromEntry.text()).quantize(self.fractional, ROUND_HALF_UP)
                toAmount = Decimal(self.rightTransactionsFilterAmountToEntry.text()).quantize(self.fractional, ROUND_HALF_UP)
            except InvalidOperation:
                filterMsg.setText("Amount must be a number!")
                filterMsg.exec()
                return
            filters = filters + f" AND {transactionType}.originValue BETWEEN {fromAmount} AND {toAmount}"
        if self.rightTransactionsFilterCategoryCheckbox.isChecked():
            category = self.rightTransactionsFilterCategoryComboBox.currentText()
            if not category:
                filterMsg.setText("Category is not selected!")
                filterMsg.exec()
                return
            selectCategoryIDQuery = QSqlQuery()
            if not selectCategoryIDQuery.exec(f"SELECT categoryID FROM categories WHERE name = '{category}' AND categoryType = '{transactionType}' AND userID = {self.userID}"):
                print(selectCategoryIDQuery.lastError().databaseText())
                return -1
            if selectCategoryIDQuery.next():
                categoryID = selectCategoryIDQuery.value(0)
            else:
                return -1
            filters = filters + f" AND {transactionType}.categoryID = {categoryID}"
        if self.rightTransactionsFilterAccountCheckbox.isChecked():
            account = self.rightTransactionsFilterAccountComboBox.currentText()
            if not account:
                filterMsg.setText("Account is not selected!")
                filterMsg.exec()
                return
            selectAccountIDQuery = QSqlQuery()
            if not selectAccountIDQuery.exec(f"SELECT accountID FROM accounts WHERE name = '{account}' AND userID = {self.userID}"):
                print(selectAccountIDQuery.lastError().databaseText())
                return -1
            if selectAccountIDQuery.next():
                accountID = selectAccountIDQuery.value(0)
            else:
                return -1
            filters = filters + f" AND {transactionType}.accountID = {accountID}"
        if self.rightTransactionsFilterDateCheckbox.isChecked():
            temp_var1 = self.rightTransactionsFilterDateFromEntry.date()
            dateFrom = temp_var1.toPyDate()
            temp_var2 = self.rightTransactionsFilterDateToEntry.date()
            dateTo = temp_var2.toPyDate()
            if dateTo < dateFrom:
                filterMsg.setText("Date!")
                filterMsg.exec()
                return
            filters = filters + f" AND {transactionType}.transactionDate BETWEEN '{dateFrom}' AND '{dateTo}'"
        self.filtersGroupBox.setVisible(False)
        self.rightTransactionsFilterButton.setVisible(True)
        print(filters)

        if self.rightTransactionsExpenseRadioButton.isChecked():
            self.fillTransactionTable(filtersEx=filters)
        elif self.rightTransactionsIncomeRadioButton.isChecked():
            self.fillTransactionTable(filtersIn=filters)

    def grayOutFilters(self, state, *args):
        """Metoda aktywująca i dezaktywująca wybór filtrów"""
        if state:
            for arg in args:
                arg.setDisabled(False)
        else:
            for arg in args:
                arg.setDisabled(True)
