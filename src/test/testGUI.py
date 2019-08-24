#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets


def run():
    QtCore.QCoreApplication.setOrganizationName("RustDaVinci")
    QtCore.QCoreApplication.setApplicationName("RustDaVinci")

    app = QtWidgets.QApplication(sys.argv)
    app.exec_()
    sys.exit()



if __name__ == "__main__":
    run()
