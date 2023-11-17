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


class FillTablesFunctions:

    def __init__(self):
        super().__init__()

    def fillTransactionTable(self, filtersEx=None, filtersIn=None):
        tableModelExpeneses = QSqlRelationalTableModel()
        tableModelExpeneses.setTable("expenses")
        if filtersEx:
            tableModelExpeneses.setFilter(filtersEx)
        else:
            tableModelExpeneses.setFilter(f"expenses.userID = {self.userID}")
        tableModelExpeneses.setSort(3, Qt.SortOrder.DescendingOrder)
        tableModelExpeneses.setRelation(1, QSqlRelation("categories", "categoryID", "name"))
        tableModelExpeneses.setRelation(2, QSqlRelation("accounts", "accountID", "name"))
        tableModelExpeneses.setHeaderData(0, Qt.Orientation.Horizontal, "Amount")
        tableModelExpeneses.setHeaderData(1, Qt.Orientation.Horizontal, "Category")
        tableModelExpeneses.setHeaderData(2, Qt.Orientation.Horizontal, "Account")
        tableModelExpeneses.setHeaderData(3, Qt.Orientation.Horizontal, "Date")
        tableModelExpeneses.setHeaderData(4, Qt.Orientation.Horizontal, "Notes")
        tableModelExpeneses.select()
        self.rightTransactionsTableExpenses.setModel(tableModelExpeneses)
        self.rightTransactionsTableExpenses.setColumnWidth(1, 140)
        self.rightTransactionsTableExpenses.setColumnWidth(2, 140)
        self.rightTransactionsTableExpenses.setColumnHidden(5, True)
        self.rightTransactionsTableExpenses.setColumnHidden(6, True)
        self.rightTransactionsTableExpenses.setColumnHidden(7, True)
        self.rightTransactionsTableExpenses.setColumnHidden(8, True)
        self.rightTransactionsTableExpenses.setColumnHidden(9, True)

        tableModelIncome = QSqlRelationalTableModel()
        tableModelIncome.setTable("income")
        if filtersIn:
            tableModelIncome.setFilter(filtersIn)
        else:
            tableModelIncome.setFilter(f"income.userID = {self.userID}")
        tableModelIncome.setSort(3, Qt.SortOrder.DescendingOrder)
        tableModelIncome.setRelation(1, QSqlRelation("categories", "categoryID", "name"))
        tableModelIncome.setRelation(2, QSqlRelation("accounts", "accountID", "name"))
        tableModelIncome.setHeaderData(0, Qt.Orientation.Horizontal, "Amount")
        tableModelIncome.setHeaderData(1, Qt.Orientation.Horizontal, "Category")
        tableModelIncome.setHeaderData(2, Qt.Orientation.Horizontal, "Account")
        tableModelIncome.setHeaderData(3, Qt.Orientation.Horizontal, "Date")
        tableModelIncome.setHeaderData(4, Qt.Orientation.Horizontal, "Notes")
        tableModelIncome.select()
        self.rightTransactionsTableIncome.setModel(tableModelIncome)
        self.rightTransactionsTableIncome.setColumnWidth(1, 150)
        self.rightTransactionsTableIncome.setColumnWidth(2, 150)
        self.rightTransactionsTableIncome.setColumnHidden(5, True)
        self.rightTransactionsTableIncome.setColumnHidden(6, True)
        self.rightTransactionsTableIncome.setColumnHidden(7, True)
        self.rightTransactionsTableIncome.setColumnHidden(8, True)
        self.rightTransactionsTableIncome.setColumnHidden(9, True)

    def fillAccountsTable(self):
        tableModelAccounts = QSqlTableModel()
        tableModelAccounts.setTable("accounts")
        tableModelAccounts.setFilter(f"userID = {self.userID}")
        tableModelAccounts.setSort(5, Qt.SortOrder.AscendingOrder)
        tableModelAccounts.setHeaderData(0, Qt.Orientation.Horizontal, "Name")
        tableModelAccounts.setHeaderData(1, Qt.Orientation.Horizontal, "Currency")
        tableModelAccounts.setHeaderData(2, Qt.Orientation.Horizontal, "Balance")
        tableModelAccounts.setHeaderData(4, Qt.Orientation.Horizontal, "Notes")
        tableModelAccounts.select()
        self.rightAccountsPanelTable.setModel(tableModelAccounts)
        self.rightAccountsPanelTable.resizeColumnsToContents()
        self.rightAccountsPanelTable.setColumnWidth(0, 150)
        self.rightAccountsPanelTable.setColumnHidden(3, True)
        self.rightAccountsPanelTable.setColumnHidden(5, True)
        self.rightAccountsPanelTable.setColumnHidden(6, True)
        self.rightAccountsPanelTable.setColumnHidden(7, True)
        self.rightAccountsPanelTable.setColumnHidden(8, True)

    def fillBudgetsTable(self):
        tableModelBudgets = QSqlRelationalTableModel()
        tableModelBudgets.setTable("Budgets")
        tableModelBudgets.setFilter(f"budgets.userID = {self.userID}")
        tableModelBudgets.setHeaderData(0, Qt.Orientation.Horizontal, "Name")
        tableModelBudgets.setHeaderData(3, Qt.Orientation.Horizontal, "Type")
        tableModelBudgets.setHeaderData(5, Qt.Orientation.Horizontal, "Notes")
        tableModelBudgets.select()
        self.bottomLeftBudgetsPanelTable.setModel(tableModelBudgets)
        self.bottomLeftBudgetsPanelTable.setColumnHidden(1, True)
        self.bottomLeftBudgetsPanelTable.setColumnHidden(2, True)
        self.bottomLeftBudgetsPanelTable.setColumnHidden(4, True)
        self.bottomLeftBudgetsPanelTable.setColumnHidden(6, True)
        self.bottomLeftBudgetsPanelTable.setColumnHidden(7, True)
        self.bottomLeftBudgetsPanelTable.setColumnHidden(8, True)
        self.bottomLeftBudgetsPanelTable.resizeRowsToContents()

    def fillTransfersTable(self):
        tableModelTransfers = QSqlRelationalTableModel()
        tableModelTransfers.setTable("transfers")
        tableModelTransfers.setFilter(f"transfers.userID = {self.userID}")
        tableModelTransfers.setRelation(1, QSqlRelation("accounts", "accountID", "name"))
        tableModelTransfers.setRelation(2, QSqlRelation("accounts", "accountID", "name"))
        tableModelTransfers.setHeaderData(0, Qt.Orientation.Horizontal, "Amount")
        tableModelTransfers.setHeaderData(1, Qt.Orientation.Horizontal, "From")
        tableModelTransfers.setHeaderData(2, Qt.Orientation.Horizontal, "To")
        tableModelTransfers.setHeaderData(3, Qt.Orientation.Horizontal, "Date")
        tableModelTransfers.setHeaderData(4, Qt.Orientation.Horizontal, "Notes")
        tableModelTransfers.select()
        self.bottomRightAccountsPanelTable.setModel(tableModelTransfers)
        self.bottomRightAccountsPanelTable.setColumnWidth(1, 150)
        self.bottomRightAccountsPanelTable.setColumnWidth(2, 150)
        self.bottomRightAccountsPanelTable.setColumnHidden(5, True)
        self.bottomRightAccountsPanelTable.setColumnHidden(6, True)
        self.bottomRightAccountsPanelTable.setColumnHidden(7, True)
        self.bottomRightAccountsPanelTable.setColumnHidden(8, True)
        self.bottomRightAccountsPanelTable.setColumnHidden(9, True)

    def fillJobsTable(self):
        tableModelJobs = QSqlRelationalTableModel()
        tableModelJobs.setTable("jobs")
        tableModelJobs.setFilter(f"jobs.userID = {self.userID}")
        tableModelJobs.setRelation(5, QSqlRelation("accounts", "accountID", "name"))
        tableModelJobs.setHeaderData(0, Qt.Orientation.Horizontal, "Name")
        tableModelJobs.setHeaderData(1, Qt.Orientation.Horizontal, "Status")
        tableModelJobs.setHeaderData(2, Qt.Orientation.Horizontal, "Type")
        tableModelJobs.setHeaderData(3, Qt.Orientation.Horizontal, "Amount")
        tableModelJobs.setHeaderData(5, Qt.Orientation.Horizontal, "Account")
        tableModelJobs.setHeaderData(7, Qt.Orientation.Horizontal, "Schedule")
        tableModelJobs.setHeaderData(8, Qt.Orientation.Horizontal, "Frequency")
        tableModelJobs.setHeaderData(9, Qt.Orientation.Horizontal, "Recurrence")
        tableModelJobs.setHeaderData(12, Qt.Orientation.Horizontal, "Time")
        tableModelJobs.setHeaderData(13, Qt.Orientation.Horizontal, "Start date")
        tableModelJobs.setHeaderData(14, Qt.Orientation.Horizontal, "End date")
        tableModelJobs.select()
        self.scheduledTrTableView.setModel(tableModelJobs)
        self.scheduledTrTableView.setColumnHidden(4, True)
        self.scheduledTrTableView.setColumnHidden(6, True)
        self.scheduledTrTableView.setColumnHidden(10, True)
        self.scheduledTrTableView.setColumnHidden(11, True)
        self.scheduledTrTableView.setColumnHidden(15, True)
        self.scheduledTrTableView.setColumnHidden(16, True)
        self.scheduledTrTableView.setColumnHidden(17, True)
        self.scheduledTrTableView.setColumnHidden(18, True)
        self.scheduledTrTableView.resizeRowsToContents()
