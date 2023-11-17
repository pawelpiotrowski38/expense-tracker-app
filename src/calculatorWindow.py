from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLabel, QLineEdit, QGridLayout, QPushButton, \
    QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox
from forex_python.converter import CurrencyRates, CurrencyCodes
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from sympy import sympify, SympifyError
from functools import partial


class CalculatorWindow(QWidget):
    def __init__(self, parent, userID):
        super().__init__()
        self.parent = parent
        self.userID = userID
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 250, 300)
        font = self.font()
        font.setFamily(self.parent.fontName)
        font.setPointSize(self.parent.fontSize)
        self.window().setFont(font)
        self.window().setWindowTitle('Calculator')
        self.window().setWindowIcon(QIcon('calc.png'))

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        calculatorWindowMainLayout = QVBoxLayout(self)
        calculatorWindowMainLayout.setSpacing(10)

        self.button1 = QPushButton('C')
        self.button1.setFixedSize(40, 40)
        self.button1.clicked.connect(self.clearDisplay)
        self.button2 = QPushButton('(')
        self.button2.setFixedSize(40, 40)
        self.button2.clicked.connect(partial(self.action, '('))
        self.button3 = QPushButton(')')
        self.button3.setFixedSize(40, 40)
        self.button3.clicked.connect(partial(self.action, ')'))
        self.button4 = QPushButton('+')
        self.button4.setFixedSize(40, 40)
        self.button4.clicked.connect(partial(self.action, '+'))
        self.button5 = QPushButton('7')
        self.button5.setFixedSize(40, 40)
        self.button5.clicked.connect(partial(self.action, '7'))
        self.button6 = QPushButton('8')
        self.button6.setFixedSize(40, 40)
        self.button6.clicked.connect(partial(self.action, '8'))
        self.button7 = QPushButton('9')
        self.button7.setFixedSize(40, 40)
        self.button7.clicked.connect(partial(self.action, '9'))
        self.button8 = QPushButton('-')
        self.button8.setFixedSize(40, 40)
        self.button8.clicked.connect(partial(self.action, '-'))
        self.button9 = QPushButton('4')
        self.button9.setFixedSize(40, 40)
        self.button9.clicked.connect(partial(self.action, '4'))
        self.button10 = QPushButton('5')
        self.button10.setFixedSize(40, 40)
        self.button10.clicked.connect(partial(self.action, '5'))
        self.button11 = QPushButton('6')
        self.button11.setFixedSize(40, 40)
        self.button11.clicked.connect(partial(self.action, '6'))
        self.button12 = QPushButton('*')
        self.button12.setFixedSize(40, 40)
        self.button12.clicked.connect(partial(self.action, '*'))
        self.button13 = QPushButton('1')
        self.button13.setFixedSize(40, 40)
        self.button13.clicked.connect(partial(self.action, '1'))
        self.button14 = QPushButton('2')
        self.button14.setFixedSize(40, 40)
        self.button14.clicked.connect(partial(self.action, '2'))
        self.button15 = QPushButton('3')
        self.button15.setFixedSize(40, 40)
        self.button15.clicked.connect(partial(self.action, '3'))
        self.button16 = QPushButton('/')
        self.button16.setFixedSize(40, 40)
        self.button16.clicked.connect(partial(self.action, '/'))
        self.button17 = QPushButton('00')
        self.button17.setFixedSize(40, 40)
        self.button17.clicked.connect(partial(self.action, '00'))
        self.button18 = QPushButton('0')
        self.button18.setFixedSize(40, 40)
        self.button18.clicked.connect(partial(self.action, '0'))
        self.button19 = QPushButton('.')
        self.button19.setFixedSize(40, 40)
        self.button19.clicked.connect(partial(self.action, '.'))
        self.button20 = QPushButton('=')
        self.button20.setFixedSize(40, 40)
        self.button20.clicked.connect(self.actionEqual)

        self.display = QLineEdit()
        self.display.setFixedHeight(35)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)

        self.converterButton = QPushButton('Currency converter')

        calculatorGrid = QGridLayout()
        calculatorGrid.addWidget(self.button1, 0, 0)
        calculatorGrid.addWidget(self.button2, 0, 1)
        calculatorGrid.addWidget(self.button3, 0, 2)
        calculatorGrid.addWidget(self.button4, 0, 3)
        calculatorGrid.addWidget(self.button5, 1, 0)
        calculatorGrid.addWidget(self.button6, 1, 1)
        calculatorGrid.addWidget(self.button7, 1, 2)
        calculatorGrid.addWidget(self.button8, 1, 3)
        calculatorGrid.addWidget(self.button9, 2, 0)
        calculatorGrid.addWidget(self.button10, 2, 1)
        calculatorGrid.addWidget(self.button11, 2, 2)
        calculatorGrid.addWidget(self.button12, 2, 3)
        calculatorGrid.addWidget(self.button13, 3, 0)
        calculatorGrid.addWidget(self.button14, 3, 1)
        calculatorGrid.addWidget(self.button15, 3, 2)
        calculatorGrid.addWidget(self.button16, 3, 3)
        calculatorGrid.addWidget(self.button17, 4, 0)
        calculatorGrid.addWidget(self.button18, 4, 1)
        calculatorGrid.addWidget(self.button19, 4, 2)
        calculatorGrid.addWidget(self.button20, 4, 3)

        calculatorWindowMainLayout.addWidget(self.display)
        calculatorWindowMainLayout.addLayout(calculatorGrid)
        calculatorWindowMainLayout.addWidget(self.converterButton)

    def action(self, a):
        text = self.display.text()
        self.display.setText(text + a)

    def actionEqual(self):
        equation = self.display.text()
        try:
            ans = str(sympify(equation).evalf()).strip("0")
            if ans[-1] == '.':
                ans = ans[:-1]
            self.display.setText(ans)
        except (TypeError, AttributeError, SympifyError):
            self.display.setText('Error')

    def clearDisplay(self):
        self.display.setText('')

    def exit(self):
        self.close()


class ConverterWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):

        codesList = ['EUR', 'IDR', 'BGN', 'ILS', 'GBP', 'DKK', 'CAD', 'JPY', 'HUF', 'RON', 'MYR', 'SEK', 'SGD', 'HKD',
                     'AUD', 'CHF', 'KRW', 'CNY', 'TRY', 'HRK', 'NZD', 'THB', 'USD', 'NOK', 'RUB', 'INR', 'MXN', 'CZK',
                     'BRL', 'PLN', 'PHP', 'ZAR']
        code = CurrencyCodes()
        self.setGeometry(0, 0, 350, 200)
        font = self.font()
        font.setFamily(self.parent.fontName)
        font.setPointSize(self.parent.fontSize)
        self.window().setFont(font)
        self.window().setWindowTitle('Currency Converter')

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        converterWindowMainLayout = QVBoxLayout(self)
        converterWindowMainLayout.setSpacing(10)
        hLayout1 = QHBoxLayout()
        hLayout2 = QHBoxLayout()

        self.symbolFromLabel = QLabel('€')
        self.symbolToLabel = QLabel('€')
        self.currencyFromLabel = QLabel('From:')
        self.currencyFromBox = QComboBox()
        self.currencyFromBox.currentIndexChanged.connect(lambda: self.indexChanged('f', code))
        self.currencyToLabel = QLabel('Amount:')
        self.currencyToBox = QComboBox()
        for i in codesList:
            name = code.get_currency_name(i)
            item = i + ' - ' + name
            self.currencyFromBox.addItem(item)
            self.currencyToBox.addItem(item)
        self.currencyToBox.currentIndexChanged.connect(lambda: self.indexChanged('t', code))
        self.amountFromLabel = QLabel('To:')
        self.amountFrom = QLineEdit()
        self.amountToLabel = QLabel('Result:')
        self.amountTo = QLineEdit()
        self.amountTo.setReadOnly(True)

        self.convertButton = QPushButton('Convert')
        self.convertButton.clicked.connect(self.convert)

        hLayout1.addWidget(self.amountFrom)
        hLayout1.addWidget(self.symbolFromLabel)
        hLayout2.addWidget(self.amountTo)
        hLayout2.addWidget(self.symbolToLabel)

        converterGrid = QGridLayout()
        converterGrid.addWidget(self.currencyFromLabel, 0, 0)
        converterGrid.addWidget(self.currencyFromBox, 0, 1)
        converterGrid.addWidget(self.currencyToLabel, 1, 0)
        converterGrid.addLayout(hLayout1, 1, 1)
        converterGrid.addWidget(self.amountFromLabel, 2, 0)
        converterGrid.addWidget(self.currencyToBox, 2, 1)
        converterGrid.addWidget(self.amountToLabel, 3, 0)
        converterGrid.addLayout(hLayout2, 3, 1)

        converterWindowMainLayout.addLayout(converterGrid)
        converterWindowMainLayout.addWidget(self.convertButton)

    def indexChanged(self, opt, code):
        if opt == 'f':
            name = self.currencyFromBox.currentText()
            name = name[:3]
            symbol = code.get_symbol(name)
            self.symbolFromLabel.setText(symbol)
        else:
            name = self.currencyToBox.currentText()
            name = name[:3]
            symbol = code.get_symbol(name)
            self.symbolToLabel.setText(symbol)

    def convert(self):
        convertMsg = QMessageBox()
        cents = Decimal('0.01')
        symbolFrom = self.currencyFromBox.currentText()[:3]
        symbolTo = self.currencyToBox.currentText()[:3]

        try:
            amount = Decimal(self.amountFrom.text()).quantize(cents, ROUND_HALF_UP)
        except InvalidOperation:
            convertMsg.setWindowTitle("Warning")
            convertMsg.setIcon(QMessageBox.Warning)
            convertMsg.setText("Amount must be a number!")
            convertMsg.exec()
            return

        rates = CurrencyRates()
        rate = Decimal(rates.get_rate(symbolFrom, symbolTo))

        result = amount * rate
        self.amountTo.setText(str(result.quantize(cents, ROUND_HALF_UP)))

    def exit(self):
        self.close()
