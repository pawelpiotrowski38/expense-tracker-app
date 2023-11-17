import bcrypt
import re
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont, QGuiApplication
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLabel, QLineEdit, QGridLayout, QPushButton, \
    QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QGroupBox, QComboBox, QSplitter, QProgressDialog
from forex_python.converter import CurrencyCodes, CurrencyRates
from decimal import Decimal
from colorThemes import lightTheme, darkTheme


class SettingsWindow(QWidget):
    rates = CurrencyRates()
    codes = CurrencyCodes()

    def __init__(self, parent, userID, currency, con, login):
        super().__init__()
        self.parent = parent
        self.userID = userID
        self.currency = currency
        self.con = con
        self.login = login
        self.initUI()

    def initUI(self):

        width = self.frameGeometry().width()

        self.setGeometry(0, 0, 800, 350)
        font = self.font()
        font.setFamily(self.parent.fontName)
        font.setPointSize(self.parent.fontSize)
        self.setFont(font)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        settingsLayout = QHBoxLayout(self)

        leftSettingsPanel = QFrame()
        leftSettingsPanel.setFrameShape(QFrame.StyledPanel)
        leftSettingsPanelVLayout = QVBoxLayout(leftSettingsPanel)

        self.changeUsernameCurrentLabel = QLabel("Current username:")
        self.changeUsernameCurrentEntry = QLineEdit()
        self.changeUsernameCurrentEntry.setMaxLength(20)
        self.changeUsernameNewLabel = QLabel("New username:")
        self.changeUsernameNewEntry = QLineEdit()
        self.changeUsernameNewEntry.setMaxLength(20)
        self.changeUsernameButton = QPushButton("Change username")
        self.changeUsernameButton.clicked.connect(self.changeUsername)

        self.changePasswordCurrentLabel = QLabel("Current password:")
        self.changePasswordNewLabel = QLabel("New password:")
        self.changePasswordConfirmLabel = QLabel("Confirm password:")
        self.changePasswordCurrentEntry = QLineEdit()
        self.changePasswordCurrentEntry.setMaxLength(20)
        self.changePasswordCurrentEntry.setEchoMode(QLineEdit.Password)
        self.changePasswordNewEntry = QLineEdit()
        self.changePasswordNewEntry.setMaxLength(20)
        self.changePasswordNewEntry.setEchoMode(QLineEdit.Password)
        self.changePasswordConfirmEntry = QLineEdit()
        self.changePasswordConfirmEntry.setMaxLength(20)
        self.changePasswordConfirmEntry.setEchoMode(QLineEdit.Password)
        self.changePasswordButton = QPushButton("Change password")
        self.changePasswordButton.clicked.connect(self.changePassword)

        self.deleteAccountLabel = QLabel("Delete account")
        self.deleteAccountPasswordLabel = QLabel("Current password:")
        self.deleteAccountPasswordEntry = QLineEdit()
        self.deleteAccountPasswordEntry.setMaxLength(20)
        self.deleteAccountPasswordEntry.setEchoMode(QLineEdit.Password)
        self.deleteAccountButton = QPushButton("Delete account")
        self.deleteAccountButton.clicked.connect(self.deleteUserAccount)

        changeUsernameGridLayout = QGridLayout()
        changeUsernameGridLayout.addWidget(self.changeUsernameCurrentLabel, 0, 0)
        changeUsernameGridLayout.addWidget(self.changeUsernameCurrentEntry, 0, 1)
        changeUsernameGridLayout.addWidget(self.changeUsernameNewLabel, 1, 0)
        changeUsernameGridLayout.addWidget(self.changeUsernameNewEntry, 1, 1)
        changeUsernameGridLayout.addWidget(self.changeUsernameButton, 2, 1)

        changePasswordGridLayout = QGridLayout()
        changePasswordGridLayout.addWidget(self.changePasswordCurrentLabel, 0, 0)
        changePasswordGridLayout.addWidget(self.changePasswordCurrentEntry, 0, 1)
        changePasswordGridLayout.addWidget(self.changePasswordNewLabel, 1, 0)
        changePasswordGridLayout.addWidget(self.changePasswordNewEntry, 1, 1)
        changePasswordGridLayout.addWidget(self.changePasswordConfirmLabel, 2, 0)
        changePasswordGridLayout.addWidget(self.changePasswordConfirmEntry, 2, 1)
        changePasswordGridLayout.addWidget(self.changePasswordButton, 3, 1)

        deleteAccountGridLayout = QGridLayout()
        deleteAccountGridLayout.addWidget(self.deleteAccountPasswordLabel, 0, 0)
        deleteAccountGridLayout.addWidget(self.deleteAccountPasswordEntry, 0, 1)
        deleteAccountGridLayout.addWidget(self.deleteAccountButton, 1, 1)

        changeUsernameBox = QGroupBox()
        changeUsernameBox.setTitle("Change username")
        changeUsernameBox.setLayout(changeUsernameGridLayout)
        changePasswordBox = QGroupBox()
        changePasswordBox.setTitle("Change password")
        changePasswordBox.setLayout(changePasswordGridLayout)
        deleteAccountBox = QGroupBox()
        deleteAccountBox.setTitle("Delete account")
        deleteAccountBox.setLayout(deleteAccountGridLayout)

        leftSettingsPanelVLayout.addWidget(changeUsernameBox)
        leftSettingsPanelVLayout.addWidget(changePasswordBox)
        leftSettingsPanelVLayout.addWidget(deleteAccountBox)

        rightSettingsPanel = QFrame()
        rightSettingsPanel.setFrameShape(QFrame.StyledPanel)
        rightSettingsPanelVLayout = QVBoxLayout(rightSettingsPanel)

        self.currencyLabel = QLabel("Default currency:")
        self.currencyComboBox = QComboBox()
        codesList = ['EUR', 'IDR', 'BGN', 'ILS', 'GBP', 'DKK', 'CAD', 'JPY', 'HUF', 'RON', 'MYR', 'SEK', 'SGD', 'HKD',
                     'AUD', 'CHF', 'KRW', 'CNY', 'TRY', 'HRK', 'NZD', 'THB', 'USD', 'NOK', 'RUB', 'INR', 'MXN', 'CZK',
                     'BRL', 'PLN', 'PHP', 'ZAR']
        for i in codesList:
            name = self.codes.get_currency_name(i)
            item = i + ' - ' + name
            self.currencyComboBox.addItem(item)
        currencyName = self.codes.get_currency_name(self.parent.currencyCode)
        self.currencyComboBox.setCurrentText(self.parent.currencyCode + ' - ' + currencyName)
        self.themeLabel = QLabel("Theme:")
        self.themeEntry = QComboBox()
        self.themeEntry.addItems(["Light theme", "Dark theme"])
        if self.parent.theme:
            self.themeEntry.setCurrentIndex(1)
        else:
            self.themeEntry.setCurrentIndex(0)
        self.fontLabel = QLabel("Font: ")
        self.fontEntry = QComboBox()
        fontObject = QFontDatabase()
        self.fontEntry.addItems(fontObject.families())
        print(self.parent.fontName)
        self.fontEntry.setCurrentText(self.parent.fontName)
        self.fontSizeLabel = QLabel("Font size:")
        self.fontSizeEntry = QComboBox()
        self.fontSizeEntry.addItems(["Small", "Medium", "Large"])
        if self.parent.fontSize == 11:
            self.fontSizeEntry.setCurrentIndex(0)
        if self.parent.fontSize == 12:
            self.fontSizeEntry.setCurrentIndex(1)
        if self.parent.fontSize == 13:
            self.fontSizeEntry.setCurrentIndex(2)
        self.currencySaveButton = QPushButton("Save changes")
        self.currencySaveButton.clicked.connect(self.changeSettings)

        rightSettingsGridLayout = QGridLayout()
        rightSettingsGridLayout.addWidget(self.currencyLabel, 0, 0)
        rightSettingsGridLayout.addWidget(self.currencyComboBox, 0, 1)
        rightSettingsGridLayout.addWidget(self.themeLabel, 1, 0)
        rightSettingsGridLayout.addWidget(self.themeEntry, 1, 1)
        rightSettingsGridLayout.addWidget(self.fontLabel, 2, 0)
        rightSettingsGridLayout.addWidget(self.fontEntry, 2, 1)
        rightSettingsGridLayout.addWidget(self.fontSizeLabel, 3, 0)
        rightSettingsGridLayout.addWidget(self.fontSizeEntry, 3, 1)

        test = QGroupBox()
        test.setTitle("Change settings")
        test.setLayout(rightSettingsGridLayout)

        # rightSettingsPanelVLayout.addLayout(leftSettingsHBoxLayout)
        rightSettingsPanelVLayout.addWidget(test)
        rightSettingsPanelVLayout.addWidget(self.currencySaveButton, alignment=Qt.AlignRight)

        splitterSettings = QSplitter(Qt.Horizontal)
        splitterSettings.addWidget(leftSettingsPanel)
        splitterSettings.addWidget(rightSettingsPanel)
        splitterSettings.setSizes([int(width * 0.5), int(width * 0.5)])

        settingsLayout.addWidget(splitterSettings)

    def changeUsername(self):
        changeMsg = QMessageBox()
        changeMsg.setWindowTitle("Warning")
        changeMsg.setIcon(QMessageBox.Warning)
        characters = " !\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"

        changeQuery = QSqlQuery()
        changeQuery.exec(f"SELECT login FROM users WHERE userID = {self.userID}")
        if changeQuery.next():
            username = changeQuery.value(0)
        else:
            changeQuery.finish()
            return
        if username != self.changeUsernameCurrentEntry.text():
            changeMsg.setText("Invalid username!")
            changeMsg.exec()
            return
        newUsername = self.changeUsernameNewEntry.text()
        changeQuery.prepare("SELECT login FROM users WHERE login = :login")
        changeQuery.bindValue(":login", newUsername)
        changeQuery.exec()
        if changeQuery.next():
            changeMsg.setText("Such user already exists!")
            changeMsg.exec()
            return
        elif len(newUsername) < 5:
            changeMsg.setText("Username has to be at least 5 characters long.")
            changeMsg.exec()
            return
        elif any(char in characters for char in newUsername):
            changeMsg.setText("Username can contain only letters, digits and underscores!")
            changeMsg.exec()
            return

        changeQuery.prepare(f"UPDATE users SET login = :login WHERE userID = {self.userID}")
        changeQuery.bindValue(":login", newUsername)
        if changeQuery.exec():
            self.parent.topMenuButton.setText(' ' + newUsername)
            changeMsg.setWindowTitle("Info")
            changeMsg.setIcon(QMessageBox.Information)
            changeMsg.setText("Username has been changed.")
            changeMsg.exec()
        else:
            print(changeQuery.lastError().databaseText())
        changeQuery.finish()

    def changePassword(self):
        changeMsg = QMessageBox()
        changeMsg.setWindowTitle("Warning")
        changeMsg.setIcon(QMessageBox.Warning)
        characters = " !\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"

        currentPassword = self.changePasswordCurrentEntry.text()
        newPassword = self.changePasswordNewEntry.text()
        confirmPassword = self.changePasswordConfirmEntry.text()

        changeQuery = QSqlQuery()
        changeQuery.exec(f"SELECT password FROM users WHERE userID = {self.userID}")
        if changeQuery.next():
            passwordHash = (changeQuery.value(0)).encode()
            valid = bcrypt.checkpw(currentPassword.encode(), passwordHash)
            if not valid:
                changeMsg.setText("Incorrect password!")
                changeMsg.exec()
            elif not newPassword == confirmPassword:
                changeMsg.setText("Passwords don't match!")
                changeMsg.exec()
            elif len(newPassword) < 5:
                changeMsg.setText("Password has to be at least 5 characters long.")
                changeMsg.exec()
                return
            elif re.search('[0-9]', newPassword) is None or re.search('[A-Z]', newPassword) is None:
                changeMsg.setText("Password has to contain at least one digit and one capital letter!")
                changeMsg.exec()
                return
            else:
                passwordHash = bcrypt.hashpw(newPassword.encode(), bcrypt.gensalt())
                passwordHashStr = passwordHash.decode()
                changeQuery.prepare(f"UPDATE users SET password = :pass WHERE userID = {self.userID}")
                changeQuery.bindValue(":pass", passwordHashStr)
                if changeQuery.exec():
                    changeMsg.setWindowTitle("Info")
                    changeMsg.setIcon(QMessageBox.Information)
                    changeMsg.setText("Password has been changed.")
                    changeMsg.exec()
                else:
                    print(changeQuery.lastError().databaseText())
        changeQuery.finish()

    def changeSettings(self):
        newCurrency = self.currencyComboBox.currentText()[:3]
        newTheme = self.themeEntry.currentText()
        if newTheme == "Light theme":
            newTheme = 0
        elif newTheme == "Dark theme":
            newTheme = 1
        newFontName = self.fontEntry.currentText()
        newFontSize = self.fontSizeEntry.currentText()
        if newFontSize == "Small":
            newFontSize = 11
        elif newFontSize == "Medium":
            newFontSize = 12
        elif newFontSize == "Large":
            newFontSize = 13

        if not newCurrency == self.parent.currencyCode:
            updateCurrencyQuery = QSqlQuery()
            updateCurrencyQuery.exec(f"UPDATE users SET currency = '{newCurrency}' WHERE userID = {self.userID}")
            updateCurrencyQuery.finish()

            exList = {}
            inList = {}

            transactionQuery = QSqlQuery()
            transactionQuery.exec(
                f"SELECT transactionID, originValue, currency FROM expenses WHERE userID = {self.userID}")
            while transactionQuery.next():
                exList[transactionQuery.value(0)] = [Decimal(transactionQuery.value(1)), transactionQuery.value(2)]
            transactionQuery.exec(f"SELECT transactionID, originValue, currency FROM income WHERE userID = {self.userID}")
            while transactionQuery.next():
                inList[transactionQuery.value(0)] = [Decimal(transactionQuery.value(1)), transactionQuery.value(2)]

            currencyRates = {}
            transactionQuery.exec(f"SELECT currency FROM accounts WHERE userID = {self.userID}")
            while transactionQuery.next():
                oldCurrency = transactionQuery.value(0)
                rate = Decimal(self.rates.get_rate(oldCurrency, newCurrency))
                currencyRates[oldCurrency] = rate

            for key, value in exList.items():
                currency = value[1]
                rate = currencyRates[currency]
                convertedValue = value[0] * rate
                transactionQuery.exec(f"UPDATE expenses SET value = {convertedValue} WHERE transactionID = {key}")
            for key, value in inList.items():
                currency = value[1]
                rate = currencyRates[currency]
                convertedValue = value[0] * rate
                transactionQuery.exec(f"UPDATE income SET value = {convertedValue} WHERE transactionID = {key}")
            transactionQuery.finish()

            self.parent.currencyCode = newCurrency
            self.parent.currency = self.codes.get_symbol(newCurrency)
            self.parent.topLeftBudgetsSymbolLabel.setText(self.parent.currency)
            currencyName = newCurrency + ' - ' + self.codes.get_currency_name(newCurrency)
            self.parent.topLeftAccountsCurrencyEntry.setCurrentText(currencyName)
            self.parent.refresh()

        if not newTheme == self.parent.theme:
            if newTheme == 0:
                QGuiApplication.setPalette(lightTheme())
            else:
                QGuiApplication.setPalette(darkTheme())
            self.parent.theme = newTheme
            self.parent.refreshCharts()
            updateThemeQuery = QSqlQuery()
            updateThemeQuery.exec(f"UPDATE users SET darkMode = {newTheme} WHERE userID = {self.userID}")
            updateThemeQuery.finish()

        if not newFontName == self.parent.fontName or not newFontSize == self.parent.fontSize:
            font = QFont()
            font.setFamily(newFontName)
            font.setPointSize(newFontSize)
            font.setWeight(55)

            updateFontQuery = QSqlQuery()
            updateFontQuery.exec(f"UPDATE users SET font = '{newFontName}', fontSize = {newFontSize} WHERE userID = {self.userID}")
            updateFontQuery.finish()

            self.setFont(font)
            self.parent.setFont(font)
            self.parent.topMenu.setFont(font)
            self.parent.fontName = newFontName
            self.parent.fontSize = newFontSize
            self.parent.fontt = font
            #self.parent.refresh()

    def deleteUserAccount(self):
        deleteMsg = QMessageBox()
        deleteQuery = QSqlQuery()
        currentPassword = self.deleteAccountPasswordEntry.text()

        deleteQuery.exec(f"SELECT password FROM users WHERE userID = {self.userID}")
        if deleteQuery.next():
            passwordHash = (deleteQuery.value(0)).encode()
            valid = bcrypt.checkpw(currentPassword.encode(), passwordHash)
            if not valid:
                deleteMsg.setWindowTitle("Warning")
                deleteMsg.setIcon(QMessageBox.Warning)
                deleteMsg.setText("Incorrect password!")
                deleteMsg.exec()
            else:
                deleteMsg.setWindowTitle("Confirm")
                deleteMsg.setIcon(QMessageBox.Question)
                deleteMsg.setText("You will be logged out and all your data will be deleted.\nDo you want to continue?")
                yesButton = QPushButton("Yes")
                noButton = QPushButton("No")
                deleteMsg.addButton(yesButton, QMessageBox.YesRole)
                deleteMsg.addButton(noButton, QMessageBox.NoRole)
                deleteMsg.exec()
                if deleteMsg.clickedButton() == yesButton:
                    if not deleteQuery.exec(f"DELETE FROM expenses WHERE userID = {self.userID}"):
                        print(deleteQuery.lastError().databaseText())
                    if not deleteQuery.exec(f"DELETE FROM income WHERE userID = {self.userID}"):
                        print(deleteQuery.lastError().databaseText())
                    if not deleteQuery.exec(f"SELECT jobName FROM jobs WHERE userID = {self.userID}"):
                        print(deleteQuery.lastError().databaseText())
                    else:
                        deleteJobQuery = QSqlQuery()
                        while deleteQuery.next():
                            jobName = deleteQuery.value(0)
                            statusJobName = jobName + "_status"
                            deleteJobQuery.exec(f"USE msdb ; "
                                                f"EXEC dbo.sp_delete_job @job_name = N'{jobName}', @delete_unused_schedule = 1 ; "
                                                f"EXEC dbo.sp_delete_job @job_name = N'{statusJobName}', @delete_unused_schedule = 1 ; "
                                                f"USE Baza ;")
                        deleteJobQuery.finish()
                    if not deleteQuery.exec(f"DELETE FROM jobs WHERE userID = {self.userID}"):
                        print(deleteQuery.lastError().databaseText())
                    if not deleteQuery.exec(f"DELETE FROM transfers WHERE userID = {self.userID}"):
                        print(deleteQuery.lastError().databaseText())
                    if not deleteQuery.exec(f"DELETE FROM accounts WHERE userID = {self.userID}"):
                        print(deleteQuery.lastError().databaseText())
                    if not deleteQuery.exec(f"DELETE FROM budgetEntries WHERE userID = {self.userID}"):
                        print(deleteQuery.lastError().databaseText())
                    if not deleteQuery.exec(f"SELECT type, jobName FROM budgets WHERE userID = {self.userID}"):
                        print(deleteQuery.lastError().databaseText())
                    else:
                        deleteJobQuery = QSqlQuery()
                        while deleteQuery.next():
                            budgetType = deleteQuery.value(0)
                            if budgetType == "Periodic":
                                budgetJobName = deleteQuery.value(1)
                                if not deleteJobQuery.exec(f"USE msdb ; "
                                                           f"EXEC dbo.sp_delete_job @job_name = N'{budgetJobName}', @delete_unused_schedule = 1 ; "
                                                           f"USE Baza ;"):
                                    print(deleteJobQuery.lastError().databaseText())
                        deleteJobQuery.finish()

                    if not deleteQuery.exec(f"DELETE FROM budgets WHERE userID = {self.userID}"):
                        print(deleteQuery.lastError().databaseText())
                    if not deleteQuery.exec(f"DELETE FROM categories WHERE userID = {self.userID}"):
                        print(deleteQuery.lastError().databaseText())
                    if not deleteQuery.exec(f"DELETE FROM users WHERE userID = {self.userID}"):
                        print(deleteQuery.lastError().databaseText())
                    deleteQuery.finish()

                    self.close()
                    self.parent.logout()

    def exit(self):
        self.close()
