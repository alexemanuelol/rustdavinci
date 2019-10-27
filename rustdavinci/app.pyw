#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5 import QtWidgets

import sys

from ui.views.main import MainWindow


def run():

    # Set some application settings for QSettings
    QtCore.QCoreApplication.setOrganizationName("RustDaVinci")
    QtCore.QCoreApplication.setApplicationName("RustDaVinci")

    # Setup the application and start
    app = QtWidgets.QApplication(sys.argv)

    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
