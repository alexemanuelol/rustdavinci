#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore
from PtQt5 import QtGui
from PyQt5 import QtWidgets

class Settings(QtWidgets.QDialog):

    def __init__(self):
        QtWidgets.QDialog.__init__(self, parent)



if __name__ == "__main__":
    QtCore.QCoreApplication.setOrganizationName("RustDaVinci")
    QtCore.QCoreApplication.setApplicationName("RustDaVinci")
    app = QtGui.QApplication(sys.argv)
    s = Settings()
    s.show()
    sys.exit(app.exec_())
