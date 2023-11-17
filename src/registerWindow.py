import bcrypt
import random
import re
import smtplib
import ssl
import string
from email.message import EmailMessage
from forex_python.converter import CurrencyCodes
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLabel, QLineEdit, QGridLayout, QPushButton, \
    QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QDialog
from credentials import emailPassword

MAILPASSWORD = emailPassword


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 380, 320)
        registerWindowFont = self.font()
        registerWindowFont.setPointSize(12)
        self.window().setFont(registerWindowFont)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.registerWindowEmailLabel = QLabel('E-mail:')
        self.registerWindowEmailEntry = QLineEdit()
        self.registerWindowEmailEntry.setMaxLength(40)
        self.registerWindowLoginLabel = QLabel('Username:')
        self.registerWindowLoginEntry = QLineEdit()
        self.registerWindowLoginEntry.setMaxLength(20)
        self.registerWindowPasswordLabel = QLabel('Password:')
        self.registerWindowPasswordEntry = QLineEdit()
        self.registerWindowPasswordEntry.setMaxLength(20)
        self.registerWindowPasswordEntry.setEchoMode(QLineEdit.Password)
        self.registerWindowConfirmPasswordLabel = QLabel('Confirm password:')
        self.registerWindowConfirmPasswordLabel.setWordWrap(True)
        self.registerWindowConfirmPasswordEntry = QLineEdit()
        self.registerWindowConfirmPasswordEntry.setMaxLength(20)
        self.registerWindowConfirmPasswordEntry.setEchoMode(QLineEdit.Password)
        self.registerWindowCurrencyLabel = QLabel('Currency:')
        self.registerWindowCurrencyComboBox = QComboBox()
        codesList = ['EUR', 'IDR', 'BGN', 'ILS', 'GBP', 'DKK', 'CAD', 'JPY', 'HUF', 'RON', 'MYR', 'SEK', 'SGD', 'HKD',
                     'AUD', 'CHF', 'KRW', 'CNY', 'TRY', 'HRK', 'NZD', 'THB', 'USD', 'NOK', 'RUB', 'INR', 'MXN', 'CZK',
                     'BRL', 'PLN', 'PHP', 'ZAR']
        code = CurrencyCodes()
        for i in codesList:
            name = code.get_currency_name(i)
            item = i + ' - ' + name
            self.registerWindowCurrencyComboBox.addItem(item)
        self.registerWindowCurrencyComboBox.setCurrentText("PLN - Polish zloty")
        self.registerWindowThemeLabel = QLabel('Theme:')
        self.registerWindowThemeEntry = QComboBox()
        self.registerWindowThemeEntry.addItems(["Light theme", "Dark theme"])

        registerWindowGridLayout = QGridLayout()
        registerWindowGridLayout.addWidget(self.registerWindowEmailLabel, 0, 0)
        registerWindowGridLayout.addWidget(self.registerWindowEmailEntry, 0, 1)
        registerWindowGridLayout.addWidget(self.registerWindowLoginLabel, 1, 0)
        registerWindowGridLayout.addWidget(self.registerWindowLoginEntry, 1, 1)
        registerWindowGridLayout.addWidget(self.registerWindowPasswordLabel, 2, 0)
        registerWindowGridLayout.addWidget(self.registerWindowPasswordEntry, 2, 1)
        registerWindowGridLayout.addWidget(self.registerWindowConfirmPasswordLabel, 3, 0)
        registerWindowGridLayout.addWidget(self.registerWindowConfirmPasswordEntry, 3, 1)
        registerWindowGridLayout.addWidget(self.registerWindowCurrencyLabel, 4, 0)
        registerWindowGridLayout.addWidget(self.registerWindowCurrencyComboBox, 4, 1)
        registerWindowGridLayout.addWidget(self.registerWindowThemeLabel, 5, 0)
        registerWindowGridLayout.addWidget(self.registerWindowThemeEntry, 5, 1)

        self.registerWindowRegisterButton = QPushButton('Register')
        self.registerWindowRegisterButton.clicked.connect(self.register)
        self.registerWindowCancelButton = QPushButton('Cancel')
        self.registerWindowCancelButton.clicked.connect(self.exit)

        registerWindowMainLayout = QVBoxLayout(self)
        registerWindowMainLayout.setSpacing(10)
        registerWindowMainLayout.addLayout(registerWindowGridLayout)
        registerWindowMainLayout.addWidget(self.registerWindowRegisterButton)
        registerWindowMainLayout.addWidget(self.registerWindowCancelButton)

        self.setWindowTitle("Register")
        self.show()

    def validateEmailAddress(self, address):
        expression = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(expression, address):
            return True
        else:
            return False

    def sendActivationCode(self, address):
        msg = EmailMessage()
        msg['Subject'] = "Account activation"
        msg['From'] = "konto.testowe467@gmail.com"
        msg['To'] = address

        port = 465
        smtp = "smtp.gmail.com"
        password = MAILPASSWORD
        code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(5))
        msg.set_content(f"Activation code: {code}\nIf you did not create the account, please ignore this message.")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp, port, context=context) as server:
            server.login("konto.testowe467@gmail.com", password)
            server.send_message(msg)

        return code

    def register(self):
        registerMsg = QMessageBox()
        registerMsg.setWindowTitle("Warning")
        registerMsg.setIcon(QMessageBox.Warning)
        characters = " !\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"

        email = self.registerWindowEmailEntry.text()
        login = self.registerWindowLoginEntry.text()
        password = self.registerWindowPasswordEntry.text()
        confirmPassword = self.registerWindowConfirmPasswordEntry.text()
        currency = self.registerWindowCurrencyComboBox.currentText()[:3]
        theme = self.registerWindowThemeEntry.currentText()

        if not self.validateEmailAddress(email):
            registerMsg.setText("Invalid email address!")
            registerMsg.exec()
            return

        findUser = QSqlQuery()
        findUser.prepare("SELECT email FROM users WHERE email = :email")
        findUser.bindValue(":email", email)
        findUser.exec()
        if findUser.next():
            registerMsg.setText("That email address is already in use!\nPlease use a different email address.")
            registerMsg.exec()
            return
        findUser.prepare("SELECT login FROM users WHERE login = :login")
        findUser.bindValue(":login", login)
        findUser.exec()
        if findUser.next():
            registerMsg.setText("Such user already exists!")
            registerMsg.exec()
            return
        elif len(login) < 5:
            registerMsg.setText("Username must be at least 5 characters long!")
            registerMsg.exec()
            return
        elif any(char in characters for char in login):
            registerMsg.setText("Username can only contain letters, digits and underscores!")
            registerMsg.exec()
            return
        elif not password == confirmPassword:
            registerMsg.setText("Password and confirmation password do not match!")
            registerMsg.exec()
            return
        elif len(password) < 5:
            registerMsg.setText("Password must be at least 5 characters long!")
            registerMsg.exec()
            return
        elif re.search('[0-9]', password) is None or re.search('[A-Z]', password) is None:
            registerMsg.setText("Password must contain at least one digit and one capital letter!")
            registerMsg.exec()
            return
        if theme == "Light theme":
            theme = 0
        elif theme == "Dark theme":
            theme = 1

        passwordHash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        passwordHashStr = passwordHash.decode()

        code = self.sendActivationCode(email)
        activateWindow = ActivateWindow(self, code, email, login, passwordHashStr, currency, theme)
        activateWindow.exec()

    def exit(self):
        self.close()


