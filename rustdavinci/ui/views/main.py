#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QAction, QPushButton, QVBoxLayout, QGroupBox, QMenu
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, QRect

from ui.settings.settings import Settings

#from ui.views.mainui import Ui_MainUI

class MainWindow(QtWidgets.QMainWindow):

    closeEventSignal = QtCore.pyqtSignal(QtGui.QCloseEvent)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.title = "RustDaVinci"
        self.width = 240
        self.height = 400
        self._initUI()

        #self.ui = Ui_MainUI()
        #self.ui.setupUi(self)
        #self.settings = QtCore.QSettings()


    def loadImageFile(self):
        print("load image file...")

    def loadImageURL(self):
        print("load image URL...")

    def showPreview(self):
        print("Showing preview of dithered image...")

    def clearCurrentImage(self):
        print("Cleared the current Image...")

    def identifyAreas(self):
        print("Identify palette and frame...")

    def startPainting(self):
        print("Start painting")

    def settings(self):
        settings = Settings(self)
        settings.setModal(True)
        settings.show()
        print("Settings")



    def show(self):
        super(MainWindow, self).show()


    def hide(self):
        super(MainWindow, self).hide()


    def _initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon("../images/RustDaVinci-icon.ico"))
        self.resize(self.width, self.height)
        self.setMinimumSize(QSize(self.width, self.height))

        loadImagePushButton = QPushButton("               Load Image...             ", self)
        loadImagePushButton.setGeometry(QRect(10, 10, self.width - 20, 45))
        loadImagePushButton.setFlat(True)
        loadImagePushButton.setIcon(QtGui.QIcon("../images/load_image_icon.png"))
        loadImagePushButton.setIconSize(QtCore.QSize(self.width - 20, 45))

        loadMenu = QtWidgets.QMenu()
        loadMenu.addAction("Load from File", self.loadImageFile)
        loadMenu.addAction("Load from URL", self.loadImageURL)
        loadMenu.addAction("Show preview", self.showPreview)
        loadMenu.addAction("Clear image", self.clearCurrentImage)
        loadImagePushButton.setMenu(loadMenu)

        identifyAreasPushButton = QPushButton("    Identify palette and frame...", self)
        identifyAreasPushButton.setGeometry(QRect(10, 65, self.width - 20, 45))
        identifyAreasPushButton.setFlat(True)
        identifyAreasPushButton.setIcon(QtGui.QIcon("../images/select_area_icon.png"))
        identifyAreasPushButton.setIconSize(QtCore.QSize(self.width - 20, 45))
        identifyAreasPushButton.clicked.connect(self.identifyAreas)

        paintImagePushButton = QPushButton("               Paint Image...            ", self)
        paintImagePushButton.setGeometry(QRect(10, 120, self.width - 20, 45))
        paintImagePushButton.setFlat(True)
        paintImagePushButton.setEnabled(False)
        paintImagePushButton.setIcon(QtGui.QIcon("../images/paint_image_icon.png"))
        paintImagePushButton.setIconSize(QtCore.QSize(self.width - 20, 45))
        paintImagePushButton.clicked.connect(self.startPainting)

        settingsPushButton = QPushButton("                 Settings                    ", self)
        settingsPushButton.setGeometry(QRect(10, 175, self.width - 20, 45))
        settingsPushButton.setFlat(True)
        settingsPushButton.setIcon(QtGui.QIcon("../images/settings_icon.png"))
        settingsPushButton.setIconSize(QtCore.QSize(self.width - 20, 45))
        settingsPushButton.clicked.connect(self.settings)


    def closeEvent(self, closeEvent):
        super(MainWindow, self).closeEvent(closeEvent)
        self.closeEventSignal.emit(closeEvent)
