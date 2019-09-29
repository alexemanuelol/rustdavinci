#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QAction, QPushButton, QVBoxLayout, QGroupBox, QMenu
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, QRect

from ui.settings.settings import Settings

from ui.views.mainui import Ui_MainUI

class MainWindow(QtWidgets.QMainWindow):

    closeEventSignal = QtCore.pyqtSignal(QtGui.QCloseEvent)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.ui = Ui_MainUI()
        self.ui.setupUi(self)

        self.settings = QtCore.QSettings()

        self.connectAll()



    def connectAll(self):
        """ Connect all the buttons """
        loadMenu = QtWidgets.QMenu()
        loadMenu.addAction("Load from File", self.loadImageFile_clicked)
        loadMenu.addAction("Load from URL", self.loadImageURL_clicked)
        loadMenu.addAction("Show preview", self.showPreview_clicked)
        loadMenu.addAction("Clear image", self.clearCurrentImage_clicked)
        self.ui.loadImagePushButton.setMenu(loadMenu)

        self.ui.identifyAreasPushButton.clicked.connect(self.identifyAreas_clicked)
        self.ui.paintImagePushButton.clicked.connect(self.startPainting_clicked)
        self.ui.settingsPushButton.clicked.connect(self.settings_clicked)


    def loadImageFile_clicked(self):
        print("load image file...")

    def loadImageURL_clicked(self):
        print("load image URL...")

    def showPreview_clicked(self):
        print("Showing preview of dithered image...")

    def clearCurrentImage_clicked(self):
        print("Cleared the current Image...")

    def identifyAreas_clicked(self):
        print("Identify palette and frame...")

    def startPainting_clicked(self):
        print("Start painting")

    def settings_clicked(self):
        settings = Settings(self)
        settings.setModal(True)
        settings.show()
        print("Settings")


    def show(self):
        super(MainWindow, self).show()

    def hide(self):
        super(MainWindow, self).hide()

    def closeEvent(self, closeEvent):
        super(MainWindow, self).closeEvent(closeEvent)
        self.closeEventSignal.emit(closeEvent)
