from PyQt5.QtChart import QChart
from PyQt5.QtCore import Qt, QTimer, QDate, QDateTime, QLocale, QThread
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLabel, QLineEdit, QGridLayout, QPushButton, \
    QVBoxLayout, QHBoxLayout, QStackedLayout, QToolButton, QMenu, QFrame, QCalendarWidget, \
    QAbstractItemView, QTableView, QSplitter, QGroupBox, QScrollArea, QRadioButton, QButtonGroup, QComboBox, \
    QPlainTextEdit, QCheckBox, QSpinBox, QTimeEdit, QDateEdit, QTabWidget, QHeaderView, QStyledItemDelegate, \
    QToolTip
from decimal import Decimal
from forex_python.converter import CurrencyRates, CurrencyCodes
from functools import partial
from dataFunctions import DataFunctions
from functions.accountFunctions import AccountFunctions
from functions.budgetFunctions import BudgetFunctions
from functions.categoryFunctions import CategoryFunctions
from functions.transactionFunctions import TransactionFunctions
from functions.transferFunctions import TransferFunctions
from functions.fillChartsFunctions import FillChartsFunctions
from functions.fillComboBoxesFunctions import FillComboBoxesFunctions
from functions.fillOtherFunctions import FillOtherFunctions
from functions.fillTablesFunctions import FillTablesFunctions
from functions.jobFunctions import JobFunctions
from functions.otherFunctions import OtherFunctions
from functions.clearFunctions import ClearFunctions
from functions.filterFunctions import FilterFunctions
from functions.showChartsFunctions import ShowChartsFunctions
from colorThemes import darkTheme, lightTheme


