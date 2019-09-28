#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from ui.settings.settingsui import Ui_SettingsUI


class Settings(QtWidgets.QDialog):

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)

        self.ui = Ui_SettingsUI()
        self.ui.setupUi(self)
        self.settings = QtCore.QSettings()
        self.setWindowFlags(
                QtCore.Qt.Dialog |
                QtCore.Qt.MSWindowsFixedSizeDialogHint |
                QtCore.Qt.WindowSystemMenuHint |
                QtCore.Qt.WindowTitleHint |
                QtCore.Qt.WindowCloseButtonHint)

        self.loadSettings()
        self.connectAll()


    def loadSettings(self):
        None

    def connectAll(self):
        # Buttons
        self.ui.defaultPushButton.clicked.connect(self.setDefaultSettings)
        self.ui.okPushButton.clicked.connect(self.saveAndExit)
        self.ui.cancelPushButton.clicked.connect(self.close)
        self.ui.applyPushButton.clicked.connect(self.saveSettings)

        # General
        self.ui.backgroundColorLineEdit.textChanged.connect(self.setBackgroundColor)
        

    def setDefaultSettings(self):
        print("Setting default settings...")
        None

    def saveAndExit(self):
        self.saveSettings()
        print("Exit Settings...")
        self.close()

    def saveSettings(self):
        print("Save Settings...")

    def setBackgroundColor(self):
        print("Set Background color...")



if __name__ == "__main__":
    QtCore.QCoreApplication.setOrganizationName("RustDaVinci")
    QtCore.QCoreApplication.setApplicationName("RustDaVinci")
    app = QtWidgets.QApplication(sys.argv)
    settings = Settings()
    settings.setModal(True)
    settings.show()
    sys.exit(app.exec_())
