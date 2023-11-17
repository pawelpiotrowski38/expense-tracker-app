from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from forex_python.converter import CurrencyRates
from PyQt5.QtCore import QTime
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QPushButton, QMessageBox


class JobFunctions:
    def addJob(self):
        # -------------------------------------------------------------------------------
        # ------------------------------Transaction Info---------------------------------
        # -------------------------------------------------------------------------------
        addJobMsg = QMessageBox()
        addJobMsg.setWindowTitle("Warning")
        addJobMsg.setIcon(QMessageBox.Warning)
        characters = " !\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"
        rates = CurrencyRates()

        name = self.recurringNameEdit.text()
        jobName = "sched_" + self.login + "_" + name
        if len(name) < 3:
            addJobMsg.setText("Name must be at least 3 characters long.")
            addJobMsg.exec()
            return
        elif any(char in characters for char in name):
            addJobMsg.setText("Name can only contain letters, digits and underscores!")
            addJobMsg.exec()
            return

        findJob = QSqlQuery()
        findJob.prepare("SELECT name FROM jobs WHERE name = :name AND userID = :userID")
        findJob.bindValue(":name", name)
        findJob.bindValue(":userID", self.userID)
        if not findJob.exec():
            addJobMsg.setText("Database error!")
            addJobMsg.exec()
        if findJob.next():
            addJobMsg.setText("A job with that name already exists!")
            addJobMsg.exec()
            findJob.finish()
            return
        findJob.finish()

        try:
            value = Decimal(self.recurringValueEntry.text()).quantize(self.fractional, ROUND_HALF_UP)
            if value <= 0:
                raise InvalidOperation
        except InvalidOperation:
            addJobMsg.setText("Amount must be a number!")
            addJobMsg.exec()
            return

        if self.recurringExpenseRadioButton.isChecked():
            job_transaction_type = 'expenses'
            transaction_type = 'Expense'
            difference = (-1) * value
        elif self.recurringIncomeRadioButton.isChecked():
            job_transaction_type = 'income'
            transaction_type = 'Income'
            difference = value
        else:
            addJobMsg.setText("Type of transaction is not selected!")
            addJobMsg.exec()
            return

        amount = str(value) + ' ' + self.recurringSymbolLabel.text()
        cat = self.recurringCategoryEntry.currentText()
        if not cat:
            addJobMsg.setText("Category is not selected!")
            addJobMsg.exec()
            return
        acc = self.recurringAccountEntry.currentText()
        if not acc:
            addJobMsg.setText("Account is not selected!")
            addJobMsg.exec()
            return
        notes = self.recurringNotesEntry.toPlainText()
        if len(notes) > 100:
            addJobMsg.setText("Notes length cannot be greater than 100 characters.")
            addJobMsg.exec()
            return

        addJobQuery = QSqlQuery()
        if not addJobQuery.exec(
                f"SELECT categoryID FROM categories WHERE name = '{cat}' AND categoryType = '{job_transaction_type}' AND userID = {self.userID}"):
            print(addJobQuery.lastError().databaseText())
            return -1
        if addJobQuery.next():
            categoryID = addJobQuery.value(0)
        else:
            return -1
        if not addJobQuery.exec(f"SELECT accountID FROM accounts WHERE name = '{acc}' AND userID = {self.userID}"):
            print(addJobQuery.lastError().databaseText())
            return -1
        if addJobQuery.next():
            accountID = addJobQuery.value(0)
        else:
            return -1

        findCurrencyQuery = QSqlQuery()
        findCurrencyQuery.prepare(f"SELECT currency FROM accounts WHERE name = :acc AND userID = :userID;")
        findCurrencyQuery.bindValue(":acc", acc)
        findCurrencyQuery.bindValue(":userID", self.userID)
        if not findCurrencyQuery.exec():
            addJobMsg.setText("Database error!")
            addJobMsg.exec()
        if findCurrencyQuery.next():
            accCurrency = findCurrencyQuery.value(0)
        findCurrencyQuery.finish()
        if accCurrency != self.currencyCode:
            convertedValue = (rates.convert(accCurrency, self.currencyCode, value)).quantize(self.fractional,
                                                                                             ROUND_HALF_UP)
        else:
            convertedValue = value

        # --------------------------------------------------------------------------------
        # ---------------------------------Schedule Info----------------------------------
        # --------------------------------------------------------------------------------
        job_schedule_name = jobName + '_schedule'
        job_step1_name = jobName + '_step1'
        job_step2_name = jobName + '_step2'
        job_step3_name = jobName + '_step3'

        status_job_name = jobName + '_status'
        status_job_schedule_name = jobName + '_status_schedule'
        status_job_step_name = jobName + '_status_step'

        if self.recurringRecurEnabledCheckBox.isChecked():
            status = 'Enabled'
            job_status = 1
        else:
            status = 'Disabled'
            job_status = 0

        daysDict = {'Mon': 2, 'Tue': 4, 'Wed': 8, 'Thu': 16, 'Fri': 32, 'Sat': 64, 'Sun': 1}

        if self.recurringOnceRadioButton.isChecked():
            schedule_type = 'One time'
            frequency = 'n/a'
            recurrence = 'n/a'
            month_day = 'n/a'
            week_day = 'n/a'
            end_date = 'n/a'
            freq_type = 1
            freq_interval = 0
            freq_recurrence_factor = 0

            tempVar1 = self.recurringOnceDateEntry.date()
            tempDate = tempVar1.toPyDate()
            tempDateStatus = tempDate + timedelta(days=1)

            tempVar2 = self.recurringOnceTimeEntry.time()
            tempTime = tempVar2.toPyTime()
            tempTimeStatus = (datetime.combine(date(1, 1, 1), tempTime) + timedelta(seconds=1)).time()

            startDate = str(tempDate).translate({ord(i): None for i in '-'})
            startDateStatus = str(tempDateStatus).translate({ord(i): None for i in '-'})

            startTime = (str(tempTime).translate({ord(i): None for i in ':'})).split('.')[0]

            start_date = str(tempDate)
            start_time = (str(tempTime)).split('.')[0]

            startTimeStatus = (str(tempTimeStatus).translate({ord(i): None for i in ':'})).split('.')[0]
            active_start_time_status = startTimeStatus

            if int(startTimeStatus) == 0:
                active_start_date_status = startDateStatus
            else:
                active_start_date_status = startDate

            active_start_date = startDate
            active_start_time = startTime
            active_end_date = 99991231
            active_end_date_status = 99991231
            active_end_time = 235959

        if self.recurringRecurRadioButton.isChecked():
            schedule_type = 'Recurring'
            if self.recurringFreqComboBox.currentText() == 'Daily':
                frequency = 'Daily'
                recurrence = 'Every ' + str(self.recurringFreqDaySpinBox.value()) + ' day(s)'
                month_day = 'n/a'
                week_day = 'n/a'
                freq_type = 4
                freq_interval = self.recurringFreqDaySpinBox.value()
                freq_recurrence_factor = 0
            if self.recurringFreqComboBox.currentText() == 'Weekly':
                frequency = 'Weekly'
                recurrence = 'Every ' + str(self.recurringFreqWeekSpinBox.value()) + ' week(s)'
                month_day = 'n/a'
                week_day_list = []
                freq_type = 8
                days_sum = 0
                for checkBox in self.recurringDaysCheckBoxList:
                    if checkBox.isChecked():
                        days_sum += daysDict[checkBox.text()]
                        week_day_list.append(checkBox.text())
                if days_sum == 0:
                    addJobMsg.setText("At least one day has to be selected!")
                    addJobMsg.exec()
                    return
                week_day = ','.join(week_day_list)
                freq_interval = days_sum
                freq_recurrence_factor = self.recurringFreqWeekSpinBox.value()
            if self.recurringFreqComboBox.currentText() == 'Monthly':
                frequency = 'Monthly'
                recurrence = 'Every ' + str(self.recurringFreqMonthSpinBox.value()) + ' month(s)'
                month_day = self.recurringOnDaySpinBox.value()
                week_day = 'n/a'
                freq_type = 16
                freq_interval = self.recurringOnDaySpinBox.value()
                freq_recurrence_factor = self.recurringFreqMonthSpinBox.value()

            tempVar1 = self.recurringFreqOccursAtTimeEntry.time()
            tempTime = tempVar1.toPyTime()
            tempTimeStatus = (datetime.combine(date(1, 1, 1), tempTime) + timedelta(seconds=1)).time()

            startTime = (str(tempTime).translate({ord(i): None for i in ':'})).split('.')[0]
            startTimeStatus = (str(tempTimeStatus).translate({ord(i): None for i in ':'})).split('.')[0]
            start_time = (str(tempTime)).split('.')[0]

            active_start_time = startTime
            active_end_time = 235959
            active_start_time_status = startTimeStatus

            tempVar2 = self.recurringDurationStartDateEntry.date()
            tempSDate = tempVar2.toPyDate()
            tempSDateStatus = tempSDate + timedelta(days=1)
            startDate = str(tempSDate).translate({ord(i): None for i in '-'})
            startDateStatus = str(tempSDateStatus).translate({ord(i): None for i in '-'})
            start_date = str(tempSDate)
            active_start_date = startDate

            if int(startTimeStatus) == 0:
                active_start_date_status = startDateStatus
            else:
                active_start_date_status = startDate

            if self.recurringDurationEndRadioButton.isChecked():
                tempVar3 = self.recurringDurationEndDateEntry.date()
                tempEDate = tempVar3.toPyDate()
                if tempEDate < tempSDate:
                    addJobMsg.setText("Date!")
                    addJobMsg.exec()
                    return
                tempEDateStatus = tempEDate + timedelta(days=1)

                endDate = str(tempEDate).translate({ord(i): None for i in '-'})
                endDateStatus = str(tempEDateStatus).translate({ord(i): None for i in '-'})
                end_date = str(tempEDate)
                active_end_date = endDate

                if int(startTimeStatus) == 0:
                    active_end_date_status = endDateStatus
                else:
                    active_end_date_status = endDate
            else:
                end_date = 'no end date'
                active_end_date = 99991231
                active_end_date_status = 99991231
        # --------------------------------------------------------------------------------

        addJobQuery.prepare(
            f"INSERT INTO jobs (name,status,type_t,value,categoryID,accountID,notes,type_s,frequency,recurrence,month_day,week_day,time,start_date,end_date,originValue,jobName,userID) "
            f"VALUES (:name,'{status}','{transaction_type}',:amount,:cat,:acc,:notes,'{schedule_type}','{frequency}','{recurrence}','{month_day}','{week_day}','{start_time}','{start_date}','{end_date}',{value},:jobName,{self.userID})")
        addJobQuery.bindValue(":name", name)
        addJobQuery.bindValue(":amount", amount)
        addJobQuery.bindValue(":cat", categoryID)
        addJobQuery.bindValue(":acc", accountID)
        addJobQuery.bindValue(":notes", notes)
        addJobQuery.bindValue(":jobName", jobName)
        if not addJobQuery.exec():
            print(addJobQuery.lastError().databaseText())
        addJobQuery.finish()

        jobName = jobName.replace("'", "''")
        job_step1_name = job_step1_name.replace("'", "''")
        job_step2_name = job_step2_name.replace("'", "''")
        job_schedule_name = job_schedule_name.replace("'", "''")
        status_job_name = status_job_name.replace("'", "''")
        status_job_step_name = status_job_step_name.replace("'", "''")
        status_job_schedule_name = status_job_schedule_name.replace("'", "''")

        jobQuery = QSqlQuery()
        query = f"""USE msdb ;
    EXEC dbo.sp_add_job  
        @job_name = N'{jobName}' ;
    EXEC sp_add_jobstep  
        @job_name = N'{jobName}',  
        @step_name = N'{job_step1_name}',  
        @subsystem = N'TSQL',  
        @command = N'INSERT INTO Baza.dbo.{job_transaction_type} (amount,categoryID,accountID,transactionDate,notes,value,originValue,currency,userID) VALUES ("{amount}", {categoryID}, {accountID}, CONVERT(date,getdate()), "{notes}", {convertedValue}, {value}, "{accCurrency}", "{self.userID}");',
        @on_success_action = 3,
        @retry_attempts = 0,  
        @retry_interval = 0 ;
    EXEC sp_add_jobstep  
        @job_name = N'{jobName}',  
        @step_name = N'{job_step2_name}',  
        @subsystem = N'TSQL',  
        @command = N'UPDATE Baza.dbo.accounts SET currAmount = (SELECT currAmount FROM Baza.dbo.accounts WHERE accountID = "{accountID}") + {difference} WHERE accountID = "{accountID}" AND userID = "{self.userID}";',
        @retry_attempts = 0,  
        @retry_interval = 0 ;
    EXEC dbo.sp_add_schedule  
        @schedule_name = N'{job_schedule_name}',
        @enabled = {job_status},
        @freq_type = {freq_type},
        @freq_interval = {freq_interval}, 
        @freq_relative_interval = 0, 
        @freq_recurrence_factor = {freq_recurrence_factor},
        @active_start_date = {active_start_date},
        @active_end_date = {active_end_date},
        @active_start_time = {active_start_time},
        @active_end_time = {active_end_time} ;  
    USE msdb ;
    EXEC sp_attach_schedule  
       @job_name = N'{jobName}',  
       @schedule_name = N'{job_schedule_name}';
    EXEC dbo.sp_add_jobserver  
        @job_name = N'{jobName}';

    USE msdb ;
    EXEC dbo.sp_add_job  
        @job_name = N'{status_job_name}' ;
    EXEC sp_add_jobstep  
        @job_name = N'{status_job_name}',  
        @step_name = N'{status_job_step_name}',  
        @subsystem = N'TSQL',  
        @command = N'UPDATE Baza.dbo.jobs SET status = (SELECT enabled FROM msdb.dbo.sysschedules WHERE name = "{job_schedule_name}") WHERE name = "{name}";',
        @retry_attempts = 0,  
        @retry_interval = 0 ;
    EXEC dbo.sp_add_schedule  
        @schedule_name = N'{status_job_schedule_name}',
        @enabled = {job_status},
        @freq_type = {freq_type},
        @freq_interval = {freq_interval}, 
        @freq_relative_interval = 0, 
        @freq_recurrence_factor = {freq_recurrence_factor},
        @active_start_date = {active_start_date_status},
        @active_end_date = {active_end_date_status},
        @active_start_time = {active_start_time_status},
        @active_end_time = {active_end_time} ;
    USE msdb ;
    EXEC sp_attach_schedule  
       @job_name = N'{status_job_name}',  
       @schedule_name = N'{status_job_schedule_name}';
    EXEC dbo.sp_add_jobserver  
        @job_name = N'{status_job_name}';
    USE Baza ;"""
        print(query)
        if not jobQuery.exec(query):
            print(jobQuery.lastError().databaseText())
        jobQuery.finish()

        self.cancelEditScheduledTransaction()
        self.fillJobsTable()

    def deleteScheduledTransaction(self):
        deleteSchMsg = QMessageBox()
        if self.scheduledTrTableView.currentIndex().isValid():
            indexes = self.scheduledTrTableView.selectionModel().selectedRows()
            if not indexes:
                deleteSchMsg.setWindowTitle("Info")
                deleteSchMsg.setText("Transaction is not selected!")
                deleteSchMsg.exec()
                return None
            else:
                deleteSchMsg.setWindowTitle("Confirm")
                deleteSchMsg.setIcon(QMessageBox.Question)
                deleteSchMsg.setText("The transaction will be deleted. \nDo you want to continue?")
                yesButton = QPushButton("Yes")
                noButton = QPushButton("No")
                deleteSchMsg.addButton(yesButton, QMessageBox.YesRole)
                deleteSchMsg.addButton(noButton, QMessageBox.NoRole)
                deleteSchMsg.exec()
                if deleteSchMsg.clickedButton() == yesButton:
                    tableModelJobs = self.scheduledTrTableView.model()
                    rows = []
                    for index in sorted(indexes):
                        rows.append(index.row())
                    rows.reverse()
                    for row in rows:
                        name = tableModelJobs.data(tableModelJobs.index(row, 0))
                        name = "sched_" + self.login + "_" + name
                        name = name.replace("'", "''")
                        addname = name + '_status'
                        tableModelJobs.removeRow(row)
                        deleteJobQuery = QSqlQuery(f"USE msdb ; "
                                                   f"EXEC dbo.sp_delete_job @job_name = N'{name}', @delete_unused_schedule = 1 ; "
                                                   f"EXEC dbo.sp_delete_job @job_name = N'{addname}', @delete_unused_schedule = 1 ; "
                                                   f"USE Baza ;")
                        deleteJobQuery.finish()
                        tableModelJobs.select()
                        self.fillJobsTable()
        else:
            deleteSchMsg.setWindowTitle("Info")
            deleteSchMsg.setText("Transaction is not selected!")
            deleteSchMsg.exec()

    def editScheduledTransaction(self):
        editSchMsg = QMessageBox()
        if self.scheduledTrTableView.currentIndex().isValid():
            indexes = self.scheduledTrTableView.selectionModel().selectedRows()
            if not indexes:
                editSchMsg.setWindowTitle("Info")
                editSchMsg.setText("Transaction is not selected!")
                editSchMsg.exec()
                return None
            tableModelJobs = self.scheduledTrTableView.model()
            self.recurringEditStackedLayout.setCurrentIndex(1)
            for index in sorted(indexes):
                row = index.row()
                self.old_name = tableModelJobs.data(tableModelJobs.index(row, 0))
                status = tableModelJobs.data(tableModelJobs.index(row, 1))
                type_t = tableModelJobs.data(tableModelJobs.index(row, 2))
                value = Decimal(tableModelJobs.data(tableModelJobs.index(row, 15))).quantize(self.fractional,
                                                                                             ROUND_HALF_UP)
                categoryID = tableModelJobs.data(tableModelJobs.index(row, 4))
                account = tableModelJobs.data(tableModelJobs.index(row, 5))
                notes = tableModelJobs.data(tableModelJobs.index(row, 6))
                sched = tableModelJobs.data(tableModelJobs.index(row, 7))
                freq = tableModelJobs.data(tableModelJobs.index(row, 8))
                recur = tableModelJobs.data(tableModelJobs.index(row, 9))
                month_day = tableModelJobs.data(tableModelJobs.index(row, 10))
                week_day = tableModelJobs.data(tableModelJobs.index(row, 11))
                time_t = tableModelJobs.data(tableModelJobs.index(row, 12))
                startDate = tableModelJobs.data(tableModelJobs.index(row, 13))
                endDate = tableModelJobs.data(tableModelJobs.index(row, 14))

            self.old_job_name = "sched_" + self.login + "_" + self.old_name
            self.old_schedule_name = self.old_job_name + '_schedule'
            self.old_status_job_name = self.old_job_name + '_status'
            self.old_status_job_schedule_name = self.old_job_name + '_status_schedule'

            self.recurringNameEdit.setText(self.old_name)
            if status == 'Enabled' or status == 1:
                self.recurringRecurEnabledCheckBox.setChecked(True)
            else:
                self.recurringRecurEnabledCheckBox.setChecked(False)
            if type_t == 'Expense':
                self.recurringExpenseRadioButton.setChecked(True)
            else:
                self.recurringIncomeRadioButton.setChecked(True)
            self.recurringValueEntry.setText(str(value))

            editScheduledTransaction = QSqlQuery()
            if not editScheduledTransaction.exec(
                    f"SELECT name FROM categories WHERE categoryID = {categoryID} AND userID = {self.userID}"):
                print(editScheduledTransaction.lastError().databaseText())
                return -1
            if editScheduledTransaction.next():
                category = editScheduledTransaction.value(0)
            else:
                return -1
            self.recurringCategoryEntry.setCurrentText(category)
            self.recurringAccountEntry.setCurrentText(account)
            self.recurringNotesEntry.setPlainText(notes)

            if sched == 'Recurring':
                self.recurringRecurRadioButton.setChecked(True)
                recur_n = [int(s) for s in recur.split() if s.isdigit()]

                if freq == 'Daily':
                    self.recurringFreqComboBox.setCurrentText('Daily')
                    self.recurringFreqDaySpinBox.setValue(recur_n[0])
                elif freq == 'Weekly':
                    self.recurringFreqComboBox.setCurrentText('Weekly')
                    self.recurringFreqWeekSpinBox.setValue(recur_n[0])
                    for checkBox in self.recurringDaysCheckBoxList:
                        if not checkBox.isChecked() and checkBox.text() in week_day:
                            checkBox.setChecked(True)
                        elif checkBox.isChecked() and checkBox.text() in week_day:
                            pass
                        else:
                            checkBox.setChecked(False)
                else:
                    self.recurringFreqComboBox.setCurrentText('Monthly')
                    self.recurringFreqMonthSpinBox.setValue(recur_n[0])
                    self.recurringOnDaySpinBox.setValue(int(month_day))

                timeObject = datetime.strptime(time_t, '%H:%M:%S').time()
                timeObjectStatus = (datetime.combine(date(1, 1, 1), timeObject) + timedelta(seconds=1)).time()
                self.recurringFreqOccursAtTimeEntry.setTime(timeObject)

                startDateObject = datetime.strptime(startDate, '%Y-%m-%d').date()
                self.recurringDurationStartDateEntry.setDate(startDateObject)

                if not endDate == 'no end date':
                    self.recurringDurationEndRadioButton.setChecked(True)
                    endDateObject = datetime.strptime(endDate, '%Y-%m-%d').date()
                    self.recurringDurationEndDateEntry.setDate(endDateObject)
                else:
                    self.recurringDurationNoEndRadioButton.setChecked(True)
            else:
                self.recurringOnceRadioButton.setChecked(True)
                startDateObject = datetime.strptime(startDate, '%Y-%m-%d').date()
                self.recurringOnceDateEntry.setDate(startDateObject)
                timeObject = datetime.strptime(time_t, '%H:%M:%S').time()
                # timeObjectStatus = (datetime.combine(date(1,1,1), timeObject) + timedelta(seconds = 1)).time()
                self.recurringOnceTimeEntry.setTime(timeObject)
            self.edited = False
            self.recurringApplyButton.clicked.connect(self.applyEditScheduledTransaction)
        else:
            editSchMsg.setWindowTitle("Info")
            editSchMsg.setText("Transaction is not selected!")
            editSchMsg.exec()

    def applyEditScheduledTransaction(self):
        if self.edited:
            return
        editJobMsg = QMessageBox()
        editJobMsg.setWindowTitle("Error")
        editJobMsg.setIcon(QMessageBox.Warning)
        characters = " !\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"
        rates = CurrencyRates()

        name = self.recurringNameEdit.text()
        if len(name) < 3:
            editJobMsg.setText("Name must be at least 3 characters long.")
            editJobMsg.exec()
            self.edited = True
            self.cancelEditScheduledTransaction()
            return
        elif any(char in characters for char in name):
            editJobMsg.setText("Name can only contain letters, digits and underscores!")
            editJobMsg.exec()
            self.edited = True
            self.cancelEditScheduledTransaction()
            return
        findJob = QSqlQuery()
        findJob.prepare("SELECT name FROM jobs WHERE name = :name AND userID = :userID")
        findJob.bindValue(":name", name)
        findJob.bindValue(":userID", self.userID)
        findJob.exec()
        if findJob.next():
            if findJob.value(0) == self.old_name:
                pass
            else:
                editJobMsg.setText("A job with that name already exists!")
                editJobMsg.exec()
                self.edited = True
                self.cancelEditScheduledTransaction()
                return
        jobName = "sched_" + self.login + "_" + name
        try:
            value = Decimal(self.recurringValueEntry.text()).quantize(self.fractional, ROUND_HALF_UP)
            if value <= 0:
                raise InvalidOperation
        except InvalidOperation:
            editJobMsg.setText("Amount must be a number!")
            editJobMsg.exec()
            self.edited = True
            self.cancelEditScheduledTransaction()
            return

        amount = str(value) + ' ' + self.recurringSymbolLabel.text()
        category = self.recurringCategoryEntry.currentText()
        account = self.recurringAccountEntry.currentText()
        notes = self.recurringNotesEntry.toPlainText()
        if len(notes) > 100:
            editJobMsg.setText("Notes length cannot be greater than 100 characters.")
            editJobMsg.exec()
            return
        if self.recurringExpenseRadioButton.isChecked():
            job_transaction_type = 'expenses'
            transaction_type = 'Expense'
            difference = (-1) * value
        elif self.recurringIncomeRadioButton.isChecked():
            job_transaction_type = 'income'
            transaction_type = 'Income'
            difference = Decimal(value).quantize(self.fractional, ROUND_HALF_UP)
        else:
            editJobMsg.setText("Type of transaction is not selected!")
            editJobMsg.exec()
            self.edited = True
            self.cancelEditScheduledTransaction()
            return

        editJobQuery = QSqlQuery()
        if not editJobQuery.exec(
                f"SELECT categoryID FROM categories WHERE name = '{category}' AND categoryType = '{job_transaction_type}' AND userID = {self.userID}"):
            print(editJobQuery.lastError().databaseText())
            return -1
        if editJobQuery.next():
            categoryID = editJobQuery.value(0)
        else:
            return -1
        if not editJobQuery.exec(f"SELECT accountID FROM accounts WHERE name = '{account}' AND userID = {self.userID}"):
            print(editJobQuery.lastError().databaseText())
            return -1
        if editJobQuery.next():
            accountID = editJobQuery.value(0)
        else:
            return -1

        findCurrencyQuery = QSqlQuery()
        findCurrencyQuery.exec(f"SELECT currency FROM accounts WHERE name = '{account}' AND userID = '{self.userID}';")
        if findCurrencyQuery.next():
            accCurrency = findCurrencyQuery.value(0)
        findCurrencyQuery.finish()
        if accCurrency != self.currencyCode:
            convertedValue = (rates.convert(accCurrency, self.currencyCode, value)).quantize(self.fractional,
                                                                                             ROUND_HALF_UP)
        else:
            convertedValue = value
        findCurrencyQuery.finish()

        schedule_name = jobName + '_schedule'
        step_name1 = jobName + '_step1'
        step_name2 = jobName + '_step2'

        status_job_name = jobName + '_status'
        status_job_schedule_name = jobName + '_status_schedule'
        status_job_step_name = jobName + '_status_step'

        if self.recurringRecurEnabledCheckBox.isChecked():
            status = 'Enabled'
            job_status = 1
        else:
            status = 'Disabled'
            job_status = 0

        daysDict = {'Mon': 2, 'Tue': 4, 'Wed': 8, 'Thu': 16, 'Fri': 32, 'Sat': 64, 'Sun': 1}

        if self.recurringOnceRadioButton.isChecked():

            type_s = 'One time'
            frequency = 'n/a'
            recurrence = 'n/a'
            month_day = 'n/a'
            week_day = 'n/a'
            end_date = 'n/a'
            freq_type = 1
            freq_interval = 0
            freq_recurrence_factor = 0

            tempVar1 = self.recurringOnceDateEntry.date()
            tempDate = tempVar1.toPyDate()
            tempDateStatus = tempDate + timedelta(days=1)

            tempVar2 = self.recurringOnceTimeEntry.time()
            tempTime = tempVar2.toPyTime()
            tempTimeStatus = (datetime.combine(date(1, 1, 1), tempTime) + timedelta(seconds=1)).time()

            startDate = str(tempDate).translate({ord(i): None for i in '-'})
            startDateStatus = str(tempDateStatus).translate({ord(i): None for i in '-'})

            startTime = (str(tempTime).translate({ord(i): None for i in ':'})).split('.')[0]

            start_date = str(tempDate)
            start_time = (str(tempTime)).split('.')[0]

            startTimeStatus = (str(tempTimeStatus).translate({ord(i): None for i in ':'})).split('.')[0]
            active_start_time_status = startTimeStatus

            if int(startTimeStatus) == 0:
                active_start_date_status = startDateStatus
            else:
                active_start_date_status = startDate

            active_start_date = startDate
            active_start_time = startTime
            active_end_date = 99991231
            active_end_date_status = 99991231
            active_end_time = 235959

        if self.recurringRecurRadioButton.isChecked():
            type_s = 'Recurring'
            if self.recurringFreqComboBox.currentText() == 'Daily':
                frequency = 'Daily'
                recurrence = 'Every ' + str(self.recurringFreqDaySpinBox.value()) + ' day(s)'
                month_day = 'n/a'
                week_day = 'n/a'
                freq_type = 4
                freq_interval = self.recurringFreqDaySpinBox.value()
                freq_recurrence_factor = 0
            if self.recurringFreqComboBox.currentText() == 'Weekly':
                frequency = 'Weekly'
                recurrence = 'Every ' + str(self.recurringFreqWeekSpinBox.value()) + ' week(s)'
                month_day = 'n/a'
                week_day_list = []
                freq_type = 8
                days_sum = 0
                for checkBox in self.recurringDaysCheckBoxList:
                    if checkBox.isChecked():
                        days_sum += daysDict[checkBox.text()]
                        week_day_list.append(checkBox.text())
                if days_sum == 0:
                    editJobMsg.setText("At least one day must be selected!")
                    editJobMsg.exec()
                    self.edited = True
                    self.cancelEditScheduledTransaction()
                    return
                week_day = ','.join(week_day_list)
                freq_interval = days_sum
                freq_recurrence_factor = self.recurringFreqWeekSpinBox.value()
            if self.recurringFreqComboBox.currentText() == 'Monthly':
                frequency = 'Monthly'
                recurrence = 'Every ' + str(self.recurringFreqMonthSpinBox.value()) + ' month(s)'
                month_day = self.recurringOnDaySpinBox.value()
                week_day = 'n/a'
                freq_type = 16
                freq_interval = self.recurringOnDaySpinBox.value()
                freq_recurrence_factor = self.recurringFreqMonthSpinBox.value()

            tempVar1 = self.recurringFreqOccursAtTimeEntry.time()
            tempTime = tempVar1.toPyTime()
            tempTimeStatus = (datetime.combine(date(1, 1, 1), tempTime) + timedelta(seconds=1)).time()

            startTime = (str(tempTime).translate({ord(i): None for i in ':'})).split('.')[0]
            startTimeStatus = (str(tempTimeStatus).translate({ord(i): None for i in ':'})).split('.')[0]
            start_time = (str(tempTime)).split('.')[0]

            active_start_time = startTime
            active_end_time = 235959
            active_start_time_status = startTimeStatus

            tempVar2 = self.recurringDurationStartDateEntry.date()
            tempSDate = tempVar2.toPyDate()
            tempSDateStatus = tempSDate + timedelta(days=1)
            startDate = str(tempSDate).translate({ord(i): None for i in '-'})
            startDateStatus = str(tempSDateStatus).translate({ord(i): None for i in '-'})
            start_date = str(tempSDate)
            active_start_date = startDate

            if int(startTimeStatus) == 0:
                active_start_date_status = startDateStatus
            else:
                active_start_date_status = startDate

            if self.recurringDurationEndRadioButton.isChecked():
                tempVar3 = self.recurringDurationEndDateEntry.date()
                tempEDate = tempVar3.toPyDate()
                if tempEDate < tempSDate:
                    editJobMsg.setText("Date!")
                    editJobMsg.exec()
                    self.edited = True
                    self.cancelEditScheduledTransaction()
                    return
                tempEDateStatus = tempEDate + timedelta(days=1)

                endDate = str(tempEDate).translate({ord(i): None for i in '-'})
                endDateStatus = str(tempEDateStatus).translate({ord(i): None for i in '-'})
                end_date = str(tempEDate)
                active_end_date = endDate

                if int(startTimeStatus) == 0:
                    active_end_date_status = endDateStatus
                else:
                    active_end_date_status = endDate
            else:
                end_date = 'no end date'
                active_end_date = 99991231
                active_end_date_status = 99991231

        asd = editJobQuery.exec(f"UPDATE jobs "
                                f"SET name='{name}',status='{status}',type_t='{transaction_type}',value='{amount}',categoryID={categoryID},accountID={accountID},notes='{notes}',type_s='{type_s}',frequency='{frequency}',recurrence='{recurrence}',month_day='{month_day}',week_day='{week_day}',time='{start_time}',start_date='{start_date}',end_date='{end_date}',originValue={value} "
                                f"WHERE name = '{self.old_name}' AND userID = '{self.userID}';")

        error1 = editJobQuery.lastError()
        print(error1.databaseText())

        jobQuery = QSqlQuery()
        query = f"""USE msdb ;
    EXEC dbo.sp_update_job  
        @job_name = N'{self.old_job_name}',
        @new_name = N'{jobName}' ;
    EXEC sp_update_jobstep
        @step_id = 1,
        @job_name = N'{jobName}',  
        @step_name = N'{step_name1}',  
        @subsystem = N'TSQL',  
        @command = N'INSERT INTO Baza.dbo.{job_transaction_type} (amount,categoryID,accountID,transactionDate,notes,value,originValue,userID,currency) VALUES ("{amount}", "{categoryID}", "{accountID}", CONVERT(date,getdate()), "{notes}", {convertedValue}, {value}, "{self.userID}", "{accCurrency}");',
        @on_success_action = 3,
        @retry_attempts = 0,  
        @retry_interval = 0 ;
    EXEC sp_update_jobstep
        @step_id = 2,
        @job_name = N'{jobName}',  
        @step_name = N'{step_name2}',  
        @subsystem = N'TSQL',  
        @command = N'UPDATE Baza.dbo.accounts SET currAmount = (SELECT currAmount FROM Baza.dbo.accounts WHERE accountID = "{accountID}") + {difference} WHERE accountID = "{accountID}" AND userID = "{self.userID}";',
        @retry_attempts = 0,  
        @retry_interval = 0 ;
    EXEC dbo.sp_update_schedule  
        @name = N'{self.old_schedule_name}',
        @new_name = N'{schedule_name}',
        @enabled = {job_status},
        @freq_type = {freq_type},
        @freq_interval = {freq_interval}, 
        @freq_relative_interval = 0, 
        @freq_recurrence_factor = {freq_recurrence_factor},
        @active_start_date = {active_start_date},
        @active_end_date = {active_end_date},
        @active_start_time = {active_start_time},
        @active_end_time = {active_end_time} ;
    EXEC dbo.sp_update_job  
        @job_name = N'{self.old_status_job_name}',
        @new_name = N'{status_job_name}' ;
    EXEC sp_update_jobstep
        @step_id = 1,
        @job_name = N'{status_job_name}',  
        @step_name = N'{status_job_step_name}',  
        @subsystem = N'TSQL',  
        @command = N'UPDATE Baza.dbo.jobs SET status = (SELECT enabled FROM msdb.dbo.sysschedules WHERE name = "{schedule_name}") WHERE name = "{name}";',
        @retry_attempts = 0,  
        @retry_interval = 0 ;
    EXEC dbo.sp_update_schedule
        @name = N'{self.old_status_job_schedule_name}',
        @new_name = N'{status_job_schedule_name}',
        @enabled = {job_status},
        @freq_type = {freq_type},
        @freq_interval = {freq_interval}, 
        @freq_relative_interval = 0, 
        @freq_recurrence_factor = {freq_recurrence_factor},
        @active_start_date = {active_start_date_status},
        @active_end_date = {active_end_date_status},
        @active_start_time = {active_start_time_status},
        @active_end_time = {active_end_time} ;
    USE Baza ;"""

        isValid = jobQuery.exec(query)
        error = jobQuery.lastError()
        print(error.databaseText())
        self.fillJobsTable()

        self.clearRecurringTrInfo()
        self.cancelEditScheduledTransaction()
        self.recurringEditStackedLayout.setCurrentIndex(0)
        self.edited = True

    def cancelEditScheduledTransaction(self):
        self.recurringEditStackedLayout.setCurrentIndex(0)
        self.clearRecurringTrInfo()
        self.recurringRecurRadioButton.setChecked(True)
        self.recurringRecurEnabledCheckBox.setChecked(True)
        self.recurringOnceDateEntry.setDate(date.today())
        self.recurringOnceTimeEntry.setTime(datetime.now().time())
        self.recurringFreqComboBox.setCurrentText('Daily')
        self.recurringFreqDaySpinBox.setValue(1)
        self.recurringFreqWeekSpinBox.setValue(1)
        self.recurringFreqMonthSpinBox.setValue(1)
        self.recurringOnDaySpinBox.setValue(1)
        for checkBox in self.recurringDaysCheckBoxList:
            if checkBox.isChecked():
                checkBox.setChecked(False)
        self.recurringFreqOccursAtTimeEntry.setTime(QTime(0, 0, 0))
        self.recurringDurationStartDateEntry.setDate(date.today())
        self.recurringDurationEndDateEntry.setDate(date.today())
        self.recurringDurationNoEndRadioButton.setChecked(True)