from PyQt5.QtCore import Qt, QDateTime, QDate
from PyQt5.QtSql import QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLabel, QLineEdit, QGridLayout, QPushButton, \
    QVBoxLayout, QHBoxLayout, QComboBox, QDateEdit, QPlainTextEdit, QSpinBox, QRadioButton, \
    QCheckBox
from forex_python.converter import CurrencyCodes


class EditTransactionWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 300, 350)
        self.setFont(self.parent.fontt)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        editTransactionWindowMainLayout = QVBoxLayout(self)
        editTransactionWindowMainLayout.setSpacing(10)

        self.editTransactionAmountLabel = QLabel("Amount:")
        self.editTransactionSymbolLabel = QLabel("")
        self.editTransactionCategoryLabel = QLabel("Category:")
        self.editTransactionAccountLabel = QLabel("Account:")
        self.editTransactionDateLabel = QLabel("Date:")
        self.editTransactionNotesLabel = QLabel("Notes (Optional):")
        self.editTransactionNotesLabel.setWordWrap(True)
        self.editTransactionAmountEntry = QLineEdit()
        self.editTransactionAmountEntry.setMaxLength(15)
        self.editTransactionCategoryEntry = QComboBox()
        self.editTransactionAccountEntry = QComboBox()
        self.editTransactionAccountEntry.currentTextChanged.connect(self.changeCurrencySymbol)
        self.editTransactionDateEntry = QDateEdit()
        self.editTransactionDateEntry.setCalendarPopup(True)
        self.editTransactionDateEntry.setMaximumDate(QDate.currentDate())
        self.editTransactionDateEntry.setDateTime(QDateTime.currentDateTime())
        self.editTransactionNotesEntry = QPlainTextEdit()

        self.editTransactionCancelButton = QPushButton("Cancel")
        self.editTransactionCancelButton.clicked.connect(self.exit)
        self.editTransactionEditButton = QPushButton("Edit")

        editTransactionHLayout = QHBoxLayout()
        editTransactionHLayout.setSpacing(5)
        editTransactionHLayout.addWidget(self.editTransactionAmountEntry)
        editTransactionHLayout.addWidget(self.editTransactionSymbolLabel)

        editTransactionGrid = QGridLayout()
        editTransactionGrid.addWidget(self.editTransactionAmountLabel, 0, 0)
        editTransactionGrid.addLayout(editTransactionHLayout, 0, 1)
        editTransactionGrid.addWidget(self.editTransactionCategoryLabel, 1, 0)
        editTransactionGrid.addWidget(self.editTransactionCategoryEntry, 1, 1)
        editTransactionGrid.addWidget(self.editTransactionAccountLabel, 2, 0)
        editTransactionGrid.addWidget(self.editTransactionAccountEntry, 2, 1)
        editTransactionGrid.addWidget(self.editTransactionDateLabel, 3, 0)
        editTransactionGrid.addWidget(self.editTransactionDateEntry, 3, 1)
        editTransactionGrid.addWidget(self.editTransactionNotesLabel, 4, 0)
        editTransactionGrid.addWidget(self.editTransactionNotesEntry, 4, 1)
        editTransactionGrid.addWidget(self.editTransactionCancelButton, 5, 0)
        editTransactionGrid.addWidget(self.editTransactionEditButton, 5, 1)
        editTransactionWindowMainLayout.addLayout(editTransactionGrid)

        self.setWindowTitle("Transaction")

    def changeCurrencySymbol(self, text):
        code = CurrencyCodes()
        findSymbolQuery = QSqlQuery()
        findSymbolQuery.prepare("SELECT currency FROM accounts WHERE name = :name")
        findSymbolQuery.bindValue(":name", text)
        findSymbolQuery.exec()
        if findSymbolQuery.next():
            currency = findSymbolQuery.value(0)
        else:
            return
        symbol = code.get_symbol(currency)
        self.editTransactionSymbolLabel.setText(symbol)
        findSymbolQuery.finish()

    def exit(self):
        self.close()


