#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TRGUI.py

__author__ = "Adrian Torres"
__date__ = "2013-11-02"
__version__ = "1.0"


import sys
import TRCore
import parsing
import pickle
from loginGUI import Ui_Dialog
from mainGUI import Ui_mainScreen
from PySide.QtCore import *
from PySide.QtGui import *


class LoginDialog(QDialog, Ui_Dialog):
    
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        # setupUi is a function generated by the QtDesigner 4
        # that allows us to implement the GUI into our code
        self.setupUi(self)
        # we connect the login button to the login function defined
        # below
        self.buttonLogin.clicked.connect(self.login)
        # we try to load saved info
        self.loadLogin()
    
    def login(self):
        usr = self.usrEntry.text()
        pwd = self.pwdEntry.text()
        srv = self.srvEntry.text()
        # we get the user input
        login = LoginThread(usr, pwd, srv)
        if login.run():
            # if login was successful, we greet the user
            QMessageBox.information(self, "Login", "Login Successful!")
            if self.checkRemember.isChecked():
                # and if the remember credentials checkbox is checked
                # we save the credentials
                self.saveLogin(usr, pwd, srv)
            self.close()
            self.emit(SIGNAL("loadMain()"))
            # and we change to a new window // TODO
        else:
            # else, we tell the user that the login was unsuccessful
            QMessageBox.warning(self, "Login", "Invalid credentials")
    
    def saveLogin(self, usr, pwd, srv):
        toRemember = [usr, pwd, srv]
        with open("login", "w") as f:
            # we dump the credentials in the login file
            pickle.dump(toRemember, f)
            
    def loadLogin(self):
        try:
            # we try to open the login file
            with open("login", "r") as f:
                credentials = pickle.load(f)
            # and we set the entries to the credentials
            self.usrEntry.setText(str(credentials[0]))
            self.pwdEntry.setText(str(credentials[1]))
            self.srvEntry.setText(str(credentials[2]))
        except:
            # if we cannot open the file, we do nothing
            pass

