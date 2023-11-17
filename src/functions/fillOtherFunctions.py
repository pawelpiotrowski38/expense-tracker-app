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


class FillOtherFunctions:

    def __init__(self):
        super().__init__()

    def fillAmountOwned(self):
        currencyRates = {}
        amounts = []
        currencies = []
        sumTotalQuery = QSqlQuery()
        if not sumTotalQuery.exec(f"SELECT currency FROM accounts WHERE userID = {self.userID}"):
            return
        while sumTotalQuery.next():
            currency = sumTotalQuery.value(0)
            currencyRates[currency] = 0
            currencies.append(currency)
        print(currencyRates)
        print(currencies)
        if not sumTotalQuery.exec(f"SELECT currAmount FROM accounts WHERE userID = {self.userID}"):
            return
        while sumTotalQuery.next():
            amounts.append(Decimal(sumTotalQuery.value(0)).quantize(self.fractional, ROUND_HALF_UP))
        print(amounts)
        sumTotalQuery.finish()

        if self.thread.isRunning():
            return
        self.worker = Worker(self.bottomLeftTransactionsAmountValue, self.currency, currencyRates, currencies, amounts, self.rates, self.currencyCode, self.fractional)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.start()


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, widget, currency, currencyRates, currencies, amounts, rates, currencyCode, fractional):
        super().__init__()
        self.widget = widget
        self.currency = currency
        self.currencyRates = currencyRates
        self.currencies = currencies
        self.amounts = amounts
        self.rates = rates
        self.currencyCode = currencyCode
        self.fractional = fractional

    def run(self):
        totalAmount = 0
        start = time.time()
        for key in self.currencyRates.keys():
            rate = Decimal(self.rates.get_rate(key, self.currencyCode))
            self.currencyRates[key] = rate
        end = time.time()
        print("Time of execution: " + str(end-start) + " seconds.")
        for i in range(len(self.amounts)):
            if self.currencies[i] != self.currencyCode:
                amount = Decimal(self.amounts[i] * self.currencyRates[self.currencies[i]]).quantize(self.fractional, ROUND_HALF_UP)
            else:
                amount = Decimal(self.amounts[i]).quantize(self.fractional, ROUND_HALF_UP)
            totalAmount += amount
        self.widget.setText(str(totalAmount) + ' ' + self.currency)
        self.finished.emit()