class EditAccountWindow(QWidget):
    def __init__(self, parent, userID):
        super().__init__()
        self.parent = parent
        self.userID = userID
        self.initUI()

    def initUI(self):

        self.setGeometry(0, 0, 300, 200)
        self.setFont(self.parent.fontt)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        editAccountWindowMainLayout = QVBoxLayout(self)
        editAccountWindowMainLayout.setSpacing(10)

        self.editAccountNameLabel = QLabel("Name:")
        self.editAccountCurrencyLabel = QLabel("Currency:")
        self.editAccountAmountLabel = QLabel("Initial Amount:")
        self.editAccountSymbolLabel = QLabel("")
        self.editAccountPositionLabel = QLabel("Position:")
        self.editAccountNotesLabel = QLabel("Notes (optional):")
        self.editAccountNotesLabel.setWordWrap(True)
        self.editAccountNameEntry = QLineEdit()
        self.editAccountNameEntry.setMaxLength(20)
        self.editAccountCurrencyEntry = QComboBox()
        self.editAccountCurrencyEntry.currentTextChanged.connect(self.changeCurrencySymbol)
        codesList = ['EUR', 'IDR', 'BGN', 'ILS', 'GBP', 'DKK', 'CAD', 'JPY', 'HUF', 'RON', 'MYR', 'SEK', 'SGD', 'HKD',
                     'AUD', 'CHF', 'KRW', 'CNY', 'TRY', 'HRK', 'NZD', 'THB', 'USD', 'NOK', 'RUB', 'INR', 'MXN', 'CZK',
                     'BRL', 'PLN', 'PHP', 'ZAR']
        self.codes = CurrencyCodes()
        for i in codesList:
            name = self.codes.get_currency_name(i)
            item = i + ' - ' + name
            self.editAccountCurrencyEntry.addItem(item)
        self.editAccountAmountEntry = QLineEdit()
        self.editAccountAmountEntry.setMaxLength(15)
        self.editAccountPositionEntry = QSpinBox()
        self.editAccountPositionEntry.setMinimum(1)
        self.editAccountPositionEntry.setMaximum(self.countAccounts())
        self.editAccountNotesEntry = QPlainTextEdit()

        self.editAccountCancelButton = QPushButton("Cancel")
        self.editAccountCancelButton.clicked.connect(self.exit)
        self.editAccountEditButton = QPushButton("Edit")

        editAccountHLayout = QHBoxLayout()
        editAccountHLayout.setSpacing(5)
        editAccountHLayout.addWidget(self.editAccountAmountEntry)
        editAccountHLayout.addWidget(self.editAccountSymbolLabel)

        editAccountGrid = QGridLayout()
        editAccountGrid.addWidget(self.editAccountNameLabel, 0, 0)
        editAccountGrid.addWidget(self.editAccountNameEntry, 0, 1)
        editAccountGrid.addWidget(self.editAccountCurrencyLabel, 1, 0)
        editAccountGrid.addWidget(self.editAccountCurrencyEntry, 1, 1)
        editAccountGrid.addWidget(self.editAccountAmountLabel, 2, 0)
        editAccountGrid.addLayout(editAccountHLayout, 2, 1)
        editAccountGrid.addWidget(self.editAccountPositionLabel, 3, 0)
        editAccountGrid.addWidget(self.editAccountPositionEntry, 3, 1)
        editAccountGrid.addWidget(self.editAccountNotesLabel, 4, 0)
        editAccountGrid.addWidget(self.editAccountNotesEntry, 4, 1)
        editAccountGrid.addWidget(self.editAccountCancelButton, 5, 0)
        editAccountGrid.addWidget(self.editAccountEditButton, 5, 1)
        editAccountWindowMainLayout.addLayout(editAccountGrid)

        self.setWindowTitle("Account")

    def changeCurrencySymbol(self, text):
        symbol = self.codes.get_symbol(text[:3])
        self.editAccountSymbolLabel.setText(symbol)

    def countAccounts(self):
        countAccQuery = QSqlQuery()
        countAccQuery.exec(f"SELECT COUNT(name) FROM accounts WHERE userID = {self.userID}")
        if countAccQuery.next():
            return countAccQuery.value(0)

    def exit(self):
        self.close()


