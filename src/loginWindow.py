import bcrypt
import random
import re
import smtplib
import ssl
import string
import sys
from email.message import EmailMessage
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtSql import QSqlQuery, QSqlDatabase
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLabel, QLineEdit, QGridLayout, QPushButton, \
    QVBoxLayout, QHBoxLayout, QStackedLayout, QMessageBox
from credentials import databaseLogin, databasePassword, emailPassword
from mainWindow import MainWindow
from registerWindow import RegisterWindow

SERVER = '192.168.1.18,1433'
DATABASE = 'Baza'
USERNAME = databaseLogin
PASSWORD = databasePassword
MAILPASSWORD = emailPassword


class LoginWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.defaultPalette = self.palette()
        self.initUI()
        self.databaseConnect()
        self.setAttribute(Qt.WA_DeleteOnClose)

    def initUI(self):
        self.setGeometry(0, 0, 300, 200)
        loginWindowFont = self.font()
        loginWindowFont.setPointSize(12)
        self.window().setFont(loginWindowFont)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.loginWindowLoginLabel = QLabel('Username:')
        self.loginWindowLoginEntry = QLineEdit()
        self.loginWindowLoginEntry.setMaxLength(20)
        self.loginWindowLoginEntry.returnPressed.connect(self.login)
        self.loginWindowPasswordLabel = QLabel('Password:')
        self.loginWindowPasswordEntry = QLineEdit()
        self.loginWindowPasswordEntry.setMaxLength(20)
        self.loginWindowPasswordEntry.returnPressed.connect(self.login)
        self.loginWindowPasswordEntry.setEchoMode(QLineEdit.Password)

        loginWindowGridLayout = QGridLayout()
        loginWindowGridLayout.addWidget(self.loginWindowLoginLabel, 0, 0)
        loginWindowGridLayout.addWidget(self.loginWindowLoginEntry, 0, 1)
        loginWindowGridLayout.addWidget(self.loginWindowPasswordLabel, 1, 0)
        loginWindowGridLayout.addWidget(self.loginWindowPasswordEntry, 1, 1)

        self.loginWindowForgotPasswordLabel = ForgotPasswordLabel()
        self.loginWindowForgotPasswordLabel.setText('Forgot password')
        self.loginWindowForgotPasswordLabel.setCursor(QCursor(Qt.PointingHandCursor))
        self.loginWindowForgotPasswordLabel.setStyleSheet("QLabel { font-size : 15px; color : rgb(65, 65, 255); }")
        self.loginWindowForgotPasswordLabel.clicked.connect(self.resetPassword)
        self.loginWindowLoginButton = QPushButton('Log in')
        self.loginWindowLoginButton.clicked.connect(self.login)
        self.loginWindowRegisterButton = QPushButton('Register')
        self.loginWindowRegisterButton.clicked.connect(self.register)
        self.loginWindowExitButton = QPushButton('Exit')
        self.loginWindowExitButton.clicked.connect(self.exit)

        loginWindowMainLayout = QVBoxLayout(self)
        loginWindowMainLayout.setSpacing(10)
        loginWindowMainLayout.addLayout(loginWindowGridLayout)
        loginWindowMainLayout.addWidget(self.loginWindowForgotPasswordLabel, alignment=Qt.AlignCenter)
        loginWindowMainLayout.addWidget(self.loginWindowLoginButton)
        loginWindowMainLayout.addWidget(self.loginWindowRegisterButton)
        loginWindowMainLayout.addWidget(self.loginWindowExitButton)

        self.setWindowTitle("Log in")

    def login(self):
        loginMsg = QMessageBox()
        loginMsg.setWindowTitle("Warning")
        loginMsg.setIcon(QMessageBox.Warning)

        self.username = self.loginWindowLoginEntry.text()
        self.password = self.loginWindowPasswordEntry.text()

        findUserQuery = QSqlQuery()
        findUserQuery.prepare("SELECT password, userID, currency, darkMode, font, fontSize FROM users WHERE login = :login")
        findUserQuery.bindValue(":login", self.username)
        findUserQuery.exec()

        if findUserQuery.next():
            passwordHash = (findUserQuery.value(0)).encode()
            valid = bcrypt.checkpw(self.password.encode(), passwordHash)
            if valid:
                userID = findUserQuery.value(1)
                currency = findUserQuery.value(2)
                theme = findUserQuery.value(3)
                fontName = findUserQuery.value(4)
                fontSize = findUserQuery.value(5)
                if hasattr(self, "registerWindow"):
                    self.registerWindow.close()
                if hasattr(self, "resetPasswordWindow"):
                    self.resetPasswordWindow.close()
                self.hide()
                self.loginWindowPasswordEntry.setText("")
                MainWindow(self, self.connection, self.app, self.username, userID, currency, theme, fontName, fontSize, self.defaultPalette)
            else:
                loginMsg.setText("Incorrect password!")
                loginMsg.exec()
        else:
            loginMsg.setText("No such user exists!")
            loginMsg.exec()

        findUserQuery.finish()

    def register(self):
        self.registerWindow = RegisterWindow()
        self.registerWindow.show()

    def resetPassword(self):
        self.resetPasswordWindow = ResetPasswordWindow()
        self.resetPasswordWindow.show()

    def databaseConnect(self):
        self.connection = QSqlDatabase.addDatabase('QODBC')
        self.connection.setDatabaseName(
            f'Driver={{SQL SERVER}}; Server={SERVER}; Database={DATABASE}; UID={USERNAME}; PWD={PASSWORD}')

        if not self.connection.open():
            QMessageBox.critical(
                self,
                "Error!",
                "Database Error: %s" % self.connection.lastError().databaseText(),
            )
            sys.exit(1)
        else:
            print("Success")

    def exit(self):       
        self.close()
        
    def closeEvent(self, event):    
        """Metoda zamykająca wszystkie okna po wciśnięciu przycisku zamknij"""
        self.connection.close()
        self.app.closeAllWindows()


class ResetPasswordWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 490, 130)
        registerWindowFont = self.font()
        registerWindowFont.setPointSize(12)
        self.window().setFont(registerWindowFont)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.resetPasswordEmailLabel = QLabel("Please enter the email address associated with the account.")
        self.resetPasswordEmailEntry = QLineEdit()
        self.resetPasswordCancelButton = QPushButton("Cancel")
        self.resetPasswordCancelButton.clicked.connect(self.exit)
        self.resetPasswordNextButton = QPushButton("Next")
        self.codes = None
        self.userID = None
        self.resetPasswordNextButton.clicked.connect(self.sendCode)

        resetPasswordButtonsHLayout1 = QHBoxLayout()
        resetPasswordButtonsHLayout1.addWidget(self.resetPasswordCancelButton)
        resetPasswordButtonsHLayout1.addWidget(self.resetPasswordNextButton)

        self.resetPasswordCodeLabel = QLabel("A code has been sent to the e-mail address provided.\nEnter it in the field below.")
        self.resetPasswordCodeEntry = QLineEdit()
        self.resetPasswordCancel2Button = QPushButton("Cancel")
        self.resetPasswordCancel2Button.clicked.connect(self.exit)
        self.resetPasswordNext2Button = QPushButton("Next")
        self.resetPasswordNext2Button.clicked.connect(lambda: self.checkCode(self.codes))

        resetPasswordButtonsHLayout2 = QHBoxLayout()
        resetPasswordButtonsHLayout2.addWidget(self.resetPasswordCancel2Button)
        resetPasswordButtonsHLayout2.addWidget(self.resetPasswordNext2Button)

        self.resetPasswordNewPassLabel = QLabel("New password:")
        self.resetPasswordNewPassEntry = QLineEdit()
        self.resetPasswordNewPassEntry.setEchoMode(QLineEdit.Password)
        self.resetPasswordConfPassLabel = QLabel("Confirm password:")
        self.resetPasswordConfPassEntry = QLineEdit()
        self.resetPasswordConfPassEntry.setEchoMode(QLineEdit.Password)
        self.resetPasswordCancel3Button = QPushButton("Cancel")
        self.resetPasswordCancel3Button.clicked.connect(self.exit)
        self.resetPasswordResetButton = QPushButton("Reset")
        self.resetPasswordResetButton.clicked.connect(lambda: self.reset(self.userID))

        self.firstLayout = QWidget(self)
        self.secondLayout = QWidget(self)
        self.thirdLayout = QWidget(self)

        resetPasswordLayout1 = QVBoxLayout(self.firstLayout)
        resetPasswordLayout1.setContentsMargins(0, 0, 0, 0)
        resetPasswordLayout1.addWidget(self.resetPasswordEmailLabel, alignment=Qt.AlignCenter)
        resetPasswordLayout1.addWidget(self.resetPasswordEmailEntry)
        resetPasswordLayout1.addLayout(resetPasswordButtonsHLayout1)

        resetPasswordLayout2 = QVBoxLayout(self.secondLayout)
        resetPasswordLayout2.setContentsMargins(0, 0, 0, 0)
        resetPasswordLayout2.addWidget(self.resetPasswordCodeLabel, alignment=Qt.AlignCenter)
        resetPasswordLayout2.addWidget(self.resetPasswordCodeEntry)
        resetPasswordLayout2.addLayout(resetPasswordButtonsHLayout2)

        resetPasswordLayout3 = QGridLayout(self.thirdLayout)
        resetPasswordLayout3.setContentsMargins(0, 0, 0, 0)
        resetPasswordLayout3.addWidget(self.resetPasswordNewPassLabel, 0, 0)
        resetPasswordLayout3.addWidget(self.resetPasswordNewPassEntry, 0, 1)
        resetPasswordLayout3.addWidget(self.resetPasswordConfPassLabel, 1, 0)
        resetPasswordLayout3.addWidget(self.resetPasswordConfPassEntry, 1, 1)
        resetPasswordLayout3.addWidget(self.resetPasswordCancel3Button, 2, 0)
        resetPasswordLayout3.addWidget(self.resetPasswordResetButton, 2, 1)

        self.resetPasswordStackedLayout = QStackedLayout()
        self.resetPasswordStackedLayout.addWidget(self.firstLayout)
        self.resetPasswordStackedLayout.addWidget(self.secondLayout)
        self.resetPasswordStackedLayout.addWidget(self.thirdLayout)
        self.resetPasswordStackedLayout.setCurrentIndex(0)

        resetPasswordMainLayout = QVBoxLayout(self)  
        resetPasswordMainLayout.addLayout(self.resetPasswordStackedLayout)

        self.setWindowTitle("Reset password")

    def validateEmailAddress(self, address):
        expression = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(expression, address):
            return True
        else:
            return False

    def sendCode(self):
        resetMsg = QMessageBox()
        resetMsg.setWindowTitle("Warning")
        resetMsg.setIcon(QMessageBox.Warning)
        email = self.resetPasswordEmailEntry.text()
        
        if self.validateEmailAddress(email):
            pass
        else:
            resetMsg.setText("Invalid email address!")
            resetMsg.exec()
            return

        findUserQuery = QSqlQuery()
        findUserQuery.prepare("SELECT userID FROM users WHERE email = :email")
        findUserQuery.bindValue(":email", email)
        findUserQuery.exec()
        if not findUserQuery.next():
            resetMsg.setText("This email address is not associated with any account!\nPlease use a different email address.")
            resetMsg.exec()
            findUserQuery.finish()
            return
        else:
            userID = findUserQuery.value(0)
            findUserQuery.finish()
            
            msg = EmailMessage()
            msg['Subject'] = "Password reset"
            msg['From'] = "konto.testowe467@gmail.com"
            msg['To'] = email
        
            port = 465
            smtp = "smtp.gmail.com"
            password = MAILPASSWORD
            code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(5))
            msg.set_content(f"Reset code: {code}\nIf you did not request for password reset, please ignore this message.")

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp, port, context=context) as server:
                server.login("konto.testowe467@gmail.com", password)
                server.send_message(msg)

            self.codes = code
            self.userID = userID
            self.resetPasswordStackedLayout.setCurrentIndex(1)

    def checkCode(self, code):
        resetMsg = QMessageBox()

        enteredCode = self.resetPasswordCodeEntry.text()

        if enteredCode == code:
            self.resetPasswordStackedLayout.setCurrentIndex(2)
        else:
            resetMsg.setWindowTitle("Warning")
            resetMsg.setIcon(QMessageBox.Warning)
            resetMsg.setText("Incorrect code!")
            resetMsg.exec()

    def reset(self, userID):
        resetMsg = QMessageBox()

        newPassword = self.resetPasswordNewPassEntry.text()
        confPassword = self.resetPasswordConfPassEntry.text()

        if newPassword != confPassword:
            resetMsg.setWindowTitle("Warning")
            resetMsg.setIcon(QMessageBox.Warning)
            resetMsg.setText("Passwords don't match!")
            resetMsg.exec()
            return
        else:
            passwordHash = bcrypt.hashpw(newPassword.encode(), bcrypt.gensalt())
            passwordHashStr = passwordHash.decode()
            resetQuery = QSqlQuery()
            resetQuery.prepare(f"UPDATE users SET password = :pass WHERE userID = {userID}")
            resetQuery.bindValue(":pass", passwordHashStr)
            if resetQuery.exec():
                resetMsg.setWindowTitle("Info")
                resetMsg.setIcon(QMessageBox.Information)
                resetMsg.setText("Password has been changed.")
                resetMsg.exec()
                self.close()
            else:
                print(resetQuery.lastError().databaseText())

    def exit(self):
        self.close()


class ForgotPasswordLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        QLabel.__init__(self, parent=parent)

    def mousePressEvent(self, event):
        self.clicked.emit()
