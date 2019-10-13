#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMenu, QLabel, QFrame
from PIL import Image
from PIL.ImageQt import ImageQt

from ui.settings.settings import Settings
from lib.rustDaVinci import rustDaVinci

from ui.views.mainui import Ui_MainUI

import ui.resources.icons_rc

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

        self.is_expanded = False
        self.label = None


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

        self.ui.showImagePushButton.clicked.connect(self.showImage_clicked)


    def loadImageFile_clicked(self):
        """ Load image from file """
        self.rustDaVinci.load_image_from_file()
        if self.rustDaVinci.org_img != None:
            self.action_clearImage.setEnabled(True)
            self.ui.showImagePushButton.setEnabled(True)
        if self.is_expanded:
            self.label.hide()
            self.expand_window()


    def loadImageURL_clicked(self):
        """ Load image from URL """
        self.rustDaVinci.load_image_from_url()
        if self.rustDaVinci.org_img != None:
            self.action_clearImage.setEnabled(True)
            self.ui.showImagePushButton.setEnabled(True)
        if self.is_expanded:
            self.label.hide()
            self.expand_window()


    def clearCurrentImage_clicked(self):
        """ Clear the current image """
        self.rustDaVinci.clear_image()
        self.action_clearImage.setEnabled(False)
        self.ui.showImagePushButton.setEnabled(False)
        self.ui.paintImagePushButton.setEnabled(False)
        self.is_expanded = True
        self.showImage_clicked()


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


    def showImage_clicked(self):
        """ Expand the main window and create image object """
        if self.is_expanded:
            self.ui.showImagePushButton.setText("Show Image >>")
            self.is_expanded = False
            self.setMinimumSize(QtCore.QSize(240, 450))
            self.setMaximumSize(QtCore.QSize(240, 450))
            self.resize(240, 450)
            if self.label != None:
                self.label.hide()
                self.showOriginalPushButton.hide()
                self.showNormalPushButton.hide()
                self.showHighPushButton.hide()
        else:
            self.expand_window()


    def expand_window(self):
        """"""
        self.is_expanded = True

        self.ui.showImagePushButton.setText("<< Hide Image")

        self.setMinimumSize(QtCore.QSize(800, 450))
        self.setMaximumSize(QtCore.QSize(800, 450))
        self.resize(800, 450)

        self.label = QLabel(self)
        self.label.setGeometry(QtCore.QRect(240, 10, 550, 380))
        self.label.setFrameShape(QFrame.Panel)
        self.label.setLineWidth(1)
        self.label.show()

        if self.rustDaVinci.pixmap_on_display == 0:
            pixmap = self.rustDaVinci.org_img_pixmap
        elif self.rustDaVinci.pixmap_on_display == 1:
            pixmap = self.rustDaVinci.quantized_img_pixmap_normal
        elif self.rustDaVinci.pixmap_on_display == 2:
            pixmap = self.rustDaVinci.quantized_img_pixmap_high

        pixmap = pixmap.scaled(550, 380, QtCore.Qt.KeepAspectRatio)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setPixmap(pixmap)

        self.showOriginalPushButton = QtWidgets.QPushButton("Original", self)
        self.showOriginalPushButton.setGeometry(QtCore.QRect(240, 400, 180, 21))
        self.showOriginalPushButton.show()
        self.showOriginalPushButton.clicked.connect(self.showOriginalPixmap)

        self.showNormalPushButton = QtWidgets.QPushButton("Normal", self)
        self.showNormalPushButton.setGeometry(QtCore.QRect(425, 400, 180, 21))
        self.showNormalPushButton.show()
        self.showNormalPushButton.clicked.connect(self.showNormalPixmap)

        self.showHighPushButton = QtWidgets.QPushButton("High", self)
        self.showHighPushButton.setGeometry(QtCore.QRect(610, 400, 180, 21))
        self.showHighPushButton.show()
        self.showHighPushButton.clicked.connect(self.showHighPixmap)


    def showOriginalPixmap(self):
        """"""
        self.rustDaVinci.pixmap_on_display = 0
        self.label.hide()
        self.showOriginalPushButton.hide()
        self.showNormalPushButton.hide()
        self.showHighPushButton.hide()
        self.expand_window()


    def showNormalPixmap(self):
        """"""
        self.rustDaVinci.pixmap_on_display = 1
        self.label.hide()
        self.showOriginalPushButton.hide()
        self.showNormalPushButton.hide()
        self.showHighPushButton.hide()
        self.expand_window()


    def showHighPixmap(self):
        """"""
        self.rustDaVinci.pixmap_on_display = 2
        self.label.hide()
        self.showOriginalPushButton.hide()
        self.showNormalPushButton.hide()
        self.showHighPushButton.hide()
        self.expand_window()


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