class EditTransferWindow(QWidget):
    def __init__(self, parent, userID):
        super().__init__()
        self.parent = parent
        self.userID = userID
        self.initUI()

    def initUI(self):

        self.setGeometry(0, 0, 300, 120)
        self.setFont(self.parent.fontt)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        editTransferWindowMainLayout = QVBoxLayout(self)
        editTransferWindowMainLayout.setSpacing(10)

        self.editTransferAmountLabel = QLabel("Amount:")
        self.editTransferSymbolLabel = QLabel("")
        self.editTransferDateLabel = QLabel("Date:")
        self.editTransferNotesLabel = QLabel("Notes (optional):")
        self.editTransferNotesLabel.setWordWrap(True)
        self.editTransferAmountEntry = QLineEdit()
        self.editTransferAmountEntry.setMaxLength(15)
        self.editTransferDateEntry = QDateEdit()
        self.editTransferDateEntry.setCalendarPopup(True)
        self.editTransferDateEntry.setMaximumDate(QDate.currentDate())
        self.editTransferDateEntry.setDateTime(QDateTime.currentDateTime())
        self.editTransferNotesEntry = QPlainTextEdit()

        self.editTransferCancelButton = QPushButton("Cancel")
        self.editTransferCancelButton.clicked.connect(self.exit)
        self.editTransferEditButton = QPushButton("Edit")

        editTransferHLayout = QHBoxLayout()
        editTransferHLayout.setSpacing(5)
        editTransferHLayout.addWidget(self.editTransferAmountEntry)
        editTransferHLayout.addWidget(self.editTransferSymbolLabel)

        editTransferGrid = QGridLayout()
        editTransferGrid.addWidget(self.editTransferAmountLabel, 0, 0)
        editTransferGrid.addLayout(editTransferHLayout, 0, 1)
        editTransferGrid.addWidget(self.editTransferDateLabel, 1, 0)
        editTransferGrid.addWidget(self.editTransferDateEntry, 1, 1)
        editTransferGrid.addWidget(self.editTransferNotesLabel, 2, 0)
        editTransferGrid.addWidget(self.editTransferNotesEntry, 2, 1)
        editTransferGrid.addWidget(self.editTransferCancelButton, 3, 0)
        editTransferGrid.addWidget(self.editTransferEditButton, 3, 1)
        editTransferWindowMainLayout.addLayout(editTransferGrid)

        self.setWindowTitle("Transfer")

    def exit(self):
        self.close()


class EditBudgetWindow(QWidget):
    def __init__(self, parent, userID):
        super().__init__()
        self.parent = parent
        self.userID = userID
        self.initUI()

    def initUI(self):

        self.setGeometry(0, 0, 350, 450)
        self.setFont(self.parent.fontt)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        editBudgetWindowMainLayout = QVBoxLayout(self)
        editBudgetWindowMainLayout.setSpacing(10)

        self.editBudgetNameLabel = QLabel("Name:")
        self.editBudgetAmountLabel = QLabel("Amount:")
        self.editBudgetCategoryLabel = QLabel("Category:")
        self.editBudgetStartDateLabel = QLabel("Start date:")
        self.editBudgetEndDateLabel = QLabel("End date:")
        self.editBudgetNotesLabel = QLabel("Notes (optional):")
        self.editBudgetNotesLabel.setWordWrap(True)
        self.editBudgetNameEntry = QLineEdit()
        self.editBudgetNameEntry.setMaxLength(20)
        self.editBudgetAmountEntry = QLineEdit()
        self.editBudgetAmountEntry.setMaxLength(15)
        self.editBudgetSymbolLabel = QLabel("")
        self.editBudgetCategoryEntry = QComboBox()
        self.editBudgetStartDateEntry = QDateEdit()
        self.editBudgetStartDateEntry.setCalendarPopup(True)
        self.editBudgetStartDateEntry.setDateTime(QDateTime.currentDateTime())
        self.editBudgetEndDateEntry = QDateEdit()
        self.editBudgetEndDateEntry.setCalendarPopup(True)
        self.editBudgetEndDateEntry.setDateTime(QDateTime.currentDateTime())
        self.editBudgetNotesEntry = QPlainTextEdit()

        self.editBudgetCancelButton = QPushButton("Cancel")
        self.editBudgetCancelButton.clicked.connect(self.exit)
        self.editBudgetEditButton = QPushButton("Edit")

        editBudgetHLayout = QHBoxLayout()
        editBudgetHLayout.setSpacing(5)
        editBudgetHLayout.addWidget(self.editBudgetAmountEntry)
        editBudgetHLayout.addWidget(self.editBudgetSymbolLabel)

        editBudgetGrid = QGridLayout()
        editBudgetGrid.addWidget(self.editBudgetNameLabel, 0, 0)
        editBudgetGrid.addWidget(self.editBudgetNameEntry, 0, 1)
        editBudgetGrid.addWidget(self.editBudgetAmountLabel, 1, 0)
        editBudgetGrid.addLayout(editBudgetHLayout, 1, 1)
        editBudgetGrid.addWidget(self.editBudgetCategoryLabel, 2, 0)
        editBudgetGrid.addWidget(self.editBudgetCategoryEntry, 2, 1)
        editBudgetGrid.addWidget(self.editBudgetStartDateLabel, 3, 0)
        editBudgetGrid.addWidget(self.editBudgetStartDateEntry, 3, 1)
        editBudgetGrid.addWidget(self.editBudgetEndDateLabel, 4, 0)
        editBudgetGrid.addWidget(self.editBudgetEndDateEntry, 4, 1)
        editBudgetGrid.addWidget(self.editBudgetNotesLabel, 5, 0)
        editBudgetGrid.addWidget(self.editBudgetNotesEntry, 5, 1)
        editBudgetGrid.addWidget(self.editBudgetCancelButton, 6, 0)
        editBudgetGrid.addWidget(self.editBudgetEditButton, 6, 1)
        editBudgetWindowMainLayout.addLayout(editBudgetGrid)

        self.fillCategoriesComboBox()
        self.setWindowTitle("Budget")

    def fillCategoriesComboBox(self):
        budgetsCategoriesModel = QSqlTableModel()
        budgetsCategoriesModel.setTable("categories")
        budgetsCategoriesModel.setFilter(f"categoryType = 'expenses' AND userID = {self.userID}")
        budgetsCategoriesModel.setSort(2, Qt.SortOrder.AscendingOrder)
        budgetsCategoriesModel.select()
        self.editBudgetCategoryEntry.setModel(budgetsCategoriesModel)
        self.editBudgetCategoryEntry.setModelColumn(budgetsCategoriesModel.fieldIndex("name"))
        self.editBudgetCategoryEntry.addItem("All")

    def exit(self):
        self.close()


