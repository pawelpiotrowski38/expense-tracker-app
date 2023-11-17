from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLabel, QLineEdit, QGridLayout, QPushButton, \
    QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QComboBox, QSplitter, QFileDialog
from forex_python.converter import CurrencyCodes, CurrencyRates
from decimal import Decimal
from datetime import datetime
from pandas import read_csv


# noinspection PyAttributeOutsideInit
class ImportWindow(QWidget):
    def __init__(self, parent, userID, currency, con):
        super().__init__()
        self.parent = parent
        self.userID = userID
        self.currency = currency
        self.codes = CurrencyCodes()
        self.rates = CurrencyRates()
        self.con = con
        self.initUI()

    def initUI(self):

        width = self.frameGeometry().width()

        self.setGeometry(0, 0, 700, 250)
        font = self.font()
        font.setPointSize(12)
        self.window().setFont(font)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        importLayout = QVBoxLayout(self)

        leftImportPanel = QFrame()
        leftImportPanel.setFrameShape(QFrame.StyledPanel)
        leftImportPanelVLayout = QVBoxLayout(leftImportPanel)

        self.importFileNameLine = QLineEdit()
        self.importFileNameLine.setReadOnly(True)
        self.importFileNameLabel = QLabel("File name:")
        self.importFileNameButton = QPushButton("Choose file")
        self.importFileNameButton.clicked.connect(self.chooseFile)
        self.importAccountLabel = QLabel("Account:")
        self.importAccountEntry = QComboBox()
        self.modelAcc = QSqlTableModel()
        self.modelAcc.setTable("accounts")
        self.modelAcc.setFilter(f"userID = {self.userID}")
        self.modelAcc.setSort(5, Qt.SortOrder.AscendingOrder)
        self.modelAcc.select()
        self.importAccountEntry.setModel(self.modelAcc)
        self.importAccountEntry.setModelColumn(self.modelAcc.fieldIndex("name"))
        self.importTypeLabel = QLabel("Type:")
        self.importTypeEntry = QComboBox()
        self.importTypeEntry.addItems(["Expenses", "Income"])

        leftImportFileGridLayout = QGridLayout()
        leftImportFileGridLayout.addWidget(self.importFileNameLabel, 0, 0)
        leftImportFileGridLayout.addWidget(self.importFileNameButton, 0, 1)
        leftImportFileGridLayout.addWidget(self.importAccountLabel, 1, 0)
        leftImportFileGridLayout.addWidget(self.importAccountEntry, 1, 1)
        leftImportFileGridLayout.addWidget(self.importTypeLabel, 2, 0)
        leftImportFileGridLayout.addWidget(self.importTypeEntry, 2, 1)

        leftImportPanelVLayout.addWidget(self.importFileNameLine, alignment=Qt.AlignTop)
        leftImportPanelVLayout.addLayout(leftImportFileGridLayout)

        rightImportPanel = QFrame()
        rightImportPanel.setFrameShape(QFrame.StyledPanel)
        rightImportPanelVLayout = QVBoxLayout(rightImportPanel)

        self.importMappingLabel = QLabel("Mapping columns")

        self.importMappingAmount = QLabel("Amount:")
        self.importMappingCategory = QLabel("Category:")
        self.importMappingDate = QLabel("Date:")
        self.importMappingCurrency = QLabel("Currency:")
        self.importMappingNotes = QLabel("Notes:")
        self.importMappingAmountComboBox = QComboBox()
        self.importMappingCategoryComboBox = QComboBox()
        self.importMappingDateComboBox = QComboBox()
        self.importMappingCurrencyComboBox = QComboBox()
        self.importMappingNotesComboBox = QComboBox()

        importMappingGrid = QGridLayout()
        importMappingGrid.addWidget(self.importMappingAmount, 0, 0)
        importMappingGrid.addWidget(self.importMappingAmountComboBox, 0, 1)
        importMappingGrid.addWidget(self.importMappingCategory, 1, 0)
        importMappingGrid.addWidget(self.importMappingCategoryComboBox, 1, 1)
        importMappingGrid.addWidget(self.importMappingDate, 2, 0)
        importMappingGrid.addWidget(self.importMappingDateComboBox, 2, 1)
        importMappingGrid.addWidget(self.importMappingCurrency, 3, 0)
        importMappingGrid.addWidget(self.importMappingCurrencyComboBox, 3, 1)
        importMappingGrid.addWidget(self.importMappingNotes, 4, 0)
        importMappingGrid.addWidget(self.importMappingNotesComboBox, 4, 1)

        rightImportPanelVLayout.addWidget(self.importMappingLabel, alignment=Qt.AlignCenter)
        rightImportPanelVLayout.addLayout(importMappingGrid)

        self.importCancelButton = QPushButton("Cancel")
        self.importCancelButton.clicked.connect(self.exit)
        self.importImportButton = QPushButton("Import")
        self.importImportButton.clicked.connect(self.importTr)
        importButtonsHBoxLayout = QHBoxLayout()
        importButtonsHBoxLayout.addWidget(self.importCancelButton, alignment=Qt.AlignRight)
        importButtonsHBoxLayout.addWidget(self.importImportButton, alignment=Qt.AlignLeft)

        splitterImport = QSplitter(Qt.Horizontal)
        splitterImport.addWidget(leftImportPanel)
        splitterImport.addWidget(rightImportPanel)
        splitterImport.setSizes([int(width * 0.6), int(width * 0.4)])

        importLayout.addWidget(splitterImport)
        importLayout.addLayout(importButtonsHBoxLayout)

    def chooseFile(self):
        fileDialog = QFileDialog()
        self.path = fileDialog.getOpenFileName(filter="csv(*.csv)")
        if not self.path[0]:
            return
        self.importFileNameLine.setText(self.path[0])

        columnsList = list(read_csv(self.path[0], nrows=0).columns)
        self.importMappingAmountComboBox.addItems(columnsList)
        self.importMappingCategoryComboBox.addItems(columnsList)
        self.importMappingDateComboBox.addItems(columnsList)
        self.importMappingCurrencyComboBox.addItems(columnsList)
        self.importMappingNotesComboBox.addItems(columnsList)
        self.importMappingNotesComboBox.addItem("Ignore")

    def importTr(self):
        importMsg = QMessageBox()
        importMsg.setWindowTitle("Warning")
        importMsg.setIcon(QMessageBox.Warning)

        columnsList = [self.importMappingAmountComboBox.currentText(), self.importMappingCategoryComboBox.currentText(),
                       self.importMappingDateComboBox.currentText(), self.importMappingCurrencyComboBox.currentText()]
        if self.importMappingNotesComboBox.currentText() != "Ignore":
            columnsList.append(self.importMappingNotesComboBox.currentText())
        columnsSet = set(columnsList)
        if not self.importMappingAmountComboBox.currentText() or not self.importMappingCategoryComboBox.currentText() \
            or not self.importMappingDateComboBox.currentText() or not self.importMappingCurrencyComboBox.currentText() \
                or not self.importMappingNotesComboBox.currentText():
            importMsg.setText("All mapping items must be selected!")
            importMsg.exec()
            return
        if len(columnsSet) != len(columnsList):
            importMsg.setText("All mapping items must be unique!")
            importMsg.exec()
            return

        importQuery = QSqlQuery()
        type_t = self.importTypeEntry.currentText().lower()
        df = read_csv(self.path[0])
        failCount = 0
        for index, row in df.iterrows():
            amount = row[self.importMappingAmountComboBox.currentText()]
            category = row[self.importMappingCategoryComboBox.currentText()]
            date_t = row[self.importMappingDateComboBox.currentText()]
            date_t = datetime.strptime(date_t, '%Y-%m-%d').date()
            currency = row[self.importMappingCurrencyComboBox.currentText()]
            if self.importMappingNotesComboBox.currentText() == "Ignore":
                notes = ""
            else:
                notes = str(row[self.importMappingNotesComboBox.currentText()])
                if notes == "nan":
                    notes = ""

            account = self.importAccountEntry.currentText()
            userID = self.userID

            findIDQuery = QSqlQuery()
            findIDQuery.prepare("SELECT categoryID FROM categories WHERE name = :name AND categoryType = :tableName AND userID = :userID")
            findIDQuery.bindValue(":name", category)
            findIDQuery.bindValue(":tableName", type_t)
            findIDQuery.bindValue(":userID", userID)
            findIDQuery.exec()
            if findIDQuery.next():
                categoryID = findIDQuery.value(0)
            else:
                failCount += 1
                continue
            findIDQuery.prepare("SELECT accountID FROM accounts WHERE name = :name AND userID = :userID")
            findIDQuery.bindValue(":name", account)
            findIDQuery.bindValue(":userID", userID)
            findIDQuery.exec()
            if findIDQuery.next():
                accountID = findIDQuery.value(0)
            else:
                return
            codesList = ['EUR', 'IDR', 'BGN', 'ILS', 'GBP', 'DKK', 'CAD', 'JPY', 'HUF', 'RON', 'MYR', 'SEK', 'SGD',
                         'HKD', 'AUD', 'CHF', 'KRW', 'CNY', 'TRY', 'HRK', 'NZD', 'THB', 'USD', 'NOK', 'RUB', 'INR',
                         'MXN', 'CZK', 'BRL', 'PLN', 'PHP', 'ZAR']
            if currency.upper() not in codesList:
                failCount += 1
                continue
            if currency.upper() == self.currency:
                originValue = Decimal(''.join(i for i in amount if i.isdigit() or i == '.'))
                value = originValue
            else:
                originValue = Decimal(''.join(i for i in amount if i.isdigit() or i == '.'))
                value = originValue
            importQuery.prepare(f"INSERT INTO {type_t} (amount, categoryID, accountID, transactionDate, notes, value, originValue, currency, userID) "
                                f"VALUES (:amount, :category, :account, '{date_t}', :notes, {value}, {originValue}, :currency, :userID)")
            importQuery.bindValue(":amount", amount)
            importQuery.bindValue(":category", categoryID)
            importQuery.bindValue(":account", accountID)
            importQuery.bindValue(":notes", notes)
            importQuery.bindValue(":currency", currency)
            importQuery.bindValue(":userID", userID)

            if importQuery.exec():
                importQuery.prepare("SELECT currAmount FROM accounts WHERE accountID = :account AND userID = :userID")
                importQuery.bindValue(":account", accountID)
                importQuery.bindValue(":userID", userID)
                importQuery.exec()
                if importQuery.next():
                    currAmount = Decimal(importQuery.value(0))
                    if type_t == "expenses":
                        newAmount = currAmount - originValue
                    else:
                        newAmount = currAmount + originValue
                    importQuery.prepare(f"UPDATE accounts SET currAmount = {newAmount} "
                                        "WHERE accountID = :account")
                    importQuery.bindValue(":account", accountID)
                    if not importQuery.exec():
                        print(importQuery.lastError().databaseText())
            else:
                print(importQuery.lastError().databaseText())
                return
        self.parent.fillTransactionTable()
        self.parent.fillAccountsTable()
        self.parent.fillSummaryPanel(self.parent.theme)
        self.parent.fillDailyCharts(self.parent.theme)
        importMsg.setWindowTitle("Info")
        importMsg.setIcon(QMessageBox.Information)
        importMsg.setText(f"Transactions have been imported.\n\n{failCount} import(s) failed.")
        importMsg.exec()
        self.exit()

    def exit(self):
        self.close()