class ActivateWindow(QDialog):
    def __init__(self, parent, code, email, login, passwordHashStr, currency, theme):
        super().__init__()
        self.parent = parent
        self.codes = code
        self.email = email
        self.login = login
        self.passwordHashStr = passwordHashStr
        self.currency = currency
        self.theme = theme
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 350, 175)
        loginWindowFont = self.font()
        loginWindowFont.setPointSize(12)
        self.window().setFont(loginWindowFont)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.activateWindowInformationLabel = QLabel(
            'To complete the registration, enter the activation code sent to the e-mail address provided.')
        self.activateWindowInformationLabel.setWordWrap(True)
        self.activateWindowInformationEntry = QLineEdit()

        self.activateWindowCancelButton = QPushButton('Cancel')
        self.activateWindowCancelButton.clicked.connect(self.exit)
        self.activateWindowActivateButton = QPushButton('Activate')
        self.activateWindowActivateButton.clicked.connect(self.check)

        activateWindowHLayout = QHBoxLayout()
        activateWindowHLayout.addWidget(self.activateWindowCancelButton)
        activateWindowHLayout.addWidget(self.activateWindowActivateButton)

        activateWindowMainLayout = QVBoxLayout(self)
        activateWindowMainLayout.setSpacing(10)
        activateWindowMainLayout.addWidget(self.activateWindowInformationLabel)
        activateWindowMainLayout.addWidget(self.activateWindowInformationEntry)
        activateWindowMainLayout.addLayout(activateWindowHLayout)

        self.setWindowTitle("Activate account")

    def check(self):
        activateMsg = QMessageBox()
        enteredCode = self.activateWindowInformationEntry.text()
        if enteredCode == self.codes:
            registerQuery = QSqlQuery()
            registerQuery.prepare("INSERT INTO users (email, login, password, currency, darkMode, font, fontSize) "
                                  "VALUES (:email, :login, :password, :currency, :theme, :font, :fontSize)")
            registerQuery.bindValue(":email", self.email)
            registerQuery.bindValue(":login", self.login)
            registerQuery.bindValue(":password", self.passwordHashStr)
            registerQuery.bindValue(":currency", self.currency)
            registerQuery.bindValue(":theme", self.theme)
            registerQuery.bindValue(":font", "Arial")
            registerQuery.bindValue(":fontSize", 12)
            if registerQuery.exec():
                registerQuery.prepare("SELECT userID from users WHERE login = :login;")
                registerQuery.bindValue(":login", self.login)
                registerQuery.exec()
                if registerQuery.next():
                    userID = registerQuery.value(0)
                else:
                    registerQuery.finish()
                    return

                if not registerQuery.exec(f"INSERT INTO categories (name, categoryType, position, userID) VALUES ('Shopping', 'expenses', 1, {userID})"):
                    print(registerQuery.lastError().databaseText())
                registerQuery.exec(f"INSERT INTO categories (name, categoryType, position, userID) VALUES ('Bills', 'expenses', 2, {userID})")
                registerQuery.exec(f"INSERT INTO categories (name, categoryType, position, userID) VALUES ('Transport', 'expenses', 3, {userID})")
                registerQuery.exec(f"INSERT INTO categories (name, categoryType, position, userID) VALUES ('Health', 'expenses', 4, {userID})")
                registerQuery.exec(f"INSERT INTO categories (name, categoryType, position, userID) VALUES ('Other', 'expenses', 5, {userID})")
                registerQuery.exec(f"INSERT INTO categories (name, categoryType, position, userID) VALUES ('Salary', 'income', 1, {userID})")
                registerQuery.exec(f"INSERT INTO categories (name, categoryType, position, userID) VALUES ('Other', 'income', 2, {userID})")
                registerQuery.finish()
                activateMsg.setWindowTitle("Success")
                activateMsg.setIcon(QMessageBox.Information)
                activateMsg.setText("Registration successful!")
                activateMsg.exec()
                self.close()
                self.parent.close()
            else:
                print(registerQuery.lastError().databaseText())
            registerQuery.finish()
        else:
            activateMsg.setWindowTitle("Warning")
            activateMsg.setIcon(QMessageBox.Warning)
            activateMsg.setText("Incorrect code!")
            activateMsg.exec()

    def exit(self):
        self.close()