class mainScreen(QTabWidget, Ui_mainScreen):
    
    def __init__(self, parent=None):
        super(mainScreen, self).__init__(parent)
        self.setupUi(self)
        # we setup the GUI, required when working with the QtDesigner4
        self.connect(loginDialog, SIGNAL("loadMain()"), self.loadMain)
        # we connect a signal from the loginDialog so that we can load up
        # the main program with loadMain
        self.raidlistName = "raidlist.txt"
        self.buttonRaid.clicked.connect(self.raidIt)
        self.buttonAdd.clicked.connect(self.addItem)
        self.buttonDelete.clicked.connect(self.deleteSelectedItems)
        self.buttonDeleteAll.clicked.connect(self.deleteAll)
        self.raidProgress.setValue(0)
        
    def addItem(self):
        # adds one empty item to the raidlist
        new = [4, (0, 0), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        TRCore.addToRaidlist(new, self.raidlistName)
        self.updateScreen()
    
    def deleteAll(self):
        # prompts the user with a question box, asking if he truly desires
        # to delete all the raids in the raidlist
        a = QMessageBox.question(self, "Delete All", "Are you sure you want to delete all the raids?", QMessageBox.Yes, QMessageBox.No)
        if a == 16384:
            # if so, all the items are deleted
            TRCore.deleteAll(self.raidlistName)
            self.raidTable.clearContents()
            self.updateScreen()
        else:
            # otherwise we do nothing
            pass
        
    def editCell(self, row, col):
        # first we get the desired item
        item = self.raidTable.item(row, col)
        try:
            # we check if the input is valid by casting it into an int
            newValue = int(item.text())
            # coordinates are special cells because of the raidlist.txt
            # format (should change this)
            if col == 11:
                TRCore.editAtIndex(self.raidlistName, row, col, newValue, flag="x")
            elif col == 12:
                TRCore.editAtIndex(self.raidlistName, row, col, newValue, flag="y")
            else:
                TRCore.editAtIndex(self.raidlistName, row, col, newValue)
        except:
            # if the input is invalid, then we set the cell to whatever it was
            # before trying to edit it
            updateScreen()
    
    def deleteSelectedItems(self):
        rows = []
        # gets the selected item
        for e in self.raidTable.selectedRanges():
            i = e.topRow()
            rows.append(i)
        # then removes them from the raidlist by its index
        TRCore.removeAtIndexes(self.raidlistName, rows)
        # and updates the screen
        self.updateScreen()
        
    def updateScreen(self):
        # first, we get the most recent version of the raidlist
        raidlist = TRCore.read(self.raidlistName)
        raids = len(raidlist)
        # then we set the table's rowCount to the number of raids
        self.raidTable.setRowCount(raids)
        for i in range(raids):
            # we create a horizontal item representing a raid
            item = QTableWidgetItem()
            self.raidTable.setVerticalHeaderItem(i, item)
            for j in range(len(raidlist[i][1:])):
                # then we create a column item representing each troop type
                if j == 0:
                    # except for the first item, which is a tuple containing the coordinates
                    item = QTableWidgetItem()
                    item.setText(str(raidlist[i][j+1][0]))
                    self.raidTable.setItem(i, 11, item)
                    item = QTableWidgetItem()
                    item.setText(str(raidlist[i][j+1][1]))
                    self.raidTable.setItem(i, 12, item)
                else:
                    item = QTableWidgetItem()
                    item.setText(str(raidlist[i][j+1]))
                    self.raidTable.setItem(i, j-1, item)
        # finally, we set the progressbar's range from 0 up to the number of raids
        self.raidProgress.setRange(0, raids)
    
    def loadMain(self):
        self.move(QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())
        # we center the frame
        self.show()
        # then we show it
        self.tribe = parsing.checkTribe(TRCore.b)
        # we check the user's tribe
        for i in range(13):
            # we fill the table's header with the corresponding icons
            if i < 10:
                icon = QIcon()
                icon.addPixmap(QPixmap(":/img/t"+str(i+1)+"_"+self.tribe), QIcon.Normal, QIcon.Off)
                item = QTableWidgetItem()
                item.setIcon(icon)
                # 0 -> 9 are troop icons
            elif i == 10:
                icon = QIcon()
                icon.addPixmap(QPixmap(":/img/hero"), QIcon.Normal, QIcon.Off)
                item = QTableWidgetItem()
                item.setIcon(icon)
                # 10 is the hero icon
            else:
                # 11 is the X coordinate and 12 is the Y coordinate
                if i == 11:
                    item = QTableWidgetItem("X")
                else:
                    item = QTableWidgetItem("Y")
            self.raidTable.setHorizontalHeaderItem(i, item)
        # we update the screen to display all the raids
        self.updateScreen()
        # we create a RaidThread object
        self.raidT = RaidThread()
        # the raidT object yields 1 each time a raid from the raidlist
        # has been executed, which makes the progressbar advance
        self.connect(self.raidT, SIGNAL("raided(int)"), self.raidProgress, SLOT("setValue(int)"))
        # if the user tries to edit a cell, we call the editCell function
        self.connect(self.raidTable, SIGNAL("cellChanged(int, int)"), self.editCell)
    
    def raidIt(self):
        # we reset the progressbar
        self.raidProgress.reset()
        # and we start the thread
        self.raidT.start()

class RaidThread(QThread):
    
    def __init__(self, parent=None, raidlist="raidlist.txt"):
        super(RaidThread, self).__init__(parent)
        self.raidlist = raidlist
    
    def raidIt(self, raidlist):
        raiding = TRCore.raid(raidlist)
        # we create raiding, a generator object
        c = True
        i = 1
        while c:
            try:
                raiding.next()
                # we call .next sequentially, which raids until all the
                # raids from the raidlist have been executed
                self.emit(SIGNAL("raided(int)"), i)
                # then we emit the raid index (i)
                i += 1
            except:
                c = False
    
    def run(self):
        self.raidIt(self.raidlist)
        
class LoginThread(QThread):
    
    # basically a thread for logging in, to avoid program freezing
    
    def __init__(self, usr, pwd, srv, parent=None):
        super(LoginThread, self).__init__(parent)
        self.usr = usr
        self.pwd = pwd
        self.srv = srv
    
    def run(self):
        return TRCore.login(self.srv, self.usr, self.pwd)
        

app = QApplication(sys.argv)
loginDialog = LoginDialog()
loginDialog.show()
mainDialog = mainScreen()

app.exec_()