class EditCategoriesWindow(QWidget):
    def __init__(self, parent, userID):
        super().__init__()
        self.parent = parent
        self.userID = userID
        self.initUI()

    def initUI(self):

        self.setGeometry(0, 0, 300, 200)
        self.setFont(self.parent.fontt)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        editCategoriesWindowMainLayout = QVBoxLayout(self)
        editCategoriesWindowMainLayout.setSpacing(10)

        editCategoriesWindowHLayout = QHBoxLayout()

        self.expenseRadioButton = QRadioButton("Expense")
        self.incomeRadioButton = QRadioButton("Income")
        self.editCategoriesComboBox = QComboBox()
        self.expenseRadioButton.toggled.connect(self.fillCategoriesComboBox)
        self.incomeRadioButton.toggled.connect(self.fillCategoriesComboBox)

        self.editCategoriesAddButton = QPushButton("Add new category")
        self.editCategoriesEditButton = QPushButton("Edit current category")
        self.editCategoriesDeleteButton = QPushButton("Delete current category")
        self.editCategoriesClearButton = QPushButton("Cancel")
        self.editCategoriesClearButton.clicked.connect(self.exit)

        editCategoriesWindowHLayout.addWidget(self.expenseRadioButton, alignment=Qt.AlignCenter)
        editCategoriesWindowHLayout.addWidget(self.incomeRadioButton, alignment=Qt.AlignCenter)
        editCategoriesWindowMainLayout.addLayout(editCategoriesWindowHLayout)
        editCategoriesWindowMainLayout.addWidget(self.editCategoriesComboBox)
        editCategoriesWindowMainLayout.addWidget(self.editCategoriesAddButton)
        editCategoriesWindowMainLayout.addWidget(self.editCategoriesEditButton)
        editCategoriesWindowMainLayout.addWidget(self.editCategoriesDeleteButton)
        editCategoriesWindowMainLayout.addWidget(self.editCategoriesClearButton)

        self.setWindowTitle("Categories")

    def fillCategoriesComboBox(self):
        radioButton = self.sender()
        if radioButton.text() == "Expense":
            self.modelCatE = QSqlTableModel(self)
            self.modelCatE.setTable("categories")
            self.modelCatE.setFilter(f"categoryType = 'expenses' AND userID = {self.userID}")
            self.modelCatE.setSort(2, Qt.SortOrder.AscendingOrder)
            self.modelCatE.select()
            self.editCategoriesComboBox.setModel(self.modelCatE)
            self.editCategoriesComboBox.setModelColumn(self.modelCatE.fieldIndex("name"))
        if radioButton.text() == 'Income':
            self.modelCatI = QSqlTableModel(self)
            self.modelCatI.setTable("categories")
            self.modelCatI.setFilter(f"categoryType = 'income' AND userID = {self.userID}")
            self.modelCatI.setSort(2, Qt.SortOrder.AscendingOrder)
            self.modelCatI.select()
            self.editCategoriesComboBox.setModel(self.modelCatI)
            self.editCategoriesComboBox.setModelColumn(self.modelCatI.fieldIndex("name"))

    def exit(self):
        self.close()


