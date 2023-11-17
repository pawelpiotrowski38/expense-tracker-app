from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from PyQt5.QtChart import QChart, QPieSeries, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSlice
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPainter, QFont, QBrush, QColor
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QMessageBox, QScrollBar


class ClearFunctions:

    def clearTransactionInfo(self):
        """"Metoda czyszcząca formularz do tworzenia transakcji"""
        self.topLeftTransactionsValueEntry.setText('')
        self.topLeftTransactionsAccountEntry.setCurrentIndex(0)
        self.topLeftTransactionsDateEntry.setDate(date.today())
        self.topLeftTransactionsNotesEntry.setPlainText('')       
        if self.topLeftTransactionsExpenseRadioButton.isChecked():
            self.topLeftTransactionsTrType.setExclusive(False)
            self.topLeftTransactionsExpenseRadioButton.setChecked(False)
            self.topLeftTransactionsCategoryEntry.model().clear()
            self.topLeftTransactionsTrType.setExclusive(True)
        if self.topLeftTransactionsIncomeRadioButton.isChecked():
            self.topLeftTransactionsTrType.setExclusive(False)
            self.topLeftTransactionsIncomeRadioButton.setChecked(False)
            self.topLeftTransactionsCategoryEntry.model().clear()
            self.topLeftTransactionsTrType.setExclusive(True)

    def clearAccountInfo(self):
        """"Metoda czyszcząca formularz do tworzenia konta"""
        self.topLeftAccountsNameEntry.setText("")
        self.topLeftAccountsAmountEntry.setText("")
        currencyName = self.codes.get_currency_name(self.currencyCode)
        currencyName = self.currencyCode + ' - ' + currencyName
        self.topLeftAccountsCurrencyEntry.setCurrentText(currencyName)
        self.topLeftAccountsSyncCheckBox.setChecked(False)
        self.topLeftAccountsNotesEntry.setPlainText("")

    def clearTransferInfo(self):
        """"Metoda czyszcząca formularz do tworzenia przelewu"""
        self.bottomLeftAccountsFromEntry.setCurrentIndex(0)
        self.bottomLeftAccountsToEntry.setCurrentIndex(0)
        self.bottomLeftAccountsAmountEntry.setText("")
        self.bottomLeftAccountsRateEntry.setText("")
        self.bottomLeftAccountsRateCheckBox.setChecked(False)
        self.bottomLeftAccountsDateEntry.setDate(date.today())

    def clearBudgetInfo(self):
        """"Metoda czyszcząca formularz do tworzenia budżetu"""
        self.topLeftBudgetsNameEntry.setText("")
        self.topLeftBudgetsAmountEntry.setText("")
        self.topLeftBudgetsCategoryEntry.setCurrentIndex(0)
        self.topLeftBudgetsTypeEntry.setCurrentIndex(0)
        self.topLeftBudgetsFrequencyEntry.setCurrentIndex(0)
        self.topLeftBudgetsStartDateEntry.setDate(date.today())
        self.topLeftBudgetsEndDateEntry.setDate(date.today())
        self.topLeftBudgetsNotesEntry.setPlainText("")

    def clearReportInfo(self, reportType):
        """"Metoda czyszcząca formularz do rysowania wykresu"""
        if reportType == "category":
            self.topLeftReportsTypeRadioButtons.setExclusive(False)
            self.topLeftReportsExRadioButton.setChecked(False)
            self.topLeftReportsInRadioButton.setChecked(False)
            self.topLeftReportsBothRadioButton.setChecked(False)
            self.topLeftReportsTypeRadioButtons.setExclusive(True)
            self.topLeftReportsFromEntry.setDate(date.today())
            self.topLeftReportsToEntry.setDate(date.today())
            self.topLeftReportsAccountEntry.setCurrentIndex(0)
            self.topLeftReportsAcCheck.setChecked(False)
            self.topLeftReportsTypeEntry.setCurrentIndex(0)
        elif reportType == "time":
            self.bottomLeftReportsRadioButtonGroup.setExclusive(False)
            self.bottomLeftReportsExRadioButton.setChecked(False)
            self.bottomLeftReportsInRadioButton.setChecked(False)
            self.bottomLeftReportsBothRadioButton.setChecked(False)
            self.bottomLeftReportsRadioButtonGroup.setExclusive(True)
            if not self.bottomLeftReportsDaysRadioButton.isChecked():
                self.bottomLeftReportsDaysRadioButton.setChecked(True)
            self.bottomLeftReportsFromEntry.setDate(date.today())
            self.bottomLeftReportsToEntry.setDate(date.today())
            self.bottomLeftReportsAccountEntry.setCurrentIndex(0)
            self.bottomLeftReportsAcCheck.setChecked(False)

    def clearChart(self):
        """"Metoda czyszcząca obszar wykresu"""
        if self.isChartShown:
            print(self.chartView)
            self.rightReportsPanelVLayout.removeWidget(self.chartView)
            if self.isScrollShown:
                self.rightReportsPanelVLayout.removeWidget(self.scrollbar)
            self.chart = QChart()
            self.chartView = QChartView(self.chart)
            if self.theme:
                self.chart.setBackgroundBrush(QBrush(QColor(44, 45, 50, 255)))
                self.chartView.setBackgroundBrush(QBrush(QColor(44, 45, 50, 255)))
            else:
                self.chart.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
                self.chartView.setBackgroundBrush(QBrush(QColor(248, 249, 250, 255)))
            self.rightReportsPanelVLayout.addWidget(self.chartView)

    def clearRecurringTrInfo(self):
        """"Metoda czyszcząca formularz do tworzenia transakcji planowanej"""
        self.recurringNameEdit.setText('')
        self.recurringValueEntry.setText('')
        self.recurringAccountEntry.setCurrentIndex(0)
        self.recurringNotesEntry.setPlainText('')
        if self.recurringExpenseRadioButton.isChecked():
            self.recurringTrType.setExclusive(False)
            self.recurringExpenseRadioButton.setChecked(False)
            self.recurringCategoryEntry.model().clear()
            self.recurringTrType.setExclusive(True)
        if self.recurringIncomeRadioButton.isChecked():
            self.recurringTrType.setExclusive(False)
            self.recurringIncomeRadioButton.setChecked(False)
            self.recurringCategoryEntry.model().clear()
            self.recurringTrType.setExclusive(True)
