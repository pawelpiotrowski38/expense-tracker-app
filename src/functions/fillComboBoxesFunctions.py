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


class FillComboBoxesFunctions:

    def __init__(self):
        super().__init__()

    def fillCategoriesComboBox(self, widget):
        radioButton = self.sender()
        comboBoxModel = QSqlTableModel()
        comboBoxModel.setTable("categories")
        if radioButton.text() == "Expense":
            comboBoxModel.setFilter(f"categoryType = 'expenses' AND userID = {self.userID}")
            comboBoxModel.setSort(2, Qt.SortOrder.AscendingOrder)
            comboBoxModel.select()
            widget.setModel(comboBoxModel)
            widget.setModelColumn(comboBoxModel.fieldIndex("name"))
        elif radioButton.text() == "Income":
            comboBoxModel.setFilter(f"categoryType = 'income' AND userID = {self.userID}")
            comboBoxModel.setSort(2, Qt.SortOrder.AscendingOrder)
            comboBoxModel.select()
            widget.setModel(comboBoxModel)
            widget.setModelColumn(comboBoxModel.fieldIndex("name"))

    def fillCategoriesComboBoxB(self):
        comboBoxModel = QSqlTableModel()
        comboBoxModel.setTable("categories")
        comboBoxModel.setFilter(f"categoryType = 'expenses' AND userID = {self.userID}")
        comboBoxModel.setSort(2, Qt.SortOrder.AscendingOrder)
        comboBoxModel.select()
        self.topLeftBudgetsCategoryEntry.setModel(comboBoxModel)
        self.topLeftBudgetsCategoryEntry.setModelColumn(comboBoxModel.fieldIndex("name"))

    def fillAccountsComboBox(self):
        comboBoxModel = QSqlTableModel()
        comboBoxModel.setTable("accounts")
        comboBoxModel.setFilter(f"userID = {self.userID}")
        comboBoxModel.setSort(5, Qt.SortOrder.AscendingOrder)
        comboBoxModel.select()
        self.topLeftTransactionsAccountEntry.setModel(comboBoxModel)
        self.topLeftTransactionsAccountEntry.setModelColumn(comboBoxModel.fieldIndex("name"))
        self.rightTransactionsFilterAccountComboBox.setModel(comboBoxModel)
        self.rightTransactionsFilterAccountComboBox.setModelColumn(comboBoxModel.fieldIndex("name"))
        self.bottomLeftAccountsFromEntry.setModel(comboBoxModel)
        self.bottomLeftAccountsFromEntry.setModelColumn(comboBoxModel.fieldIndex("name"))
        self.bottomLeftAccountsToEntry.setModel(comboBoxModel)
        self.bottomLeftAccountsToEntry.setModelColumn(comboBoxModel.fieldIndex("name"))
        self.topLeftReportsAccountEntry.setModel(comboBoxModel)
        self.topLeftReportsAccountEntry.setModelColumn(comboBoxModel.fieldIndex("name"))
        self.bottomLeftReportsAccountEntry.setModel(comboBoxModel)
        self.bottomLeftReportsAccountEntry.setModelColumn(comboBoxModel.fieldIndex("name"))
        self.recurringAccountEntry.setModel(comboBoxModel)
        self.recurringAccountEntry.setModelColumn(comboBoxModel.fieldIndex("name"))
