#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QAction, QPushButton, QVBoxLayout, QGroupBox, QMenu
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, QRect

class MainWindow(QtWidgets.QMainWindow):

    closeEventSignal = QtCore.pyqtSignal(QtGui.QCloseEvent)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.title = "RustDaVinci"
        self.width = 240
        self.height = 400
        self._initUI()


    def _initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon("../images/RustDaVinci-icon.ico"))
        self.resize(self.width, self.height)
        self.setMinimumSize(QSize(self.width, self.height))

        loadImageButton = QPushButton("               Load Image...             ", self)
        loadImageButton.setGeometry(QRect(10, 10, self.width - 20, 45))
        loadImageButton.setFlat(True)
        loadImageButton.setIcon(QtGui.QIcon("../images/load_image_icon.png"))
        loadImageButton.setIconSize(QtCore.QSize(self.width - 20, 45))

        loadMenu = QtWidgets.QMenu()
        loadMenu.addAction("Load from File", self.loadImageFile)
        loadMenu.addAction("Load from URL", self.loadImageURL)
        loadMenu.addAction("Clear image", self.clearCurrentImage)
        loadImageButton.setMenu(loadMenu)

        settingsButton = QPushButton("    Identify palette and frame...", self)
        settingsButton.setGeometry(QRect(10, 65, self.width - 20, 45))
        settingsButton.setFlat(True)
        settingsButton.setIcon(QtGui.QIcon("../images/select_area_icon.png"))
        settingsButton.setIconSize(QtCore.QSize(self.width - 20, 45))
        settingsButton.clicked.connect(self.identifyAreas)

        paintImageButton = QPushButton("               Paint Image...            ", self)
        paintImageButton.setGeometry(QRect(10, 120, self.width - 20, 45))
        paintImageButton.setFlat(True)
        paintImageButton.setEnabled(False)
        paintImageButton.setIcon(QtGui.QIcon("../images/paint_image_icon.png"))
        paintImageButton.setIconSize(QtCore.QSize(self.width - 20, 45))
        paintImageButton.clicked.connect(self.startPainting)

        settingsButton = QPushButton("                 Settings                    ", self)
        settingsButton.setGeometry(QRect(10, 175, self.width - 20, 45))
        settingsButton.setFlat(True)
        settingsButton.setIcon(QtGui.QIcon("../images/settings_icon.png"))
        settingsButton.setIconSize(QtCore.QSize(self.width - 20, 45))
        settingsButton.clicked.connect(self.settings)

    def loadImageFile(self):
        print("load image file...")

    def loadImageURL(self):
        print("load image URL...")

    def clearCurrentImage(self):
        print("Cleared the current Image...")

    def identifyAreas(self):
        print("Identify palette and frame...")

    def startPainting(self):
        print("Start painting")

    def settings(self):
        print("Settings")



    def show(self):
        super(MainWindow, self).show()


    def hide(self):
        super(MainWindow, self).hide()


    def closeEvent(self, closeEvent):
        super(MainWindow, self).closeEvent(closeEvent)
        self.closeEventSignal.emit(closeEvent)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
