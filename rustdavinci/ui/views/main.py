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

        self.connectAll()
        self.rustDaVinci.update_status()



    def connectAll(self):
        """ Connect all the buttons """
        loadMenu = QtWidgets.QMenu()
        loadMenu.addAction("From File...", self.loadImageFile_clicked)
        loadMenu.addAction("From URL...", self.loadImageURL_clicked)
        self.action_clearImage = loadMenu.addAction("Clear image", self.clearCurrentImage_clicked)
        self.action_clearImage.setEnabled(False)
        self.ui.loadImagePushButton.setMenu(loadMenu)

        identifyMenu = QtWidgets.QMenu()
        identifyMenu.addAction("Manually", self.locateControlAreaManually_clicked)
        identifyMenu.addAction("Automatically", self.locateControlAreaAutomatically_clicked)
        self.ui.identifyAreasPushButton.setMenu(identifyMenu)

        self.ui.paintImagePushButton.clicked.connect(self.paintImage_clicked)
        self.ui.settingsPushButton.clicked.connect(self.settings_clicked)

    def initial_setup(self):
        None


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

    def locateControlAreaManually_clicked(self):
        self.rustDaVinci.locate_control_area_manually()

    def locateControlAreaAutomatically_clicked(self):
        self.rustDaVinci.locate_control_area_automatically()

    def paintImage_clicked(self):
        self.rustDaVinci.start_painting()

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