class AddCategoryWindow(QWidget):
    def __init__(self, parent, title):
        super().__init__()
        self.parent = parent
        self.title = title
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 300, 100)
        self.setFont(self.parent.fontt)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.addCategoryWindowMainLayout = QVBoxLayout(self)
        self.addCategoryWindowMainLayout.setSpacing(10)

        addCategoryWindowGridLayout = QGridLayout()

        self.addCategoryNameLabel = QLabel("Name:")
        self.addCategoryTypeLabel = QLabel("Type:")
        self.addCategoryNameEntry = QLineEdit()
        self.addCategoryNameEntry.setMaxLength(20)
        self.addCategoryTypeEntry = QComboBox()
        self.addCategoryTypeEntry.addItem('Expense')
        self.addCategoryTypeEntry.addItem('Income')
        self.addCategoryAddButton = QPushButton("Add")

        addCategoryWindowGridLayout.addWidget(self.addCategoryNameLabel, 0, 0)
        addCategoryWindowGridLayout.addWidget(self.addCategoryNameEntry, 0, 1)
        addCategoryWindowGridLayout.addWidget(self.addCategoryTypeLabel, 1, 0)
        addCategoryWindowGridLayout.addWidget(self.addCategoryTypeEntry, 1, 1)
        self.addCategoryWindowMainLayout.addLayout(addCategoryWindowGridLayout)
        self.addCategoryWindowMainLayout.addWidget(self.addCategoryAddButton)

        self.setWindowTitle(self.title)

    def exit(self):
        self.close()


class EditCategoryWindow(QWidget):
    def __init__(self, parent, title, categoryType):
        super().__init__()
        self.parent = parent
        self.title = title
        self.categoryType = categoryType
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 300, 100)
        self.setFont(self.parent.fontt)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.editCategoryWindowMainLayout = QVBoxLayout(self)
        self.editCategoryWindowMainLayout.setSpacing(10)

        editCategoryWindowGridLayout = QGridLayout()

        self.editCategoryNameLabel = QLabel("Name:")
        self.editCategoryPositionLabel = QLabel("Position:")
        self.editCategoryNameEntry = QLineEdit()
        self.editCategoryNameEntry.setMaxLength(20)
        self.editCategoryPositionEntry = QSpinBox()
        self.editCategoryPositionEntry.setMinimum(1)
        self.editCategoryPositionEntry.setMaximum(self.countCategories(self.categoryType))
        self.editCategoryButton = QPushButton("Edit")

        editCategoryWindowGridLayout.addWidget(self.editCategoryNameLabel, 0, 0)
        editCategoryWindowGridLayout.addWidget(self.editCategoryNameEntry, 0, 1)
        editCategoryWindowGridLayout.addWidget(self.editCategoryPositionLabel, 1, 0)
        editCategoryWindowGridLayout.addWidget(self.editCategoryPositionEntry, 1, 1)
        self.editCategoryWindowMainLayout.addLayout(editCategoryWindowGridLayout)
        self.editCategoryWindowMainLayout.addWidget(self.editCategoryButton)

        self.setWindowTitle(self.title)

    def countCategories(self, categoryType):
        countCatQuery = QSqlQuery()
        countCatQuery.exec(f"SELECT COUNT(name) FROM categories WHERE categoryType = '{categoryType}' AND userID = {self.parent.userID}")
        if countCatQuery.next():
            return countCatQuery.value(0)

    def exit(self):
        self.close()