# noinspection PyAttributeOutsideInit
class MainWindow(
        QWidget,
        AccountFunctions,
        BudgetFunctions,
        CategoryFunctions,
        TransactionFunctions,
        TransferFunctions
        FillChartsFunctions,
        FillComboBoxesFunctions,
        FillOtherFunctions,
        FillTablesFunctions,
        JobFunctions,
        ClearFunctions,
        FilterFunctions
        OtherFunctions,
        ShowChartsFunctions
    ):
    """Klasa reprezentująca okno główne programu"""
    codes = CurrencyCodes()
    rates = CurrencyRates()
    fractional = Decimal("0.01")
    thread = QThread()

    def __init__(self, loginWindow, connection, app, username, userID, currency, theme, fontName, fontSize, defPalette):
        """Konstruktor klasy MainWindow"""
        super().__init__()
        self.loginWindow = loginWindow
        self.con = connection
        self.app = app
        self.login = username
        self.userID = userID
        self.currencyCode = currency
        self.currency = self.codes.get_symbol(self.currencyCode)
        self.theme = theme
        self.fontName = fontName
        self.fontSize = fontSize
        self.defaultPalette = defPalette
        self.fontt = None
        
        if self.theme:
            self.app.setPalette(darkTheme())
        else:
            self.app.setPalette(lightTheme())
        self.initUI()
        self.show()
        self.fillSummaryPanel(self.theme)
        self.fillAmountOwned()
        self.fillDailyCharts(self.theme)
        self.fillTransactionTable()
        self.fillAccountsComboBox()
        self.fillAccountsTable()
        self.fillTransfersTable()
        self.fillBudgetsTable()
        self.fillBudgetsCharts()
        self.fillJobsTable()

    def initUI(self):
        """Metoda tworząca interfejs graficzny okna głównego programu"""
        #--------------------------------------------------------------------------------------
        #-------------------------- POSITION, LAYUOT, SIZE, FONT ------------------------------
        #--------------------------------------------------------------------------------------

        self.setGeometry(0, 0, 1120, 760)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.fontt = self.font()
        self.fontt.setFamily(self.fontName)
        self.fontt.setPointSize(self.fontSize)
        self.fontt.setWeight(60)
        self.window().setFont(self.fontt)

        mainLayout = QVBoxLayout()

        topHorizontalLayout = QHBoxLayout()
        self.topClockLabel = QLabel("")
        self.topClock = QTimer()
        self.topClock.timeout.connect(self.showTime)
        self.topClock.start(100)
        self.topMenuButton = QToolButton()
        self.topMenuButton.setPopupMode(QToolButton.InstantPopup)
        self.topMenuButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        self.topMenuButton.setText(' ' + self.login)
        self.topMenuButton.setIcon(QIcon("icons/accountIcon.png"))
        
        self.topMenu = QMenu()
        topFenuFont = self.topMenu.font()
        topFenuFont.setFamily(self.fontName)
        topFenuFont.setPointSize(self.fontSize)
        self.topMenu.setFont(topFenuFont)

        self.topMenu.addAction(QIcon("icons/refreshIcon.png"), "Refresh", self.refresh)
        self.topMenu.addAction(QIcon("icons/settingsIcon.png"), "Settings", partial(self.settings, self.userID, self.currencyCode, self.con, self.login))
        self.topMenu.addSeparator()
        self.topMenu.addAction(QIcon("icons/logOutIcon.png"), "Log out", self.logout)
        self.topMenu.setLayoutDirection(Qt.RightToLeft)
        self.topMenuButton.setMenu(self.topMenu)
        topHorizontalLayout.addWidget(self.topMenuButton, alignment=Qt.AlignLeft)
        topHorizontalLayout.addWidget(self.topClockLabel, alignment=Qt.AlignRight)

        width = self.frameGeometry().width()
        height = self.frameGeometry().height()

        #--------------------------------------------------------------------------------------
        #------------------------------------ HOME TAB ----------------------------------------
        #--------------------------------------------------------------------------------------

        homeLayout = QHBoxLayout()

        firstHomePanel = QFrame()
        firstHomePanel.setFrameShape(QFrame.StyledPanel)
        firstHomePanelVLayout = QVBoxLayout(firstHomePanel)

        self.firstHomeCalendar = QCalendarWidget()
        firstHomePanelVLayout.addWidget(self.firstHomeCalendar)
        
        secondHomePanel = QFrame()
        secondHomePanel.setFrameShape(QFrame.StyledPanel)
        secondHomePanelMainLayout = QVBoxLayout(secondHomePanel)

        self.secondHomeMainLabel = QLabel('Summary')

        self.secondHomeLabel1 = QLabel('month year')
        self.secondHomeChart1 = QChart()
        self.secondHomeLabel11 = QLabel('Income:')
        self.secondHomeLabel12 = QLabel('')
        self.secondHomeLabel13 = QLabel('Expenses:')
        self.secondHomeLabel14 = QLabel('')
        self.secondHomeLabel15 = QLabel('Total:')
        self.secondHomeLabel16 = QLabel('')

        self.hLine1 = QFrame()
        self.hLine1.setFrameShape(QFrame.HLine)
        self.hLine1.setFrameShadow(QFrame.Sunken)

        self.secondHomeLabel2 = QLabel('month year')
        self.secondHomeChart2 = QChart()
        self.secondHomeLabel21 = QLabel('Income:')
        self.secondHomeLabel22 = QLabel('')
        self.secondHomeLabel23 = QLabel('Expenses:')
        self.secondHomeLabel24 = QLabel('')
        self.secondHomeLabel25 = QLabel('Total:')
        self.secondHomeLabel26 = QLabel('')

        self.hLine2 = QFrame()
        self.hLine2.setFrameShape(QFrame.HLine)
        self.hLine2.setFrameShadow(QFrame.Sunken)

        self.secondHomeLabel3 = QLabel('month year')
        self.secondHomeChart3 = QChart()
        self.secondHomeLabel31 = QLabel('Income:')
        self.secondHomeLabel32 = QLabel('')
        self.secondHomeLabel33 = QLabel('Expenses:')
        self.secondHomeLabel34 = QLabel('')
        self.secondHomeLabel35 = QLabel('Total:')
        self.secondHomeLabel36 = QLabel('')

        self.hLine3 = QFrame()
        self.hLine3.setFrameShape(QFrame.HLine)
        self.hLine3.setFrameShadow(QFrame.Sunken)

        self.secondHomeLabel4 = QLabel('month year')
        self.secondHomeChart4 = QChart()
        self.secondHomeLabel41 = QLabel('Income:')
        self.secondHomeLabel42 = QLabel('')
        self.secondHomeLabel43 = QLabel('Expenses:')
        self.secondHomeLabel44 = QLabel('')
        self.secondHomeLabel45 = QLabel('Total:')
        self.secondHomeLabel46 = QLabel('')

        self.chartsList = [self.secondHomeChart1, self.secondHomeChart2, self.secondHomeChart3, self.secondHomeChart4]

        self.secondHomePanelGridLayout1 = QGridLayout()
        self.secondHomePanelGridLayout1.setRowMinimumHeight(1, 150)
        self.secondHomePanelGridLayout1.setColumnMinimumWidth(0, 150)
        self.secondHomePanelGridLayout1.setHorizontalSpacing(20)
        
        self.secondHomePanelGridLayout2 = QGridLayout()
        self.secondHomePanelGridLayout2.setRowMinimumHeight(1, 150)
        self.secondHomePanelGridLayout2.setColumnMinimumWidth(0, 150)
        self.secondHomePanelGridLayout2.setHorizontalSpacing(20)
        
        self.secondHomePanelGridLayout3 = QGridLayout()
        self.secondHomePanelGridLayout3.setRowMinimumHeight(1, 150)
        self.secondHomePanelGridLayout3.setColumnMinimumWidth(0, 150)
        self.secondHomePanelGridLayout3.setHorizontalSpacing(20)
        
        self.secondHomePanelGridLayout4 = QGridLayout()
        self.secondHomePanelGridLayout4.setRowMinimumHeight(1, 150)
        self.secondHomePanelGridLayout4.setColumnMinimumWidth(0, 150)
        self.secondHomePanelGridLayout4.setHorizontalSpacing(20)

        grid1 = QGridLayout()
        grid2 = QGridLayout()
        grid3 = QGridLayout()
        grid4 = QGridLayout()

        grid1.setColumnMinimumWidth(0, 100)
        grid1.setColumnMinimumWidth(1, 100)
        grid2.setColumnMinimumWidth(0, 100)
        grid2.setColumnMinimumWidth(1, 100)
        grid3.setColumnMinimumWidth(0, 100)
        grid3.setColumnMinimumWidth(1, 100)
        grid4.setColumnMinimumWidth(0, 100)
        grid4.setColumnMinimumWidth(1, 100)

        grid1.addWidget(self.secondHomeLabel11, 0, 0)
        grid1.addWidget(self.secondHomeLabel12, 0, 1)
        grid1.addWidget(self.secondHomeLabel13, 1, 0)
        grid1.addWidget(self.secondHomeLabel14, 1, 1)
        grid1.addWidget(self.secondHomeLabel15, 2, 0)
        grid1.addWidget(self.secondHomeLabel16, 2, 1)
        
        grid2.addWidget(self.secondHomeLabel21, 0, 0)
        grid2.addWidget(self.secondHomeLabel22, 0, 1)
        grid2.addWidget(self.secondHomeLabel23, 1, 0)
        grid2.addWidget(self.secondHomeLabel24, 1, 1)
        grid2.addWidget(self.secondHomeLabel25, 2, 0)
        grid2.addWidget(self.secondHomeLabel26, 2, 1)
        
        grid3.addWidget(self.secondHomeLabel31, 0, 0)
        grid3.addWidget(self.secondHomeLabel32, 0, 1)
        grid3.addWidget(self.secondHomeLabel33, 1, 0)
        grid3.addWidget(self.secondHomeLabel34, 1, 1)
        grid3.addWidget(self.secondHomeLabel35, 2, 0)
        grid3.addWidget(self.secondHomeLabel36, 2, 1)
        
        grid4.addWidget(self.secondHomeLabel41, 0, 0)
        grid4.addWidget(self.secondHomeLabel42, 0, 1)
        grid4.addWidget(self.secondHomeLabel43, 1, 0)
        grid4.addWidget(self.secondHomeLabel44, 1, 1)
        grid4.addWidget(self.secondHomeLabel45, 2, 0)
        grid4.addWidget(self.secondHomeLabel46, 2, 1)

        self.secondHomePanelGridLayout1.addWidget(self.secondHomeLabel1, 0, 0)
        self.secondHomePanelGridLayout1.addLayout(grid1, 1, 1)

        self.secondHomePanelGridLayout2.addWidget(self.secondHomeLabel2, 0, 0)
        self.secondHomePanelGridLayout2.addLayout(grid2, 1, 1)

        self.secondHomePanelGridLayout3.addWidget(self.secondHomeLabel3, 0, 0)
        self.secondHomePanelGridLayout3.addLayout(grid3, 1, 1)

        self.secondHomePanelGridLayout4.addWidget(self.secondHomeLabel4, 0, 0)
        self.secondHomePanelGridLayout4.addLayout(grid4, 1, 1)

        secondHomePanelMainLayout.addWidget(self.secondHomeMainLabel, alignment=Qt.AlignCenter)
        secondHomePanelMainLayout.addLayout(self.secondHomePanelGridLayout1)
        secondHomePanelMainLayout.addWidget(self.hLine1)
        secondHomePanelMainLayout.addLayout(self.secondHomePanelGridLayout2)
        secondHomePanelMainLayout.addWidget(self.hLine2)
        secondHomePanelMainLayout.addLayout(self.secondHomePanelGridLayout3)
        secondHomePanelMainLayout.addWidget(self.hLine3)
        secondHomePanelMainLayout.addLayout(self.secondHomePanelGridLayout4)

        thirdHomePanel = QFrame()
        thirdHomePanel.setFrameShape(QFrame.StyledPanel)
        self.thirdHomePanelMainLayout = QVBoxLayout(thirdHomePanel)

        self.thirdHomeChart = QChart()
        
        fourthHomePanel = QFrame()
        fourthHomePanel.setFrameShape(QFrame.StyledPanel)
        self.fourthHomePanelMainLayout = QVBoxLayout(fourthHomePanel)

        self.fourthHomeChart = QChart()

        self.areDailyChartsShown = False

        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(thirdHomePanel)
        splitter1.addWidget(fourthHomePanel)
        splitter1.setSizes([int(width*0.5), int(width*0.5)])

        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(secondHomePanel)
        splitter2.addWidget(splitter1)
        splitter2.setSizes([int(width*0.3), int(width*0.7)])

        splitter3 = QSplitter(Qt.Vertical)
        splitter3.setContentsMargins(10, 10, 10, 10)
        splitter3.addWidget(firstHomePanel)
        splitter3.addWidget(splitter2)

        homeLayout.addWidget(splitter3)

        homeScroll = QScrollArea()
        homeScroll.setWidget(splitter3)
        homeScroll.setWidgetResizable(True)

        #--------------------------------------------------------------------------------------
        #------------------------------- TRANSACTIONS TAB -------------------------------------
        #--------------------------------------------------------------------------------------

        transactionsLayout = QHBoxLayout()
        
        self.topLeftTransactionsTypeLabel = QLabel("Type:")
        self.topLeftTransactionsExpenseRadioButton = QRadioButton("Expense")
        self.topLeftTransactionsIncomeRadioButton = QRadioButton("Income")
        self.topLeftTransactionsTrType = QButtonGroup()
        self.topLeftTransactionsTrType.addButton(self.topLeftTransactionsExpenseRadioButton)
        self.topLeftTransactionsTrType.addButton(self.topLeftTransactionsIncomeRadioButton)
        self.topLeftTransactionsValueLabel = QLabel("Amount:")
        self.topLeftTransactionsCategoryLabel = QLabel("Category:")
        self.topLeftTransactionsAccountLabel = QLabel("Account:")
        self.topLeftTransactionsDateLabel = QLabel("Date:")
        self.topLeftTransactionsNotesLabel = QLabel("Notes (optional):")
        self.topLeftTransactionsNotesLabel.setWordWrap(True)
        self.topLeftTransactionsValueEntry = QLineEdit()
        self.topLeftTransactionsValueEntry.setMaxLength(15)
        self.topLeftTransactionsCategoryEntry = QComboBox()
        self.topLeftTransactionsCalcButton = QPushButton()
        self.topLeftTransactionsCalcButton.setFixedWidth(30)
        self.topLeftTransactionsCalcButton.setIcon(QIcon('icons/calc.png'))
        self.topLeftTransactionsCalcButton.setToolTip("Calculator")
        self.topLeftTransactionsCalcButton.clicked.connect(partial(self.calculator, self.userID))
        self.topLeftTransactionsSymbolLabel = QLabel("")
        self.topLeftTransactionsEditCatButton = QPushButton()
        self.topLeftTransactionsEditCatButton.setFixedWidth(30)
        self.topLeftTransactionsEditCatButton.setIcon(QIcon('icons/editCategories.png'))
        self.topLeftTransactionsEditCatButton.setToolTip("Edit categories")
        self.topLeftTransactionsEditCatButton.clicked.connect(partial(self.editCategories, self.userID))
        editCatHLayout = QHBoxLayout()
        editCatHLayout.addWidget(self.topLeftTransactionsEditCatButton)
        editCatHLayout.addWidget(self.topLeftTransactionsCategoryEntry)
        editCatHLayout.setSpacing(5)
        calcHLayout = QHBoxLayout()
        calcHLayout.addWidget(self.topLeftTransactionsCalcButton)
        calcHLayout.addWidget(self.topLeftTransactionsValueEntry)
        calcHLayout.addWidget(self.topLeftTransactionsSymbolLabel)
        calcHLayout.setSpacing(5)
        self.topLeftTransactionsAccountEntry = QComboBox()
        self.topLeftTransactionsAccountEntry.currentTextChanged.connect(lambda: self.changeCurrencySymbol(self.topLeftTransactionsAccountEntry.currentText(), self.topLeftTransactionsSymbolLabel))
        self.topLeftTransactionsDateEntry = QDateEdit()
        self.topLeftTransactionsDateEntry.setCalendarPopup(True)
        self.topLeftTransactionsDateEntry.setDate(QDate.currentDate())
        self.topLeftTransactionsDateEntry.setMaximumDate(QDate.currentDate())
        self.topLeftTransactionsNotesEntry = QPlainTextEdit()
        self.topLeftTransactionsClearButton = QPushButton("Clear")
        self.topLeftTransactionsClearButton.clicked.connect(self.clearTransactionInfo)
        self.topLeftTransactionsAddButton = QPushButton("Add transaction")
        self.topLeftTransactionsAddButton.clicked.connect(self.addTransaction)
        self.topLeftTransactionsImportButton = QPushButton("Import transactions")
        self.topLeftTransactionsImportButton.clicked.connect(partial(self.importTransactions, self.userID, self.currencyCode, self.con))
        self.topLeftTransactionsExportButton = QPushButton("Export transactions")
        self.topLeftTransactionsExportButton.clicked.connect(self.exportTransactions)
        self.topLeftTransactionsExpenseRadioButton.toggled.connect(lambda: self.fillCategoriesComboBox(self.topLeftTransactionsCategoryEntry))
        self.topLeftTransactionsIncomeRadioButton.toggled.connect(lambda: self.fillCategoriesComboBox(self.topLeftTransactionsCategoryEntry))

        topLeftTransactionsPanel = QFrame()
        topLeftTransactionsPanel.setFrameShape(QFrame.StyledPanel)
        
        topLeftTransactionsPanelVLayout = QVBoxLayout(topLeftTransactionsPanel)
        topLeftTransactionsPanelHLayout = QHBoxLayout()
        topLeftTransactionsPanelGrid = QGridLayout()

        topLeftTransactionsPanelHLayout.addWidget(self.topLeftTransactionsExpenseRadioButton, alignment=Qt.AlignCenter)
        topLeftTransactionsPanelHLayout.addWidget(self.topLeftTransactionsIncomeRadioButton, alignment=Qt.AlignCenter)
        topLeftTransactionsPanelGrid.addWidget(self.topLeftTransactionsTypeLabel, 0, 0)
        topLeftTransactionsPanelGrid.addLayout(topLeftTransactionsPanelHLayout, 0, 1)
        topLeftTransactionsPanelGrid.addWidget(self.topLeftTransactionsValueLabel, 1, 0)
        topLeftTransactionsPanelGrid.addLayout(calcHLayout, 1, 1)
        topLeftTransactionsPanelGrid.addWidget(self.topLeftTransactionsCategoryLabel, 2, 0)
        topLeftTransactionsPanelGrid.addLayout(editCatHLayout, 2, 1)
        topLeftTransactionsPanelGrid.addWidget(self.topLeftTransactionsAccountLabel, 3, 0)
        topLeftTransactionsPanelGrid.addWidget(self.topLeftTransactionsAccountEntry, 3, 1)
        topLeftTransactionsPanelGrid.addWidget(self.topLeftTransactionsDateLabel, 4, 0)
        topLeftTransactionsPanelGrid.addWidget(self.topLeftTransactionsDateEntry, 4, 1)
        topLeftTransactionsPanelGrid.addWidget(self.topLeftTransactionsNotesLabel, 5, 0)
        topLeftTransactionsPanelGrid.addWidget(self.topLeftTransactionsNotesEntry, 5, 1)
        topLeftTransactionsPanelGrid.addWidget(self.topLeftTransactionsClearButton, 6, 0)
        topLeftTransactionsPanelGrid.addWidget(self.topLeftTransactionsAddButton, 6, 1)
        topLeftTransactionsPanelGrid.setVerticalSpacing(10)

        topLeftTransactionsPanelVLayout.addLayout(topLeftTransactionsPanelHLayout)
        topLeftTransactionsPanelVLayout.addLayout(topLeftTransactionsPanelGrid)
        topLeftTransactionsPanelVLayout.addWidget(self.topLeftTransactionsImportButton)
        topLeftTransactionsPanelVLayout.addWidget(self.topLeftTransactionsExportButton)

        #--------------------------------------------------------------------------------------
        
        bottomLeftTransactionsPanel = QFrame()
        bottomLeftTransactionsPanel.setFrameShape(QFrame.StyledPanel)
        bottomLeftTransactionsPanelGrid = QGridLayout(bottomLeftTransactionsPanel)

        self.bottomLeftTransactionsLine = QFrame()
        self.bottomLeftTransactionsLine.setFrameShape(QFrame.HLine)
        self.bottomLeftTransactionsLine.setFrameShadow(QFrame.Sunken)

        self.bottomLeftTransactionsAmountLabel = QLabel("Total amount owned:")
        self.bottomLeftTransactionsAmountLabel.setWordWrap(True)
        self.bottomLeftTransactionsAmountValue = QLabel()
        self.bottomLeftTransactionsIncomeLabel = QLabel("Total income:")
        self.bottomLeftTransactionsIncomeValue = QLabel()
        self.bottomLeftTransactionsExpenseLabel = QLabel("Total expenses:")
        self.bottomLeftTransactionsExpensesValue = QLabel()
        self.bottomLeftTransactionsTotalLabel = QLabel("Balance:")
        self.bottomLeftTransactionsTotalValue = QLabel()

        bottomLeftTransactionsPanelGrid.addWidget(self.bottomLeftTransactionsAmountLabel, 0, 0)
        bottomLeftTransactionsPanelGrid.addWidget(self.bottomLeftTransactionsAmountValue, 0, 1)
        bottomLeftTransactionsPanelGrid.addWidget(self.bottomLeftTransactionsLine, 1, 0, 1, 2)
        bottomLeftTransactionsPanelGrid.addWidget(self.bottomLeftTransactionsIncomeLabel, 2, 0)
        bottomLeftTransactionsPanelGrid.addWidget(self.bottomLeftTransactionsIncomeValue, 2, 1)
        bottomLeftTransactionsPanelGrid.addWidget(self.bottomLeftTransactionsExpenseLabel, 3, 0)
        bottomLeftTransactionsPanelGrid.addWidget(self.bottomLeftTransactionsExpensesValue, 3, 1)
        bottomLeftTransactionsPanelGrid.addWidget(self.bottomLeftTransactionsTotalLabel, 4, 0)
        bottomLeftTransactionsPanelGrid.addWidget(self.bottomLeftTransactionsTotalValue, 4, 1)

        #--------------------------------------------------------------------------------------
        
        rightTransactionsPanel = QFrame()      
        rightTransactionsPanel.setFrameShape(QFrame.StyledPanel)
        rightTransactionsPanelVLayout = QVBoxLayout(rightTransactionsPanel)

        self.rightTransactionsFilterButton = QPushButton("Filters")
        self.rightTransactionsFilterButton.clicked.connect(self.showFilters)

        self.filtersGroupBox = QGroupBox()
        
        self.rightTransactionsExpenseRadioButton = QRadioButton("Expense")
        self.rightTransactionsIncomeRadioButton = QRadioButton("Income")
        self.rightTransactionsFiltersCloseButton = QPushButton("Close")
        self.rightTransactionsFiltersCloseButton.clicked.connect(self.hideFilters)
        self.filtersTrType = QButtonGroup()
        self.filtersTrType.addButton(self.rightTransactionsExpenseRadioButton)
        self.filtersTrType.addButton(self.rightTransactionsIncomeRadioButton)
        self.rightTransactionsExpenseRadioButton.toggled.connect(lambda: self.fillCategoriesComboBox(self.rightTransactionsFilterCategoryComboBox))
        self.rightTransactionsIncomeRadioButton.toggled.connect(lambda: self.fillCategoriesComboBox(self.rightTransactionsFilterCategoryComboBox))
        self.rightTransactionsFilterAmountCheckbox = QCheckBox("Amount")
        self.rightTransactionsFilterAmountCheckbox.stateChanged.connect(lambda: self.grayOutFilters(self.rightTransactionsFilterAmountCheckbox.checkState(), self.rightTransactionsFilterAmountFromLabel, self.rightTransactionsFilterAmountToLabel, self.rightTransactionsFilterAmountFromEntry, self.rightTransactionsFilterAmountToEntry))
        self.rightTransactionsFilterAmountFromLabel = QLabel("From:")
        self.rightTransactionsFilterAmountFromLabel.setDisabled(True)
        self.rightTransactionsFilterAmountToLabel = QLabel("To:")
        self.rightTransactionsFilterAmountToLabel.setDisabled(True)
        self.rightTransactionsFilterAmountFromEntry = QLineEdit()
        self.rightTransactionsFilterAmountFromEntry.setMaxLength(15)
        self.rightTransactionsFilterAmountFromEntry.setDisabled(True)
        self.rightTransactionsFilterAmountToEntry = QLineEdit()
        self.rightTransactionsFilterAmountToEntry.setMaxLength(15)
        self.rightTransactionsFilterAmountToEntry.setDisabled(True)
        self.rightTransactionsFilterCategoryCheckbox = QCheckBox("Category")
        self.rightTransactionsFilterCategoryCheckbox.stateChanged.connect(lambda: self.grayOutFilters(self.rightTransactionsFilterCategoryCheckbox.checkState(), self.rightTransactionsFilterCategoryComboBox))
        self.rightTransactionsFilterCategoryComboBox = QComboBox()
        self.rightTransactionsFilterCategoryComboBox.setDisabled(True)
        self.rightTransactionsFilterAccountCheckbox = QCheckBox("Account")
        self.rightTransactionsFilterAccountCheckbox.stateChanged.connect(lambda: self.grayOutFilters(self.rightTransactionsFilterAccountCheckbox.checkState(), self.rightTransactionsFilterAccountComboBox))
        self.rightTransactionsFilterAccountComboBox = QComboBox()
        self.rightTransactionsFilterAccountComboBox.setDisabled(True)
        self.rightTransactionsFilterDateCheckbox = QCheckBox("Date")
        self.rightTransactionsFilterDateCheckbox.stateChanged.connect(lambda: self.grayOutFilters(self.rightTransactionsFilterDateCheckbox.checkState(), self.rightTransactionsFilterDateFromLabel, self.rightTransactionsFilterDateToLabel, self.rightTransactionsFilterDateFromEntry, self.rightTransactionsFilterDateToEntry))
        self.rightTransactionsFilterDateFromLabel = QLabel("From:")
        self.rightTransactionsFilterDateFromLabel.setDisabled(True)
        self.rightTransactionsFilterDateToLabel = QLabel("To:")
        self.rightTransactionsFilterDateToLabel.setDisabled(True)
        self.rightTransactionsFilterDateFromEntry = QDateEdit()
        self.rightTransactionsFilterDateFromEntry.setCalendarPopup(True)
        self.rightTransactionsFilterDateFromEntry.setDateTime(QDateTime.currentDateTime())
        self.rightTransactionsFilterDateFromEntry.setDisabled(True)
        self.rightTransactionsFilterDateToEntry = QDateEdit()
        self.rightTransactionsFilterDateToEntry.setCalendarPopup(True)
        self.rightTransactionsFilterDateToEntry.setDateTime(QDateTime.currentDateTime())
        self.rightTransactionsFilterDateToEntry.setDisabled(True)
        self.rightTransactionsFilterRemoveButton = QPushButton("Remove filters")
        self.rightTransactionsFilterRemoveButton.clicked.connect(self.removeFilters)
        self.rightTransactionsFilterClearButton = QPushButton("Clear")
        self.rightTransactionsFilterClearButton.clicked.connect(self.clearFilters)
        self.rightTransactionsFilterSetButton = QPushButton("Set filters")
        self.rightTransactionsFilterSetButton.clicked.connect(self.filterTransactions)

        rightTransactionsFilterHLayout = QHBoxLayout()
        rightTransactionsFilterHLayout.addWidget(self.rightTransactionsExpenseRadioButton, alignment=Qt.AlignLeft)
        rightTransactionsFilterHLayout.addWidget(self.rightTransactionsIncomeRadioButton, alignment=Qt.AlignLeft)
        rightTransactionsFilterHLayout.addWidget(self.rightTransactionsFiltersCloseButton, alignment=Qt.AlignRight)

        rightTransactionsFilterGridLayout = QGridLayout()
        rightTransactionsFilterGridLayout.setHorizontalSpacing(20)
        rightTransactionsFilterGridLayout.addLayout(rightTransactionsFilterHLayout, 0, 0, 1, 5)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterAmountCheckbox, 1, 0)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterAmountFromLabel, 1, 1)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterAmountFromEntry, 1, 2)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterAmountToLabel, 1, 3)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterAmountToEntry, 1, 4)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterCategoryCheckbox, 2, 0)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterCategoryComboBox, 2, 1, 1, 2)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterAccountCheckbox, 3, 0)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterAccountComboBox, 3, 1, 1, 2)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterDateCheckbox, 4, 0)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterDateFromLabel, 4, 1)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterDateFromEntry, 4, 2)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterDateToLabel, 4, 3)
        rightTransactionsFilterGridLayout.addWidget(self.rightTransactionsFilterDateToEntry, 4, 4)
        rightTransactionsFilterButtonsLayout = QHBoxLayout()
        rightTransactionsFilterButtonsLayout.addWidget(self.rightTransactionsFilterRemoveButton)
        rightTransactionsFilterButtonsLayout.addWidget(self.rightTransactionsFilterClearButton)
        rightTransactionsFilterButtonsLayout.addWidget(self.rightTransactionsFilterSetButton)

        filtersLayout = QVBoxLayout()
        filtersLayout.addLayout(rightTransactionsFilterGridLayout)
        filtersLayout.insertSpacing(1, 20)
        filtersLayout.addLayout(rightTransactionsFilterButtonsLayout)

        self.filtersGroupBox.setLayout(filtersLayout)
        self.filtersGroupBox.setVisible(False)
       
        self.rightTransactionsTabs = QTabWidget()
        self.rightTransactionsTabExpenses = QWidget()
        self.rightTransactionsTabIncome = QWidget()
        self.rightTransactionsTabs.addTab(self.rightTransactionsTabExpenses, "Expenses")
        self.rightTransactionsTabs.addTab(self.rightTransactionsTabIncome, "Income")
        
        self.rightTransactionsTabExpenses.layout = QVBoxLayout()
        self.rightTransactionsTabExpenses.setLayout(self.rightTransactionsTabExpenses.layout)
        self.rightTransactionsTabIncome.layout = QVBoxLayout()
        self.rightTransactionsTabIncome.setLayout(self.rightTransactionsTabIncome.layout)
        
        self.rightTransactionsTableExpenses = QTableView()
        self.rightTransactionsTableExpenses.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rightTransactionsTableExpenses.verticalHeader().setVisible(False)
        self.rightTransactionsTableExpenses.horizontalHeader().setStretchLastSection(True)
        self.rightTransactionsTableExpenses.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.rightTransactionsTableIncome = QTableView()
        self.rightTransactionsTableIncome.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rightTransactionsTableIncome.verticalHeader().setVisible(False)
        self.rightTransactionsTableIncome.horizontalHeader().setStretchLastSection(True)
        self.rightTransactionsTableIncome.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.rightTransactionsTabExpenses.layout.addWidget(self.rightTransactionsTableExpenses)
        self.rightTransactionsTabIncome.layout.addWidget(self.rightTransactionsTableIncome)
        
        rightTransactionsPanelVLayout.addWidget(self.rightTransactionsFilterButton, alignment=Qt.AlignRight)
        rightTransactionsPanelVLayout.addWidget(self.filtersGroupBox)
        rightTransactionsPanelVLayout.addWidget(self.rightTransactionsTabs)

        rightTransactionsEditDeleteHLayout = QHBoxLayout()
        self.rightTransactionsDeleteButton = QPushButton("Delete transaction")
        self.rightTransactionsEditButton = QPushButton("Edit transaction")
        self.rightTransactionsDeleteButton.clicked.connect(self.deleteTransaction)
        self.rightTransactionsEditButton.clicked.connect(self.editTransaction)
        rightTransactionsEditDeleteHLayout.addWidget(self.rightTransactionsEditButton, alignment=Qt.AlignLeft)
        rightTransactionsEditDeleteHLayout.addWidget(self.rightTransactionsDeleteButton, alignment=Qt.AlignRight)
        rightTransactionsPanelVLayout.addLayout(rightTransactionsEditDeleteHLayout)
        
        #--------------------------------------------------------------------------------------

        verticalSplitter = QSplitter(Qt.Vertical)
        verticalSplitter.addWidget(topLeftTransactionsPanel)
        verticalSplitter.addWidget(bottomLeftTransactionsPanel)
        verticalSplitter.setSizes([int(height*0.65), int(height*0.35)])

        horizontalSplitter = QSplitter(Qt.Horizontal)
        horizontalSplitter.setContentsMargins(10, 10, 10, 10)
        horizontalSplitter.addWidget(verticalSplitter)
        horizontalSplitter.addWidget(rightTransactionsPanel)
        horizontalSplitter.setSizes([int(width*0.3), int(width*0.7)])

        transactionsLayout.addWidget(horizontalSplitter)

        transactionsScroll = QScrollArea()
        transactionsScroll.setWidget(horizontalSplitter)
        transactionsScroll.setWidgetResizable(True)

        #--------------------------------------------------------------------------------------
        #--------------------------------- ACCOUNTS TAB ---------------------------------------
        #--------------------------------------------------------------------------------------

        accountsLayout = QHBoxLayout()

        topLeftAccountsPanel = QFrame()
        topLeftAccountsPanel.setFrameShape(QFrame.StyledPanel)
        topLeftAccountsPanelVLayout = QVBoxLayout(topLeftAccountsPanel)

        self.topLeftAccountsCreateLabel = QLabel("Create account")
        self.topLeftAccountsCreateLabel.setAlignment(Qt.AlignCenter)
        self.topLeftAccountsNameLabel = QLabel("Name:")
        self.topLeftAccountsAmountLabel = QLabel("Initial amount:")
        self.topLeftAccountsSymbolLabel = QLabel("")
        self.topLeftAccountsCurrencyLabel = QLabel("Currency:")
        self.topLeftAccountsNotesLabel = QLabel("Notes (optional):")
        self.topLeftAccountsNotesLabel.setWordWrap(True)
        self.topLeftAccountsNameEntry = QLineEdit()
        self.topLeftAccountsNameEntry.setMaxLength(20)
        self.topLeftAccountsAmountEntry = QLineEdit()
        self.topLeftAccountsAmountEntry.setMaxLength(15)
        self.topLeftAccountsCurrencyEntry = QComboBox()
        codesList = ['EUR', 'IDR', 'BGN', 'ILS', 'GBP', 'DKK', 'CAD', 'JPY', 'HUF', 'RON', 'MYR', 'SEK', 'SGD', 'HKD', 'AUD', 'CHF', 'KRW', 'CNY', 'TRY', 'HRK', 'NZD', 'THB', 'USD', 'NOK', 'RUB', 'INR', 'MXN', 'CZK', 'BRL', 'PLN', 'PHP', 'ZAR']
        currencyName = codesList[0]
        for i in codesList:
            name = self.codes.get_currency_name(i)
            item = i + ' - ' + name
            self.topLeftAccountsCurrencyEntry.addItem(item)      
            if i == self.currencyCode:
                currencyName = item
        self.topLeftAccountsCurrencyEntry.currentTextChanged.connect(self.changeAccountSymbol)
        
        self.topLeftAccountsCurrencyEntry.setCurrentText(currencyName)
        self.topLeftAccountsNotesEntry = QPlainTextEdit()

        topLeftAccountsAmountHLayout = QHBoxLayout()
        topLeftAccountsAmountHLayout.addWidget(self.topLeftAccountsAmountEntry)
        topLeftAccountsAmountHLayout.addWidget(self.topLeftAccountsSymbolLabel)
        topLeftAccountsAmountHLayout.setSpacing(5)
        
        self.topLeftAccountsClearButton = QPushButton("Clear")
        self.topLeftAccountsClearButton.clicked.connect(self.clearAccountInfo)
        self.topLeftAccountsAddButton = QPushButton("Add account")
        self.topLeftAccountsAddButton.clicked.connect(self.addAccount)

        topLeftAccountsPanelGrid = QGridLayout()
        topLeftAccountsPanelGrid.addWidget(self.topLeftAccountsNameLabel, 0, 0)
        topLeftAccountsPanelGrid.addWidget(self.topLeftAccountsNameEntry, 0, 1)
        topLeftAccountsPanelGrid.addWidget(self.topLeftAccountsAmountLabel, 1, 0)
        topLeftAccountsPanelGrid.addLayout(topLeftAccountsAmountHLayout, 1, 1)
        topLeftAccountsPanelGrid.addWidget(self.topLeftAccountsCurrencyLabel, 2, 0)
        topLeftAccountsPanelGrid.addWidget(self.topLeftAccountsCurrencyEntry, 2, 1)
        topLeftAccountsPanelGrid.addWidget(self.topLeftAccountsNotesLabel, 5, 0)
        topLeftAccountsPanelGrid.addWidget(self.topLeftAccountsNotesEntry, 5, 1)
        topLeftAccountsPanelGrid.addWidget(self.topLeftAccountsClearButton, 6, 0)
        topLeftAccountsPanelGrid.addWidget(self.topLeftAccountsAddButton, 6, 1)
        topLeftAccountsPanelGrid.setVerticalSpacing(5)

        topLeftAccountsPanelVLayout.addWidget(self.topLeftAccountsCreateLabel)
        topLeftAccountsPanelVLayout.addLayout(topLeftAccountsPanelGrid)
        
        #--------------------------------------------------------------------------------------
        
        bottomLeftAccountsPanel = QFrame()
        bottomLeftAccountsPanel.setFrameShape(QFrame.StyledPanel)
        bottomLeftAccountsPanelVLayout = QVBoxLayout(bottomLeftAccountsPanel)

        self.bottomLeftAccountsTransferLabel = QLabel("Funds transfer")
        self.bottomLeftAccountsTransferLabel.setAlignment(Qt.AlignCenter)
        self.bottomLeftAccountsFromLabel = QLabel("From account:")
        self.bottomLeftAccountsToLabel = QLabel("To account:")
        self.bottomLeftAccountsAmountLabel = QLabel("Amount:")
        self.bottomLeftAccountsSymbolLabel = QLabel("")
        self.bottomLeftAccountsDateLabel = QLabel("Date:")
        self.bottomLeftAccountsFromEntry = QComboBox()
        self.bottomLeftAccountsFromEntry.currentTextChanged.connect(lambda: self.changeCurrencySymbol(self.bottomLeftAccountsFromEntry.currentText(), self.bottomLeftAccountsSymbolLabel))
        self.bottomLeftAccountsFromEntry.currentTextChanged.connect(lambda: self.changeRate(self.bottomLeftAccountsFromEntry.currentText(), self.bottomLeftAccountsToEntry.currentText()))
        self.bottomLeftAccountsToEntry = QComboBox()
        self.bottomLeftAccountsToEntry.currentTextChanged.connect(lambda: self.changeRate(self.bottomLeftAccountsFromEntry.currentText(), self.bottomLeftAccountsToEntry.currentText()))
        self.bottomLeftAccountsAmountEntry = QLineEdit()
        self.bottomLeftAccountsAmountEntry.setMaxLength(15)
        self.bottomLeftAccountsDateEntry = QDateEdit()
        self.bottomLeftAccountsDateEntry.setCalendarPopup(True)
        self.bottomLeftAccountsDateEntry.setDate(QDate.currentDate())
        self.bottomLeftAccountsDateEntry.setMaximumDate(QDate.currentDate())
        self.bottomLeftAccountsRateLabel = QLabel("Rate:")
        self.bottomLeftAccountsRateEntry = QLineEdit()
        self.bottomLeftAccountsRateEntry.setMaxLength(15)
        self.bottomLeftAccountsRateCheckBox = QCheckBox("Auto")

        self.bottomLeftAccountsClearButton = QPushButton("Clear")
        self.bottomLeftAccountsClearButton.setMaximumWidth(250)
        self.bottomLeftAccountsClearButton.clicked.connect(self.clearTransferInfo)
        self.bottomLeftAccountsTransferButton = QPushButton("Transfer")
        self.bottomLeftAccountsTransferButton.setMaximumWidth(250)
        self.bottomLeftAccountsTransferButton.clicked.connect(self.addTransfer)

        bottomLeftAccountsAmountHLayout = QHBoxLayout()
        bottomLeftAccountsAmountHLayout.addWidget(self.bottomLeftAccountsAmountEntry)
        bottomLeftAccountsAmountHLayout.addWidget(self.bottomLeftAccountsSymbolLabel)
        bottomLeftAccountsAmountHLayout.setSpacing(5)

        bottomLeftAccountsRateHLayout = QHBoxLayout()
        bottomLeftAccountsRateHLayout.addWidget(self.bottomLeftAccountsRateEntry)
        bottomLeftAccountsRateHLayout.addWidget(self.bottomLeftAccountsRateCheckBox)
        bottomLeftAccountsRateHLayout.setSpacing(5)

        bottomLeftAccountsPanelGrid = QGridLayout()
        bottomLeftAccountsPanelGrid.addWidget(self.bottomLeftAccountsFromLabel, 0, 0)
        bottomLeftAccountsPanelGrid.addWidget(self.bottomLeftAccountsFromEntry, 0, 1)
        bottomLeftAccountsPanelGrid.addWidget(self.bottomLeftAccountsToLabel, 1, 0)
        bottomLeftAccountsPanelGrid.addWidget(self.bottomLeftAccountsToEntry, 1, 1)
        bottomLeftAccountsPanelGrid.addWidget(self.bottomLeftAccountsAmountLabel, 2, 0)
        bottomLeftAccountsPanelGrid.addLayout(bottomLeftAccountsAmountHLayout, 2, 1)
        bottomLeftAccountsPanelGrid.addWidget(self.bottomLeftAccountsRateLabel, 3, 0)
        bottomLeftAccountsPanelGrid.addLayout(bottomLeftAccountsRateHLayout, 3, 1)
        bottomLeftAccountsPanelGrid.addWidget(self.bottomLeftAccountsDateLabel, 4, 0)
        bottomLeftAccountsPanelGrid.addWidget(self.bottomLeftAccountsDateEntry, 4, 1)
        bottomLeftAccountsPanelGrid.addWidget(self.bottomLeftAccountsClearButton, 5, 0)
        bottomLeftAccountsPanelGrid.addWidget(self.bottomLeftAccountsTransferButton, 5, 1)
        bottomLeftAccountsPanelGrid.setVerticalSpacing(10)

        bottomLeftAccountsPanelVLayout.addWidget(self.bottomLeftAccountsTransferLabel)
        bottomLeftAccountsPanelVLayout.addLayout(bottomLeftAccountsPanelGrid)
        
        #--------------------------------------------------------------------------------------
        
        rightAccountsPanel = QFrame()
        rightAccountsPanel.setFrameShape(QFrame.StyledPanel)
        rightAccountsPanelVLayout = QVBoxLayout(rightAccountsPanel)

        self.rightAccountsPanelTable = QTableView()
        self.rightAccountsPanelTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rightAccountsPanelTable.verticalHeader().setVisible(False)
        self.rightAccountsPanelTable.horizontalHeader().setStretchLastSection(True)
        self.rightAccountsPanelTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        decimalDelegate = DecimalDelegate()
        self.rightAccountsPanelTable.setItemDelegateForColumn(2, decimalDelegate)
        rightAccountsPanelVLayout.addWidget(self.rightAccountsPanelTable)

        rightAccountsEditHLayout = QHBoxLayout()
        self.rightAccountsDeleteButton = QPushButton("Delete account")
        self.rightAccountsDeleteButton.clicked.connect(self.deleteAccount)
        self.rightAccountsEditButton = QPushButton("Edit account")
        self.rightAccountsEditButton.clicked.connect(self.editAccount)
        rightAccountsEditHLayout.addWidget(self.rightAccountsEditButton, alignment=Qt.AlignLeft)
        rightAccountsEditHLayout.addWidget(self.rightAccountsDeleteButton, alignment=Qt.AlignRight)
        rightAccountsPanelVLayout.addLayout(rightAccountsEditHLayout)
        
        #--------------------------------------------------------------------------------------
        
        bottomRightAccountsPanel = QFrame()
        bottomRightAccountsPanel.setFrameShape(QFrame.StyledPanel)
        bottomRightAccountsPanelVLayout = QVBoxLayout(bottomRightAccountsPanel)

        self.bottomRightAccountsPanelTable = QTableView()
        self.bottomRightAccountsPanelTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bottomRightAccountsPanelTable.verticalHeader().setVisible(False)
        self.bottomRightAccountsPanelTable.horizontalHeader().setStretchLastSection(True)
        self.bottomRightAccountsPanelTable.setEditTriggers(QAbstractItemView.NoEditTriggers)    
        bottomRightAccountsPanelVLayout.addWidget(self.bottomRightAccountsPanelTable)

        bottomRightAccountsEditHLayout = QHBoxLayout()
        self.bottomRightAccountsDeleteButton = QPushButton("Delete transfer")
        self.bottomRightAccountsDeleteButton.clicked.connect(self.deleteTransfer)
        self.bottomRightAccountsEditButton = QPushButton("Edit transfer")
        self.bottomRightAccountsEditButton.clicked.connect(self.editTransfer)
        bottomRightAccountsEditHLayout.addWidget(self.bottomRightAccountsEditButton, alignment=Qt.AlignLeft)
        bottomRightAccountsEditHLayout.addWidget(self.bottomRightAccountsDeleteButton, alignment=Qt.AlignRight)
        bottomRightAccountsPanelVLayout.addLayout(bottomRightAccountsEditHLayout)
               
        #--------------------------------------------------------------------------------------
        
        splitterAccountsLeft = QSplitter(Qt.Vertical)
        splitterAccountsLeft.addWidget(topLeftAccountsPanel)
        splitterAccountsLeft.addWidget(bottomLeftAccountsPanel)
        splitterAccountsLeft.setSizes([int(height*0.58), int(height*0.42)])
        splitterAccountsLeft.setHandleWidth(10)

        splitterAccountsRight = QSplitter(Qt.Vertical)
        splitterAccountsRight.addWidget(rightAccountsPanel)
        splitterAccountsRight.addWidget(bottomRightAccountsPanel)
        splitterAccountsRight.setSizes([int(height*0.58), int(height*0.42)])
        splitterAccountsRight.setHandleWidth(10)
        
        splitterAccounts = QSplitter(Qt.Horizontal)
        splitterAccounts.setContentsMargins(10, 10, 10, 10)
        splitterAccounts.addWidget(splitterAccountsLeft)
        splitterAccounts.addWidget(splitterAccountsRight)
        splitterAccounts.setSizes([int(width*0.35), int(width*0.65)])
        splitterAccounts.setHandleWidth(0)

        accountsLayout.addWidget(splitterAccounts)

        accountsScroll = QScrollArea()
        accountsScroll.setWidget(splitterAccounts)
        accountsScroll.setWidgetResizable(True)

        # --------------------------------------------------------------------------------------
        # ---------------------------------- BUDGETS TAB ---------------------------------------
        # --------------------------------------------------------------------------------------

        budgetsLayout = QHBoxLayout()

        topLeftBudgetsPanel = QFrame()
        topLeftBudgetsPanel.setFrameShape(QFrame.StyledPanel)
        topLeftBudgetsPanelVLayout = QVBoxLayout(topLeftBudgetsPanel)

        self.topLeftBudgetsCreateLabel = QLabel("Create Budget")
        self.topLeftBudgetsCreateLabel.setAlignment(Qt.AlignCenter)
        self.topLeftBudgetsNameLabel = QLabel("Name:")
        self.topLeftBudgetsAmountLabel = QLabel("Amount:")
        self.topLeftBudgetsCategoryLabel = QLabel("Category:")
        self.topLeftBudgetsTypeLabel = QLabel("Type:")
        self.topLeftBudgetsFrequencyLabel = QLabel("Frequency:")
        self.topLeftBudgetsStartDateLabel = QLabel("Start date:")
        self.topLeftBudgetsEndDateLabel = QLabel("End date:")
        self.topLeftBudgetsNotesLabel = QLabel("Notes (optional):")
        self.topLeftBudgetsNotesLabel.setWordWrap(True)
        self.topLeftBudgetsNameEntry = QLineEdit()
        self.topLeftBudgetsNameEntry.setMaxLength(20)
        self.topLeftBudgetsAmountEntry = QLineEdit()
        self.topLeftBudgetsAmountEntry.setMaxLength(15)
        self.topLeftBudgetsSymbolLabel = QLabel(self.currency)
        self.topLeftBudgetsCategoryEntry = QComboBox()
        self.fillCategoriesComboBoxB()
        self.topLeftBudgetsCategoryEntry.addItem("All")
        self.topLeftBudgetsTypeEntry = QComboBox()
        self.topLeftBudgetsTypeEntry.addItem("Periodic")
        self.topLeftBudgetsTypeEntry.addItem("One-time")
        self.topLeftBudgetsFrequencyEntry = QComboBox()
        self.topLeftBudgetsFrequencyEntry.addItems(["Weekly", "Monthly", "Yearly"])
        self.topLeftBudgetsStartDateEntry = QDateEdit()
        self.topLeftBudgetsStartDateEntry.setCalendarPopup(True)
        self.topLeftBudgetsStartDateEntry.setDate(QDate.currentDate())
        self.topLeftBudgetsStartDateEntry.setDisabled(True)
        self.topLeftBudgetsEndDateEntry = QDateEdit()
        self.topLeftBudgetsEndDateEntry.setCalendarPopup(True)
        self.topLeftBudgetsEndDateEntry.setDate(QDate.currentDate())
        self.topLeftBudgetsEndDateEntry.setDisabled(True)
        self.topLeftBudgetsNotesEntry = QPlainTextEdit()
        self.topLeftBudgetsTypeEntry.currentTextChanged.connect(self.grayOutBudget)

        self.topLeftBudgetsClearButton = QPushButton("Clear")
        self.topLeftBudgetsClearButton.clicked.connect(self.clearBudgetInfo)
        self.topLeftBudgetsAddButton = QPushButton("Add budget")
        self.topLeftBudgetsAddButton.clicked.connect(self.addBudget)

        topLeftBudgetsSymbolHLayout = QHBoxLayout()
        topLeftBudgetsSymbolHLayout.setSpacing(5)
        topLeftBudgetsSymbolHLayout.addWidget(self.topLeftBudgetsAmountEntry)
        topLeftBudgetsSymbolHLayout.addWidget(self.topLeftBudgetsSymbolLabel)

        topLeftBudgetsPanelGrid = QGridLayout()
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsNameLabel, 0, 0)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsNameEntry, 0, 1)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsAmountLabel, 1, 0)
        topLeftBudgetsPanelGrid.addLayout(topLeftBudgetsSymbolHLayout, 1, 1)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsCategoryLabel, 2, 0)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsCategoryEntry, 2, 1)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsTypeLabel, 3, 0)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsTypeEntry, 3, 1)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsFrequencyLabel, 4, 0)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsFrequencyEntry, 4, 1)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsStartDateLabel, 5, 0)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsStartDateEntry, 5, 1)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsEndDateLabel, 6, 0)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsEndDateEntry, 6, 1)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsNotesLabel, 7, 0)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsNotesEntry, 7, 1)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsClearButton, 8, 0)
        topLeftBudgetsPanelGrid.addWidget(self.topLeftBudgetsAddButton, 8, 1)
        topLeftBudgetsPanelGrid.setVerticalSpacing(5)

        topLeftBudgetsPanelVLayout.addWidget(self.topLeftBudgetsCreateLabel)
        topLeftBudgetsPanelVLayout.addLayout(topLeftBudgetsPanelGrid)

        # --------------------------------------------------------------------------------------

        bottomLeftBudgetsPanel = QFrame()
        bottomLeftBudgetsPanel.setFrameShape(QFrame.StyledPanel)
        bottomLeftBudgetsPanelVLayout = QVBoxLayout(bottomLeftBudgetsPanel)

        self.bottomLeftBudgetsPanelTable = QTableView()
        self.bottomLeftBudgetsPanelTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bottomLeftBudgetsPanelTable.verticalHeader().setVisible(False)
        self.bottomLeftBudgetsPanelTable.horizontalHeader().setStretchLastSection(True)
        self.bottomLeftBudgetsPanelTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        bottomLeftBudgetsPanelVLayout.addWidget(self.bottomLeftBudgetsPanelTable)

        bottomLeftBudgetsEditHLayout = QHBoxLayout()
        self.bottomLeftBudgetsDeleteButton = QPushButton("Delete budget")
        self.bottomLeftBudgetsDeleteButton.clicked.connect(self.deleteBudget)
        self.bottomLeftBudgetsEditButton = QPushButton("Edit budget")
        self.bottomLeftBudgetsEditButton.clicked.connect(self.editBudget)
        bottomLeftBudgetsEditHLayout.addWidget(self.bottomLeftBudgetsEditButton, alignment=Qt.AlignLeft)
        bottomLeftBudgetsEditHLayout.addWidget(self.bottomLeftBudgetsDeleteButton, alignment=Qt.AlignRight)
        bottomLeftBudgetsPanelVLayout.addLayout(bottomLeftBudgetsEditHLayout)

        # --------------------------------------------------------------------------------------

        self.rightBudgetsPanel = QFrame()
        self.rightBudgetsPanel.setFrameShape(QFrame.NoFrame)
        self.areBudgetsChartsShown = False

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.rightBudgetsPanelVLayout = QVBoxLayout(self.rightBudgetsPanel)

        # --------------------------------------------------------------------------------------

        splitterBudgetsLeft = QSplitter(Qt.Vertical)
        splitterBudgetsLeft.addWidget(topLeftBudgetsPanel)
        splitterBudgetsLeft.addWidget(bottomLeftBudgetsPanel)
        splitterBudgetsLeft.setSizes([int(height * 0.58), int(height * 0.42)])

        splitterBudgets = QSplitter(Qt.Horizontal)
        splitterBudgets.setContentsMargins(10, 10, 10, 10)
        splitterBudgets.addWidget(splitterBudgetsLeft)
        splitterBudgets.addWidget(self.scrollArea)
        splitterBudgets.setSizes([int(width * 0.35), int(width * 0.65)])

        budgetsLayout.addWidget(splitterBudgets)

        budgetsScroll = QScrollArea()
        budgetsScroll.setWidget(splitterBudgets)
        budgetsScroll.setWidgetResizable(True)

        #--------------------------------------------------------------------------------------
        #---------------------------------- REPORTS TAB ---------------------------------------
        #--------------------------------------------------------------------------------------

        reportsLayout = QHBoxLayout()

        topLeftReportsPanel = QFrame()
        topLeftReportsPanel.setFrameShape(QFrame.StyledPanel)
        topLeftReportsPanelVLayout = QVBoxLayout(topLeftReportsPanel)

        self.topLeftReportsExRadioButton = QRadioButton('Expenses')
        self.topLeftReportsInRadioButton = QRadioButton('Incomes')
        self.topLeftReportsBothRadioButton = QRadioButton('Both')
        self.topLeftReportsTypeRadioButtons = QButtonGroup()
        self.topLeftReportsTypeRadioButtons.addButton(self.topLeftReportsExRadioButton)
        self.topLeftReportsTypeRadioButtons.addButton(self.topLeftReportsInRadioButton)
        self.topLeftReportsTypeRadioButtons.addButton(self.topLeftReportsBothRadioButton)
        self.topLeftReportsCategoryLabel = QLabel('CATEGORY')
        self.topLeftReportsCategoryLabel.setAlignment(Qt.AlignCenter)
        self.topLeftReportsFromLabel = QLabel('From:')
        self.topLeftReportsToLabel = QLabel('To:')
        self.topLeftReportsAccountLabel = QLabel('Account:')
        self.topLeftReportsFromEntry = QDateEdit()
        self.topLeftReportsFromEntry.setCalendarPopup(True)
        self.topLeftReportsFromEntry.setDateTime(QDateTime.currentDateTime())
        self.topLeftReportsToEntry = QDateEdit()
        self.topLeftReportsToEntry.setCalendarPopup(True)
        self.topLeftReportsToEntry.setDateTime(QDateTime.currentDateTime())
        self.topLeftReportsAccountEntry = QComboBox()
        self.topLeftReportsAcCheck = QCheckBox('All accounts')
        self.topLeftReportsAcCheck.stateChanged.connect(lambda: self.grayOutAccount(self.topLeftReportsAcCheck.checkState(), self.topLeftReportsAccountEntry))
        self.topLeftReportsTypeEntry = QComboBox()
        self.topLeftReportsTypeEntry.addItem('Bar chart')
        self.topLeftReportsTypeEntry.addItem('Pie chart')
        self.topLeftReportsClearFormButton = QPushButton('Clear form')
        self.topLeftReportsClearFormButton.clicked.connect(partial(self.clearReportInfo, "category"))
        self.topLeftReportsClearChartButton = QPushButton('Clear chart')
        self.topLeftReportsClearChartButton.clicked.connect(self.clearChart)
        self.topLeftReportsShowButton = QPushButton('Show')
        self.topLeftReportsShowButton.clicked.connect(self.showReportCategory)

        topLeftReportsButtonsHLayout = QHBoxLayout()
        topLeftReportsButtonsHLayout.addWidget(self.topLeftReportsClearFormButton)
        topLeftReportsButtonsHLayout.addWidget(self.topLeftReportsClearChartButton)
        topLeftReportsHLayout = QHBoxLayout()
        topLeftReportsGridLayout = QGridLayout()

        topLeftReportsHLayout.addWidget(self.topLeftReportsExRadioButton, alignment=Qt.AlignCenter)
        topLeftReportsHLayout.addWidget(self.topLeftReportsInRadioButton, alignment=Qt.AlignCenter)
        topLeftReportsHLayout.addWidget(self.topLeftReportsBothRadioButton, alignment=Qt.AlignCenter)
        topLeftReportsGridLayout.addWidget(self.topLeftReportsFromLabel, 0, 0)
        topLeftReportsGridLayout.addWidget(self.topLeftReportsFromEntry, 0, 1)
        topLeftReportsGridLayout.addWidget(self.topLeftReportsToLabel, 1, 0)
        topLeftReportsGridLayout.addWidget(self.topLeftReportsToEntry, 1, 1)
        topLeftReportsGridLayout.addWidget(self.topLeftReportsAccountLabel, 2, 0)
        topLeftReportsGridLayout.addWidget(self.topLeftReportsAccountEntry, 2, 1)
        topLeftReportsGridLayout.addWidget(self.topLeftReportsAcCheck, 3, 0)

        topLeftReportsPanelVLayout.addWidget(self.topLeftReportsCategoryLabel)
        topLeftReportsPanelVLayout.addLayout(topLeftReportsHLayout)
        topLeftReportsPanelVLayout.addLayout(topLeftReportsGridLayout)
        topLeftReportsPanelVLayout.addWidget(self.topLeftReportsTypeEntry)
        topLeftReportsPanelVLayout.insertSpacing(4, 10)
        topLeftReportsPanelVLayout.addLayout(topLeftReportsButtonsHLayout)
        topLeftReportsPanelVLayout.addWidget(self.topLeftReportsShowButton)

        #---------------------------------------------------------------------------------

        bottomLeftReportsPanel = QFrame()
        bottomLeftReportsPanel.setFrameShape(QFrame.StyledPanel)
        bottomLeftReportsPanelVLayout = QVBoxLayout(bottomLeftReportsPanel)

        self.bottomLeftReportsRadioButtonGroup = QButtonGroup()

        self.bottomLeftReportsExRadioButton = QRadioButton('Expenses')
        self.bottomLeftReportsInRadioButton = QRadioButton('Incomes')
        self.bottomLeftReportsBothRadioButton = QRadioButton('Both')
        self.bottomLeftReportsRadioButtonGroup.addButton(self.bottomLeftReportsExRadioButton)
        self.bottomLeftReportsRadioButtonGroup.addButton(self.bottomLeftReportsInRadioButton)
        self.bottomLeftReportsRadioButtonGroup.addButton(self.bottomLeftReportsBothRadioButton)
        self.bottomLeftReportsTimeLabel = QLabel('TIME')
        self.bottomLeftReportsTimeLabel.setAlignment(Qt.AlignCenter)
        self.bottomLeftReportsPeriodLabel = QLabel('Period:')
        self.bottomLeftReportsDaysRadioButton = QRadioButton('Days')
        self.bottomLeftReportsMonthsRadioButton = QRadioButton('Months')
        self.bottomLeftReportsDaysRadioButton.setChecked(True)
        self.bottomLeftReportsDaysRadioButton.toggled.connect(self.setDateEdit)
        self.bottomLeftReportsMonthsRadioButton.toggled.connect(self.setDateEdit)
        self.bottomLeftReportsFromLabel = QLabel('From:')
        self.bottomLeftReportsToLabel = QLabel('To:')
        self.bottomLeftReportsAccountLabel = QLabel('Account:')
        self.bottomLeftReportsFromEntry = QDateEdit()
        self.bottomLeftReportsFromEntry.setCalendarPopup(True)
        self.bottomLeftReportsFromEntry.setDateTime(QDateTime.currentDateTime())
        self.bottomLeftReportsToEntry = QDateEdit()
        self.bottomLeftReportsToEntry.setCalendarPopup(True)
        self.bottomLeftReportsToEntry.setDateTime(QDateTime.currentDateTime())
        self.bottomLeftReportsAccountEntry = QComboBox()
        self.bottomLeftReportsAcCheck = QCheckBox('All accounts')
        self.bottomLeftReportsAcCheck.stateChanged.connect(lambda: self.grayOutAccount(self.bottomLeftReportsAcCheck.checkState(), self.bottomLeftReportsAccountEntry))
        self.bottomLeftReportsClearFormButton = QPushButton('Clear form')
        self.bottomLeftReportsClearFormButton.clicked.connect(partial(self.clearReportInfo, "time"))
        self.bottomLeftReportsClearChartButton = QPushButton('Clear chart')
        self.bottomLeftReportsClearChartButton.clicked.connect(self.clearChart)
        self.bottomLeftReportsShowButton = QPushButton('Show')
        self.bottomLeftReportsShowButton.clicked.connect(self.showReportTime)

        bottomLeftReportsButtonsHLayout = QHBoxLayout()
        bottomLeftReportsButtonsHLayout.addWidget(self.bottomLeftReportsClearFormButton)
        bottomLeftReportsButtonsHLayout.addWidget(self.bottomLeftReportsClearChartButton)
        bottomLeftReportsHLayout1 = QHBoxLayout()
        bottomLeftReportsHLayout2 = QHBoxLayout()
        bottomLeftReportsGridLayout = QGridLayout()

        bottomLeftReportsHLayout2.addWidget(self.bottomLeftReportsDaysRadioButton)
        bottomLeftReportsHLayout2.addWidget(self.bottomLeftReportsMonthsRadioButton)

        bottomLeftReportsHLayout1.addWidget(self.bottomLeftReportsExRadioButton, alignment=Qt.AlignCenter)
        bottomLeftReportsHLayout1.addWidget(self.bottomLeftReportsInRadioButton, alignment=Qt.AlignCenter)
        bottomLeftReportsHLayout1.addWidget(self.bottomLeftReportsBothRadioButton, alignment=Qt.AlignCenter)
        bottomLeftReportsGridLayout.addWidget(self.bottomLeftReportsPeriodLabel, 0, 0)
        bottomLeftReportsGridLayout.addLayout(bottomLeftReportsHLayout2, 0, 1)
        bottomLeftReportsGridLayout.addWidget(self.bottomLeftReportsFromLabel, 1, 0)
        bottomLeftReportsGridLayout.addWidget(self.bottomLeftReportsFromEntry, 1, 1)
        bottomLeftReportsGridLayout.addWidget(self.bottomLeftReportsToLabel, 2, 0)
        bottomLeftReportsGridLayout.addWidget(self.bottomLeftReportsToEntry, 2, 1)
        bottomLeftReportsGridLayout.addWidget(self.bottomLeftReportsAccountLabel, 3, 0)
        bottomLeftReportsGridLayout.addWidget(self.bottomLeftReportsAccountEntry, 3, 1)
        bottomLeftReportsGridLayout.addWidget(self.bottomLeftReportsAcCheck, 4, 0)

        bottomLeftReportsPanelVLayout.addWidget(self.bottomLeftReportsTimeLabel)
        bottomLeftReportsPanelVLayout.addLayout(bottomLeftReportsHLayout1)
        bottomLeftReportsPanelVLayout.addLayout(bottomLeftReportsGridLayout)
        bottomLeftReportsPanelVLayout.insertSpacing(3, 10)
        bottomLeftReportsPanelVLayout.addLayout(bottomLeftReportsButtonsHLayout)
        bottomLeftReportsPanelVLayout.addWidget(self.bottomLeftReportsShowButton)

        #----------------------------------------------------------------------------------
        
        rightReportsPanel = QFrame()
        rightReportsPanel.setFrameShape(QFrame.StyledPanel)
        self.rightReportsPanelVLayout = QVBoxLayout(rightReportsPanel)

        QToolTip.setFont(QFont('SansSerif', 12))

        self.isChartShown = False
        self.isScrollShown = False
        self.chart = QChart()
        
        #--------------------------------------------------------------------------------

        splitterLeftReports = QSplitter(Qt.Vertical)
        splitterLeftReports.addWidget(topLeftReportsPanel)
        splitterLeftReports.addWidget(bottomLeftReportsPanel)
        splitterLeftReports.setSizes([int(width*0.5), int(width*0.5)])
        
        splitterReports = QSplitter(Qt.Horizontal)
        splitterReports.setContentsMargins(10, 10, 10, 10)
        splitterReports.addWidget(splitterLeftReports)
        splitterReports.addWidget(rightReportsPanel)
        splitterReports.setSizes([int(width*0.3), int(width*0.7)])

        reportsLayout.addWidget(splitterReports)

        reportsScroll = QScrollArea()
        reportsScroll.setWidget(splitterReports)
        reportsScroll.setWidgetResizable(True)

        #--------------------------------------------------------------------------------------
        #------------------------------- RECURRING TRANSACTIONS -------------------------------
        #--------------------------------------------------------------------------------------

        recurringLayout = QHBoxLayout()

        leftRecurTransactionsPanel = QFrame()
        leftRecurTransactionsPanel.setFrameShape(QFrame.StyledPanel)
        self.leftRecurTransactionsPanelVLayout = QVBoxLayout(leftRecurTransactionsPanel)

        rightRecurTransactionsPanel = QFrame()
        rightRecurTransactionsPanel.setFrameShape(QFrame.StyledPanel)
        self.rightRecurTransactionsPanelVLayout = QVBoxLayout(rightRecurTransactionsPanel)

        bottomRecurTransactionsPanel = QFrame()
        bottomRecurTransactionsPanel.setFrameShape(QFrame.StyledPanel)
        bottomRecurTransactionsPanelVLayout = QVBoxLayout(bottomRecurTransactionsPanel)

        #--------------------------------------------------------------------------------------
        
        self.recurringNameLabel = QLabel('Name:')
        self.recurringNameEdit = QLineEdit()
        self.recurringNameEdit.setMaxLength(20)
        
        recurringHLayout = QHBoxLayout()
        recurringHLayout.addWidget(self.recurringNameLabel)
        recurringHLayout.insertSpacing(1, 10)
        recurringHLayout.addWidget(self.recurringNameEdit)

        self.recurringExpenseRadioButton = QRadioButton('Expense')
        self.recurringIncomeRadioButton = QRadioButton('Income')
        self.recurringTrType = QButtonGroup()
        self.recurringTrType.addButton(self.recurringExpenseRadioButton)
        self.recurringTrType.addButton(self.recurringIncomeRadioButton)
        self.recurringExpenseRadioButton.toggled.connect(lambda: self.fillCategoriesComboBox(self.recurringCategoryEntry))
        self.recurringIncomeRadioButton.toggled.connect(lambda: self.fillCategoriesComboBox(self.recurringCategoryEntry))
        self.recurringTypeLabel = QLabel('Type:')
        self.recurringValueLabel = QLabel('Amount:')
        self.recurringSymbolLabel = QLabel("")
        self.recurringCategoryLabel = QLabel('Category:')
        self.recurringAccountLabel = QLabel('Account:')
        self.recurringNotesLabel = QLabel('Notes (optional):')
        self.recurringNotesLabel.setWordWrap(True)
        self.recurringValueEntry = QLineEdit()
        self.recurringValueEntry.setMaxLength(15)
        self.recurringCategoryEntry = QComboBox()
        self.recurringAccountEntry = QComboBox()
        self.recurringAccountEntry.currentTextChanged.connect(lambda: self.changeCurrencySymbol(self.recurringAccountEntry.currentText(), self.recurringSymbolLabel))

        self.recurringNotesEntry = QPlainTextEdit()
        self.recurringClearButton = QPushButton('Clear')
        self.recurringClearButton.setFixedWidth(100)
        self.recurringClearButton.clicked.connect(self.clearRecurringTrInfo)
        recurringTrInfoHBoxLayout = QHBoxLayout()
        recurringTrInfoHBoxLayout.addWidget(self.recurringExpenseRadioButton, alignment=Qt.AlignCenter)
        recurringTrInfoHBoxLayout.addWidget(self.recurringIncomeRadioButton, alignment=Qt.AlignCenter)
        recurringTrInfoSymbolHBoxLayout = QHBoxLayout()
        recurringTrInfoSymbolHBoxLayout.setSpacing(5)
        recurringTrInfoSymbolHBoxLayout.addWidget(self.recurringValueEntry)
        recurringTrInfoSymbolHBoxLayout.addWidget(self.recurringSymbolLabel)
        recurringTrInfoGridLayout = QGridLayout()
        recurringTrInfoGridLayout.addWidget(self.recurringTypeLabel, 0, 0)
        recurringTrInfoGridLayout.addLayout(recurringTrInfoHBoxLayout, 0, 1)
        recurringTrInfoGridLayout.addWidget(self.recurringValueLabel, 1, 0)
        recurringTrInfoGridLayout.addLayout(recurringTrInfoSymbolHBoxLayout, 1, 1)
        recurringTrInfoGridLayout.addWidget(self.recurringCategoryLabel, 2, 0)
        recurringTrInfoGridLayout.addWidget(self.recurringCategoryEntry, 2, 1)
        recurringTrInfoGridLayout.addWidget(self.recurringAccountLabel, 3, 0)
        recurringTrInfoGridLayout.addWidget(self.recurringAccountEntry, 3, 1)
        recurringTrInfoGridLayout.addWidget(self.recurringNotesLabel, 4, 0)
        recurringTrInfoGridLayout.addWidget(self.recurringNotesEntry, 4, 1)
        recurringTrInfoGridLayout.setVerticalSpacing(10)

        #--------------------------------------------------------------------------------------
        
        self.recurringSchTypeLabel = QLabel('Schedule type:')
        self.recurringOnceRadioButton = QRadioButton("One time")
        self.recurringRecurRadioButton = QRadioButton("Recurring")
        self.recurringRecurEnabledCheckBox = QCheckBox('Enabled')
        self.recurringRecurEnabledCheckBox.setChecked(True)
        self.recurringSchType = QButtonGroup()
        self.recurringSchType.addButton(self.recurringOnceRadioButton)
        self.recurringSchType.addButton(self.recurringRecurRadioButton)
        self.recurringOnceRadioButton.toggled.connect(self.changeScheduleType)
        self.recurringRecurRadioButton.toggled.connect(self.changeScheduleType)

        recurringHLayout1 = QHBoxLayout()
        recurringHLayout1.addWidget(self.recurringSchTypeLabel)
        recurringHLayout1.addWidget(self.recurringOnceRadioButton, alignment=Qt.AlignCenter)
        recurringHLayout1.addWidget(self.recurringRecurRadioButton, alignment=Qt.AlignCenter)
        recurringHLayout1.addWidget(self.recurringRecurEnabledCheckBox, alignment=Qt.AlignCenter)

        #--------------------------------------------------------------------------------------

        self.recurringOnceLabel = QLabel('One-time occurence')
        self.recurringOnceLine = QFrame()
        self.recurringOnceLine.setFrameShape(QFrame.HLine)
        self.recurringOnceLine.setFrameShadow(QFrame.Sunken)
        self.recurringOnceDateLabel = QLabel('Date:')
        self.recurringOnceTimeLabel = QLabel('Time:')
        self.recurringOnceDateEntry = QDateEdit()
        self.recurringOnceDateEntry.setCalendarPopup(True)
        self.recurringOnceDateEntry.setDateTime(QDateTime.currentDateTime())
        self.recurringOnceTimeEntry = QTimeEdit()
        self.recurringOnceTimeEntry.setWrapping(True)
        self.recurringOnceTimeEntry.setDisplayFormat('hh:mm:ss')
        self.recurringOnceTimeEntry.setDateTime(QDateTime.currentDateTime())

        recurringOnceHLayout = QHBoxLayout()
        recurringOnceHLayout.addWidget(self.recurringOnceLabel)
        recurringOnceHLayout.addWidget(self.recurringOnceLine)
        recurringOnceHLayout.setStretchFactor(self.recurringOnceLine, 1)

        recurringHLayout2 = QHBoxLayout()
        recurringHLayout2.addWidget(self.recurringOnceDateLabel)
        recurringHLayout2.addWidget(self.recurringOnceDateEntry)
        recurringHLayout2.insertSpacing(2, 100)
        recurringHLayout2.addWidget(self.recurringOnceTimeLabel)
        recurringHLayout2.addWidget(self.recurringOnceTimeEntry)
        recurringHLayout2.addSpacing(100)

        #--------------------------------------------------------------------------------------

        self.recurringFreqLabel = QLabel('Frequency')
        self.recurringFreqLine = QFrame()
        self.recurringFreqLine.setFrameShape(QFrame.HLine)
        self.recurringFreqLine.setFrameShadow(QFrame.Sunken)
        self.recurringFreqOccursLabel = QLabel('Occurs:')
        self.recurringFreqComboBox = QComboBox()    
        self.recurringFreqComboBox.addItems(['Daily', 'Weekly', 'Monthly'])
        self.emptySpace1 = QLabel('')
        self.emptySpace2 = QLabel('')
        self.recurringFreqComboBox.currentTextChanged.connect(self.changeFrequency)
        self.recurringFreqOccursAtLabel = QLabel('Occurs at:')
        self.recurringFreqOccursAtTimeEntry = QTimeEdit()
        self.recurringFreqOccursAtTimeEntry.setWrapping(True)
        self.recurringFreqOccursAtTimeEntry.setDisplayFormat('hh:mm:ss')
        self.emptySpace3 = QLabel('')
        self.emptySpace4 = QLabel('')

        self.recurringFreqRecursWeekLabel = QLabel('Recurs every:')
        self.recurringFreqWeekSpinBox = QSpinBox()
        self.recurringFreqWeekSpinBox.setMinimum(1)
        self.recurringFreqWeekVarLabel = QLabel('week(s) on')
        self.recurringDaysCheckBoxList = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, v in enumerate(self.recurringDaysCheckBoxList):
            self.recurringDaysCheckBoxList[i] = QCheckBox(v)

        self.recurringFreqRecursDayLabel = QLabel('Recurs every:')
        self.recurringFreqDaySpinBox = QSpinBox()
        self.recurringFreqDaySpinBox.setMinimum(1)
        self.recurringFreqDayVarLabel = QLabel('day(s)')
        self.recurringFreqDayEmptySpace = QLabel('')

        self.recurringFreqRecursMonthLabel = QLabel('Recurs every:')
        self.recurringFreqMonthSpinBox = QSpinBox()
        self.recurringFreqMonthSpinBox.setMinimum(1)
        self.recurringFreqMonthVarLabel = QLabel('month(s)')
        self.recurringOnDayLabel = QLabel('on day:')
        self.recurringOnDaySpinBox = QSpinBox()
        self.recurringOnDaySpinBox.setMinimum(1)
        self.recurringOnDaySpinBox.setMaximum(31)

        self.firstLayout = QWidget(self)
        self.secondLayout = QWidget(self)
        self.thirdLayout = QWidget(self)

        self.recurringDayHLayout = QHBoxLayout(self.firstLayout)
        self.recurringDayHLayout.setContentsMargins(0, 0, 0, 0)
        self.recurringDayHLayout.addWidget(self.recurringFreqRecursDayLabel)
        self.recurringDayHLayout.addWidget(self.recurringFreqDaySpinBox)
        self.recurringDayHLayout.addWidget(self.recurringFreqDayVarLabel)
        self.recurringDayHLayout.addWidget(self.recurringFreqDayEmptySpace)

        self.recurringWeekHLayout = QHBoxLayout(self.secondLayout)
        self.recurringWeekHLayout.setContentsMargins(0, 0, 0, 0)
        self.recurringWeekHLayout.addWidget(self.recurringFreqRecursWeekLabel)
        self.recurringWeekHLayout.addWidget(self.recurringFreqWeekSpinBox)
        self.recurringWeekHLayout.addWidget(self.recurringFreqWeekVarLabel)
        for checkBox in self.recurringDaysCheckBoxList:
            self.recurringWeekHLayout.addWidget(checkBox)

        self.recurringMonthHLayout = QHBoxLayout(self.thirdLayout)
        self.recurringMonthHLayout.setContentsMargins(0, 0, 0, 0)
        self.recurringMonthHLayout.addWidget(self.recurringFreqRecursMonthLabel)
        self.recurringMonthHLayout.addWidget(self.recurringFreqMonthSpinBox)
        self.recurringMonthHLayout.addWidget(self.recurringFreqMonthVarLabel)
        self.recurringMonthHLayout.addWidget(self.recurringOnDayLabel)
        self.recurringMonthHLayout.addWidget(self.recurringOnDaySpinBox)

        self.stackedLayout = QStackedLayout()
        self.stackedLayout.addWidget(self.firstLayout)
        self.stackedLayout.addWidget(self.secondLayout)
        self.stackedLayout.addWidget(self.thirdLayout)

        recurringFreqHLayout = QHBoxLayout()
        recurringFreqHLayout.addWidget(self.recurringFreqLabel)
        recurringFreqHLayout.addWidget(self.recurringFreqLine)
        recurringFreqHLayout.setStretchFactor(self.recurringFreqLine, 1)

        recurringFreqGridLayout1 = QHBoxLayout()
        recurringFreqGridLayout1.addWidget(self.recurringFreqOccursLabel)
        recurringFreqGridLayout1.addWidget(self.recurringFreqComboBox)
        recurringFreqGridLayout1.addWidget(self.emptySpace1)
        recurringFreqGridLayout1.addWidget(self.emptySpace2)
        recurringFreqGridLayout2 = QHBoxLayout()
        recurringFreqGridLayout2.addWidget(self.recurringFreqOccursAtLabel)
        recurringFreqGridLayout2.addWidget(self.recurringFreqOccursAtTimeEntry)
        recurringFreqGridLayout2.addWidget(self.emptySpace3)
        recurringFreqGridLayout2.addWidget(self.emptySpace4)

        #--------------------------------------------------------------------------------------

        self.recurringDurationLabel = QLabel('Duration')
        self.recurringDurationLine = QFrame()
        self.recurringDurationLine.setFrameShape(QFrame.HLine)
        self.recurringDurationLine.setFrameShadow(QFrame.Sunken)
        self.recurringDurationStartLabel = QLabel('Start date:')
        self.recurringDurationStartDateEntry = QDateEdit()
        self.recurringDurationStartDateEntry.setCalendarPopup(True)
        self.recurringDurationStartDateEntry.setDateTime(QDateTime.currentDateTime())
        self.recurringDurationEndRadioButton = QRadioButton('End date:')
        self.recurringDurationNoEndRadioButton = QRadioButton('No end date')
        self.recurringDurationEndRadioButton.toggled.connect(self.changeEndType)
        self.recurringDurationNoEndRadioButton.toggled.connect(self.changeEndType)
        self.recurringDurationEndDateEntry = QDateEdit()
        self.recurringDurationEndDateEntry.setCalendarPopup(True)
        self.recurringDurationEndDateEntry.setDateTime(QDateTime.currentDateTime())

        recurringDurationHLayout = QHBoxLayout()
        recurringDurationHLayout.addWidget(self.recurringDurationLabel)
        recurringDurationHLayout.addWidget(self.recurringDurationLine)
        recurringDurationHLayout.setStretchFactor(self.recurringDurationLine, 1)

        recurringDurationGridLayout = QGridLayout()
        recurringDurationGridLayout.addWidget(self.recurringDurationStartLabel, 0, 0)
        recurringDurationGridLayout.addWidget(self.recurringDurationStartDateEntry, 0, 1)
        recurringDurationGridLayout.addWidget(self.recurringDurationNoEndRadioButton, 0, 2)
        recurringDurationGridLayout.addWidget(self.recurringDurationEndRadioButton, 0, 3)
        recurringDurationGridLayout.addWidget(self.recurringDurationEndDateEntry, 0, 4)

        #--------------------------------------------------------------------------------------

        self.recurringButton = QPushButton('Add scheduled operation')
        self.recurringButton.setFixedWidth(300)
        self.recurringButton.clicked.connect(self.addJob)

        self.recurringApplyButton = QPushButton('Apply changes')
        self.recurringApplyButton.setFixedWidth(250)
        self.recurringCancelButton = QPushButton('Cancel')
        self.recurringCancelButton.setFixedWidth(250)
        self.recurringCancelButton.clicked.connect(self.cancelEditScheduledTransaction)

        self.recurringAddLayout = QWidget(self)
        self.recurringEditLayout = QWidget(self)

        recurringEditButtonsHLayout1 = QHBoxLayout(self.recurringAddLayout)
        recurringEditButtonsHLayout1.setContentsMargins(0, 0, 0, 0)
        recurringEditButtonsHLayout2 = QHBoxLayout(self.recurringEditLayout)
        recurringEditButtonsHLayout2.setContentsMargins(0, 0, 0, 0)

        recurringEditButtonsHLayout1.addWidget(self.recurringButton, alignment=Qt.AlignCenter)
        recurringEditButtonsHLayout2.addWidget(self.recurringCancelButton)
        recurringEditButtonsHLayout2.addWidget(self.recurringApplyButton)

        self.recurringEditStackedLayout = QStackedLayout()
        self.recurringEditStackedLayout.addWidget(self.recurringAddLayout)
        self.recurringEditStackedLayout.addWidget(self.recurringEditLayout)

        self.leftRecurTransactionsPanelVLayout.addLayout(recurringHLayout)
        self.leftRecurTransactionsPanelVLayout.insertSpacing(1, 25)
        self.leftRecurTransactionsPanelVLayout.addLayout(recurringTrInfoGridLayout)
        self.leftRecurTransactionsPanelVLayout.addWidget(self.recurringClearButton, alignment=Qt.AlignCenter)
        
        self.rightRecurTransactionsPanelVLayout.addLayout(recurringHLayout1)
        self.rightRecurTransactionsPanelVLayout.addLayout(recurringOnceHLayout)
        self.rightRecurTransactionsPanelVLayout.addLayout(recurringHLayout2)
        self.rightRecurTransactionsPanelVLayout.addLayout(recurringFreqHLayout)
        self.rightRecurTransactionsPanelVLayout.addLayout(recurringFreqGridLayout1)
        self.stackedLayout.setCurrentIndex(0)
        self.rightRecurTransactionsPanelVLayout.insertLayout(5, self.stackedLayout)
        self.rightRecurTransactionsPanelVLayout.addLayout(recurringFreqGridLayout2)
        self.rightRecurTransactionsPanelVLayout.addLayout(recurringDurationHLayout)
        self.rightRecurTransactionsPanelVLayout.addLayout(recurringDurationGridLayout)
        self.rightRecurTransactionsPanelVLayout.insertSpacing(10, 20)
        self.recurringEditStackedLayout.setCurrentIndex(0)
        self.rightRecurTransactionsPanelVLayout.insertLayout(10, self.recurringEditStackedLayout)

        #--------------------------------------------------------------------------------------
        
        self.scheduledTrTableView = QTableView()
        self.scheduledTrTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scheduledTrTableView.verticalHeader().setVisible(False)
        self.scheduledTrTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scheduledTrTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scheduledTrEditButton = QPushButton('Edit scheduled operation')
        self.scheduledTrEditButton.setFixedWidth(300)
        self.scheduledTrEditButton.clicked.connect(self.editScheduledTransaction)
        self.scheduledTrDeleteButton = QPushButton('Delete scheduled operation')
        self.scheduledTrDeleteButton.setFixedWidth(300)
        self.scheduledTrDeleteButton.clicked.connect(self.deleteScheduledTransaction)

        bottomRecurTransactionsPanelHLayout = QHBoxLayout()
        bottomRecurTransactionsPanelHLayout.addWidget(self.scheduledTrEditButton, alignment=Qt.AlignLeft)
        bottomRecurTransactionsPanelHLayout.addWidget(self.scheduledTrDeleteButton, alignment=Qt.AlignRight)
        
        bottomRecurTransactionsPanelVLayout.addWidget(self.scheduledTrTableView)
        bottomRecurTransactionsPanelVLayout.addLayout(bottomRecurTransactionsPanelHLayout)
        
        #--------------------------------------------------------------------------------------

        splitterRecur1 = QSplitter(Qt.Horizontal)
        splitterRecur1.addWidget(leftRecurTransactionsPanel)
        splitterRecur1.addWidget(rightRecurTransactionsPanel)
        splitterRecur1.setSizes([int(width*0.3), int(width*0.7)])
        splitterRecur1.setHandleWidth(0)

        splitterRecur2 = QSplitter(Qt.Vertical)
        splitterRecur2.setContentsMargins(10, 10, 10, 10)
        splitterRecur2.addWidget(splitterRecur1)
        splitterRecur2.addWidget(bottomRecurTransactionsPanel)
        splitterRecur2.setSizes([int(height*0.4), int(height*0.6)])

        recurringLayout.addWidget(splitterRecur2)

        self.recurringRecurRadioButton.setChecked(True)
        self.recurringRecurRadioButton.clicked.connect(self.changeScheduleType)
        self.recurringDurationNoEndRadioButton.setChecked(True)
        self.recurringDurationNoEndRadioButton.clicked.connect(self.changeEndType)

        recurringScroll = QScrollArea()
        recurringScroll.setWidget(splitterRecur2)
        recurringScroll.setWidgetResizable(True)

        #--------------------------------------------------------------------------------------
        #-------------------------------------- TABS ------------------------------------------
        #--------------------------------------------------------------------------------------

        self.mainWindowTabs = QTabWidget()
        self.homeTab = QWidget()
        self.transactionsTab = QWidget()
        self.accountsTab = QWidget()
        self.budgetsTab = QWidget()
        self.reportsTab = QWidget()
        self.scheduledTab = QWidget()
        self.mainWindowTabs.resize(800, 500)
        self.mainWindowTabs.addTab(self.homeTab, "Home")
        self.mainWindowTabs.addTab(self.transactionsTab, "Transactions")
        self.mainWindowTabs.addTab(self.accountsTab, "Accounts")
        self.mainWindowTabs.addTab(self.budgetsTab, "Budgets")
        self.mainWindowTabs.addTab(self.reportsTab, "Charts")
        self.mainWindowTabs.addTab(self.scheduledTab, "Scheduled Operations")

        self.homeTab.layout = QVBoxLayout()
        self.homeTab.layout.addWidget(homeScroll)
        self.homeTab.setLayout(self.homeTab.layout)

        self.transactionsTab.layout = QVBoxLayout()
        self.transactionsTab.layout.addWidget(transactionsScroll)
        self.transactionsTab.setLayout(self.transactionsTab.layout)

        self.accountsTab.layout = QVBoxLayout()
        self.accountsTab.layout.addWidget(accountsScroll)
        self.accountsTab.setLayout(self.accountsTab.layout)

        self.budgetsTab.layout = QVBoxLayout()
        self.budgetsTab.layout.addWidget(budgetsScroll)
        self.budgetsTab.setLayout(self.budgetsTab.layout)

        self.reportsTab.layout = QVBoxLayout()
        self.reportsTab.layout.addWidget(reportsScroll)
        self.reportsTab.setLayout(self.reportsTab.layout)

        self.scheduledTab.layout = QVBoxLayout()
        self.scheduledTab.layout.addWidget(recurringScroll)
        self.scheduledTab.setLayout(self.scheduledTab.layout)

        mainLayout.addLayout(topHorizontalLayout)
        mainLayout.setSpacing(10)
        mainLayout.addWidget(self.mainWindowTabs)
        self.setLayout(mainLayout)
        
        self.setWindowTitle("Program")

    def showTime(self):
        """Metoda pobierająca i ustawiająca aktualną datę i czas"""
        currentTime = QDateTime.currentDateTime()
        labelTime = QLocale(QLocale.English).toString(currentTime, 'dddd, dd.MM.yyyy hh:mm:ss')
        self.topClockLabel.setText(labelTime)

    def logout(self):
        """Metoda wylogowująca użytkownika"""
        self.app.setPalette(self.defaultPalette)
        self.close()
        self.loginWindow.show()
        
    def closeEvent(self, event):       
        """Metoda zamykająca wszystkie okna po zamknięciu okna głównego"""
        self.app.closeAllWindows()
        

class DecimalDelegate(QStyledItemDelegate):
    """Klasa reprezentująca delegata formatującego wyświetlane w obiekcie klasy QTabelView dane"""
    def displayText(self, text, locale):
        return "{:.2f}".format(text, 2)
