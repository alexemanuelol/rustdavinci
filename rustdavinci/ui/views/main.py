#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMenu

from ui.settings.settings import Settings
from lib.rustDaVinci import rustDaVinci

from ui.views.mainui import Ui_MainUI

class MainWindow(QtWidgets.QMainWindow):

    closeEventSignal = QtCore.pyqtSignal(QtGui.QCloseEvent)

    def __init__(self, parent=None):
        """ Main window init """
        super(MainWindow, self).__init__(parent)

        # Setup UI
        self.ui = Ui_MainUI()
        self.ui.setupUi(self)

        # Setup settings object
        self.settings = QtCore.QSettings()

        # Setup rustDaVinci object
        self.rustDaVinci = rustDaVinci(self)

        # Clear Image action
        self.action_clearImage = None
        
        # Connect UI modules
        self.connectAll()

        # Update the rustDaVinci module
        self.rustDaVinci.update()


    def connectAll(self):
        """ Connect all the buttons """
        # Add actions to the loadImagePushButton
        loadMenu = QtWidgets.QMenu()
        loadMenu.addAction("From File...", self.loadImageFile_clicked)
        loadMenu.addAction("From URL...", self.loadImageURL_clicked)
        self.action_clearImage = loadMenu.addAction("Clear image", self.clearCurrentImage_clicked)
        self.action_clearImage.setEnabled(False)
        self.ui.loadImagePushButton.setMenu(loadMenu)

        # Add actions to the identifyAreasPushButton
        identifyMenu = QtWidgets.QMenu()
        identifyMenu.addAction("Manually", self.locateControlAreaManually_clicked)
        identifyMenu.addAction("Automatically", self.locateControlAreaAutomatically_clicked)
        self.ui.identifyAreasPushButton.setMenu(identifyMenu)

        self.ui.paintImagePushButton.clicked.connect(self.paintImage_clicked)
        self.ui.settingsPushButton.clicked.connect(self.settings_clicked)


    def loadImageFile_clicked(self):
        """ Load image from file """
        self.rustDaVinci.load_image_from_file()
        if self.rustDaVinci.image_path != None:
            self.action_clearImage.setEnabled(True)


    def loadImageURL_clicked(self):
        """ Load image from URL """
        self.rustDaVinci.load_image_from_url()
        if self.rustDaVinci.image_path != None:
            self.action_clearImage.setEnabled(True)


    def clearCurrentImage_clicked(self):
        """ Clear the current image """
        self.rustDaVinci.clear_image()
        self.action_clearImage.setEnabled(False)


    def locateControlAreaManually_clicked(self):
        """ Locate the control area coordinates manually """
        self.rustDaVinci.locate_control_area_manually()


    def locateControlAreaAutomatically_clicked(self):
        """ Locate the control area coordinates automatically """
        self.rustDaVinci.locate_control_area_automatically()


    def paintImage_clicked(self):
        """ Start the painting process """
        self.rustDaVinci.start_painting()


    def settings_clicked(self):
        """ Create an instance of a settings window """
        settings = Settings(self)
        settings.show()


    def show(self):
        """ Show the main window """
        super(MainWindow, self).show()


    def hide(self):
        """ Hide the main window """
        super(MainWindow, self).hide()


    def closeEvent(self, closeEvent):
        """ Close the main window """
        super(MainWindow, self).closeEvent(closeEvent)
        self.closeEventSignal.emit(closeEvent)
