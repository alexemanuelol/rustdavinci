#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from ui.dialogs.settingsui import Ui_SettingsUI


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

        self.load_settings()
        self.connect_all()


    def load_settings(self):
        None

    def connect_all(self):
        self.ui.cancelPushButton.clicked.connect(self.close)



if __name__ == "__main__":
    QtCore.QCoreApplication.setOrganizationName("RustDaVinci")
    QtCore.QCoreApplication.setApplicationName("RustDaVinci")
    app = QtWidgets.QApplication(sys.argv)
    settings = Settings()
    settings.setModal(True)
    settings.show()
    sys.exit(app.exec_())
