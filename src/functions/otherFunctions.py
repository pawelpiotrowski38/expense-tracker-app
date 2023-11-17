from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from PyQt5.QtChart import QChart, QPieSeries, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSlice
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPainter, QFont, QBrush, QColor
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QMessageBox, QScrollBar


class OtherFunctions:

    def grayOutAccount(self, state, widget):
        """Metoda aktywująca lub dezaktywująca listy z wyborem konta"""
        if state:
            widget.setDisabled(True)
        else:
            widget.setDisabled(False)

    def grayOutBudget(self, choice):
        """Metoda aktywująca lub dezaktywująca wybór częstoltliwości lub dat początkowej i końcowej budżetu"""
        if choice == "Periodic":
            self.topLeftBudgetsFrequencyEntry.setDisabled(False)
            self.topLeftBudgetsStartDateEntry.setDisabled(True)
            self.topLeftBudgetsEndDateEntry.setDisabled(True)
        elif choice == "One-time":
            self.topLeftBudgetsFrequencyEntry.setDisabled(True)
            self.topLeftBudgetsStartDateEntry.setDisabled(False)
            self.topLeftBudgetsEndDateEntry.setDisabled(False)

    def setDateEdit(self):
        """Metoda zmieniająca wyświetlany format daty w zakładce z wykresami"""
        radioButton = self.sender()
        if radioButton.text() == "Days":
            self.bottomLeftReportsFromEntry.setDisplayFormat('dd.MM.yyyy')
            self.bottomLeftReportsToEntry.setDisplayFormat('dd.MM.yyyy')
            self.bottomLeftReportsFromEntry.setCalendarPopup(True)
            self.bottomLeftReportsToEntry.setCalendarPopup(True)
        elif radioButton.text() == 'Months':
            self.bottomLeftReportsFromEntry.setDisplayFormat('MM.yyyy')
            self.bottomLeftReportsToEntry.setDisplayFormat('MM.yyyy')
            self.bottomLeftReportsFromEntry.setCalendarPopup(False)
            self.bottomLeftReportsToEntry.setCalendarPopup(False)

    def calculator(self, userID):
        """Metoda tworząca okno kalkulatora i otwierająca je"""
        from calculatorWindow import CalculatorWindow
        self.calculatorWindow = CalculatorWindow(self, userID)
        self.calculatorWindow.show()
        self.calculatorWindow.converterButton.clicked.connect(self.converter)

    def converter(self):
        """Metoda tworząca okno konwertera walut i otwierająca je"""
        from calculatorWindow import ConverterWindow
        self.converterWindow = ConverterWindow(self)
        self.converterWindow.show()

    def changeScheduleType(self):
        """Metoda akywująca lub dezaktywująca widżety służące do konfiguracji planu transakcji planowanej"""
        radioButton = self.sender()
        if radioButton.text() == "One time":
            self.recurringFreqLabel.setDisabled(True)
            self.recurringFreqOccursLabel.setDisabled(True)
            self.recurringFreqComboBox.setDisabled(True)
            self.firstLayout.setDisabled(True)
            self.secondLayout.setDisabled(True)
            self.thirdLayout.setDisabled(True)
            self.recurringFreqOccursAtLabel.setDisabled(True)
            self.recurringFreqOccursAtTimeEntry.setDisabled(True)
            self.recurringDurationLabel.setDisabled(True)
            self.recurringDurationStartLabel.setDisabled(True)
            self.recurringDurationStartDateEntry.setDisabled(True)
            self.recurringDurationEndRadioButton.setDisabled(True)
            self.recurringDurationNoEndRadioButton.setDisabled(True)
            self.recurringDurationEndDateEntry.setDisabled(True)
        else:
            self.recurringFreqLabel.setDisabled(False)
            self.recurringFreqOccursLabel.setDisabled(False)
            self.recurringFreqComboBox.setDisabled(False)
            self.firstLayout.setDisabled(False)
            self.secondLayout.setDisabled(False)
            self.thirdLayout.setDisabled(False)
            self.recurringFreqOccursAtLabel.setDisabled(False)
            self.recurringFreqOccursAtTimeEntry.setDisabled(False)
            self.recurringDurationLabel.setDisabled(False)
            self.recurringDurationStartLabel.setDisabled(False)
            self.recurringDurationStartDateEntry.setDisabled(False)
            self.recurringDurationEndRadioButton.setDisabled(False)
            self.recurringDurationNoEndRadioButton.setDisabled(False)
            if self.recurringDurationEndRadioButton.isChecked():
                self.recurringDurationEndDateEntry.setDisabled(False)
        if radioButton.text() == "Recurring":
            self.recurringOnceLabel.setDisabled(True)
            self.recurringOnceDateLabel.setDisabled(True)
            self.recurringOnceTimeLabel.setDisabled(True)
            self.recurringOnceDateEntry.setDisabled(True)
            self.recurringOnceTimeEntry.setDisabled(True)
        else:
            self.recurringOnceLabel.setDisabled(False)
            self.recurringOnceDateLabel.setDisabled(False)
            self.recurringOnceTimeLabel.setDisabled(False)
            self.recurringOnceDateEntry.setDisabled(False)
            self.recurringOnceTimeEntry.setDisabled(False)

    def changeEndType(self):
        """Metoda aktywująca lub dezaktywująca wybór daty końcowej transakcji planowanej"""
        radioButton = self.sender()
        if radioButton.text() == "No end date":
            self.recurringDurationEndDateEntry.setDisabled(True)
        else:
            self.recurringDurationEndDateEntry.setDisabled(False)

    def changeFrequency(self, text):
        """Metoda zmieniająca widżety do wyboru częstotliwości dziennej, tygodniowej lub miesięcznej"""
        if text == 'Weekly':
            self.stackedLayout.setCurrentIndex(1)
        elif text == 'Daily':
            self.stackedLayout.setCurrentIndex(0)
        elif text == 'Monthly':
            self.stackedLayout.setCurrentIndex(2)

    def changeCurrencySymbol(self, text, widget):
        """Metoda zmieniająca symbol waluty"""
        if text == "":
            widget.setText("")
            return
        findSymbolQuery = QSqlQuery()
        findSymbolQuery.prepare(f"SELECT currency FROM accounts WHERE name = :name AND userID = :userID")
        findSymbolQuery.bindValue(":name", text)
        findSymbolQuery.bindValue(":userID", self.userID)
        if not findSymbolQuery.exec():
            return
        if findSymbolQuery.next():
            currency = findSymbolQuery.value(0)
            symbol = self.codes.get_symbol(currency)
            widget.setText(symbol)
            if currency != self.currencyCode:
                self.bottomLeftAccountsRateLabel.setDisabled(False)
                self.bottomLeftAccountsRateEntry.setDisabled(False)
                self.bottomLeftAccountsRateCheckBox.setDisabled(False)
            else:
                self.bottomLeftAccountsRateLabel.setDisabled(True)
                self.bottomLeftAccountsRateEntry.setDisabled(True)
                self.bottomLeftAccountsRateCheckBox.setDisabled(True)
        findSymbolQuery.finish()

    def changeRate(self, text1, text2):
        """Metoda aktywująca i dezaktywująca wybór kursu wymiany walut"""
        if text1 == "" or text2 == "":
            return
        findSymbolQuery = QSqlQuery()
        findSymbolQuery.prepare(f"SELECT currency FROM accounts WHERE name = :name AND userID = :userID")
        findSymbolQuery.bindValue(":name", text1)
        findSymbolQuery.bindValue(":userID", self.userID)
        if not findSymbolQuery.exec():
            return
        if findSymbolQuery.next():
            currency1 = findSymbolQuery.value(0)
        else:
            return
        findSymbolQuery.prepare(f"SELECT currency FROM accounts WHERE name = :name AND userID = :userID")
        findSymbolQuery.bindValue(":name", text2)
        findSymbolQuery.bindValue(":userID", self.userID)
        if not findSymbolQuery.exec():
            return
        if findSymbolQuery.next():
            currency2 = findSymbolQuery.value(0)
        else:
            return
        if currency1 != self.currencyCode or currency2 != self.currencyCode:
            self.bottomLeftAccountsRateLabel.setDisabled(False)
            self.bottomLeftAccountsRateEntry.setDisabled(False)
            self.bottomLeftAccountsRateCheckBox.setDisabled(False)
        else:
            self.bottomLeftAccountsRateLabel.setDisabled(True)
            self.bottomLeftAccountsRateEntry.setDisabled(True)
            self.bottomLeftAccountsRateCheckBox.setDisabled(True)

    def changeAccountSymbol(self, text):
        """Metoda zmieniająca symbol waluty podczas tworzenia konta"""
        currency = text[:3]
        symbol = self.codes.get_symbol(currency)
        self.topLeftAccountsSymbolLabel.setText(symbol)

    def settings(self, userID, currency, connection, username):
        """Metoda tworząca okno ustawień i otwierająca je"""
        from settingsWindow import SettingsWindow
        self.settingsWindow = SettingsWindow(self, userID, currency, connection, username)
        self.settingsWindow.setWindowTitle("Settings")
        self.settingsWindow.show()

    def refresh(self):
        """Metoda odświeżająca tabele i wykresy"""
        self.fillTransactionTable()
        self.fillAccountsTable()
        self.fillJobsTable()
        self.fillSummaryPanel(self.theme)
        self.fillAmountOwned()
        self.fillDailyCharts(self.theme)
        self.fillBudgetsCharts()

    def refreshCharts(self):
        """Metoda odświeżająca tylko wykresy"""
        self.fillSummaryPanel(self.theme)
        self.fillDailyCharts(self.theme)
        self.fillBudgetsCharts()
