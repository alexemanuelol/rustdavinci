#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets

class MainWindow(QtWidgets.QMainWindow):

    closeEventSignal = QtCore.pyqtSignal(QtGui.QCloseEvent)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.resize(600,300)

    def show(self):
        super(MainWindow, self).show()

    def hide(self):
        super(MainWindow, self).hide()

    def closeEvent(self, closeEvent):
        super(MainWindow, self).closeEvent(closeEvent)
        self.closeEventSignal.emit(closeEvent)





def run():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("RustDaVinci")

    main = MainWindow()
    main.show()

    app.exec_()
    sys.exit()



if __name__ == "__main__":
    run()
