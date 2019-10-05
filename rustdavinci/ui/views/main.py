#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QAction, QPushButton, QVBoxLayout, QGroupBox, QMenu
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, QRect

from ui.settings.settings import Settings
from lib.rustDaVinci import rustDaVinci

from ui.views.mainui import Ui_MainUI

class MainWindow(QtWidgets.QMainWindow):

    closeEventSignal = QtCore.pyqtSignal(QtGui.QCloseEvent)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.ui = Ui_MainUI()
        self.ui.setupUi(self)

        self.settings = QtCore.QSettings()
        self.rustDaVinci = rustDaVinci(self)

        # Menu actions
        self.action_clearImage = None
        self.action_locateControlArea = None

        self.connectAll()



    def connectAll(self):
        """ Connect all the buttons """
        loadMenu = QtWidgets.QMenu()
        loadMenu.addAction("From File...", self.loadImageFile_clicked)
        loadMenu.addAction("From URL...", self.loadImageURL_clicked)
        self.action_clearImage = loadMenu.addAction("Clear image", self.clearCurrentImage_clicked)
        self.action_clearImage.setEnabled(False)
        self.ui.loadImagePushButton.setMenu(loadMenu)

        identifyMenu = QtWidgets.QMenu()
        identifyMenu.addAction("Canvas...", self.locateCanvasArea_clicked)
        self.action_locateControlArea = identifyMenu.addAction("Painting Controls...", self.locateControlArea_clicked)
        self.action_locateControlArea.setEnabled(True)
        self.ui.identifyAreasPushButton.setMenu(identifyMenu)

        paintMenu = QtWidgets.QMenu()
        self.action_paintImage = paintMenu.addAction("Paint Image", self.paintImage_clicked)
        self.action_paintImage.setEnabled(False)
        self.action_showPreview = paintMenu.addAction("Show Preview", self.showPreview_clicked)
        self.action_showPreview.setEnabled(False)
        self.ui.paintImagePushButton.setMenu(paintMenu)

        self.ui.settingsPushButton.clicked.connect(self.settings_clicked)


    def loadImageFile_clicked(self):
        self.rustDaVinci.load_image_from_file()
        if self.rustDaVinci.image_path != None:
            self.action_clearImage.setEnabled(True)

    def loadImageURL_clicked(self):
        self.rustDaVinci.load_image_from_url()
        if self.rustDaVinci.image_path != None:
            self.action_clearImage.setEnabled(True)

    def clearCurrentImage_clicked(self):
        self.rustDaVinci.clear_image()
        self.action_clearImage.setEnabled(False)

    def locateCanvasArea_clicked(self):
        self.rustDaVinci.locate_canvas_area()

    def locateControlArea_clicked(self):
        self.rustDaVinci.locate_control_area()

    def paintImage_clicked(self):
        None

    def showPreview_clicked(self):
        None

    def settings_clicked(self):
        settings = Settings(self)
        settings.setModal(True)
        settings.show()


    def show(self):
        super(MainWindow, self).show()

    def hide(self):
        super(MainWindow, self).hide()

    def closeEvent(self, closeEvent):
        super(MainWindow, self).closeEvent(closeEvent)
        self.closeEventSignal.emit(closeEvent)
