#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QRect, QSettings, QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMenu, QLabel, QFrame, QMainWindow, QMenu, QPushButton

from PIL import Image
from PIL.ImageQt import ImageQt

from ui.settings.settings import Settings
from ui.views.mainui import Ui_MainUI
from lib.rustDaVinci import rustDaVinci
import ui.resources.icons_rc

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        """ Main window init """
        super(MainWindow, self).__init__(parent)

        # Setup UI
        self.ui = Ui_MainUI()
        self.ui.setupUi(self)

        # Setup settings object
        self.settings = QSettings()

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
        loadMenu = QMenu()
        loadMenu.addAction("From File...", self.load_image_file_clicked)
        loadMenu.addAction("From URL...", self.load_image_URL_clicked)
        self.action_clearImage = loadMenu.addAction("Clear image", self.clear_image_clicked)
        self.action_clearImage.setEnabled(False)
        self.ui.load_image_PushButton.setMenu(loadMenu)

        # Add actions to the identifyAreasPushButton
        identifyMenu = QMenu()
        identifyMenu.addAction("Manually", self.locate_ctrl_manually_clicked)
        identifyMenu.addAction("Automatically", self.locate_ctrl_automatically_clicked)
        self.ui.identify_ctrl_PushButton.setMenu(identifyMenu)

        self.ui.paint_image_PushButton.clicked.connect(self.paint_image_clicked)
        self.ui.settings_PushButton.clicked.connect(self.settings_clicked)

        self.ui.preview_PushButton.clicked.connect(self.preview_clicked)


    def load_image_file_clicked(self):
        """ Load image from file """
        self.rustDaVinci.load_image_from_file()
        if self.rustDaVinci.org_img != None:
            self.action_clearImage.setEnabled(True)
            self.ui.preview_PushButton.setEnabled(True)
        if self.is_expanded:
            self.label.hide()
            self.expand_window()


    def load_image_URL_clicked(self):
        """ Load image from URL """
        self.rustDaVinci.load_image_from_url()
        if self.rustDaVinci.org_img != None:
            self.action_clearImage.setEnabled(True)
            self.ui.preview_PushButton.setEnabled(True)
        if self.is_expanded:
            self.label.hide()
            self.expand_window()


    def clear_image_clicked(self):
        """ Clear the current image """
        self.rustDaVinci.clear_image()
        self.action_clearImage.setEnabled(False)
        self.ui.preview_PushButton.setEnabled(False)
        self.ui.paint_image_PushButton.setEnabled(False)
        self.is_expanded = True
        self.preview_clicked()


    def locate_ctrl_manually_clicked(self):
        """ Locate the control area coordinates manually """
        self.rustDaVinci.locate_control_area_manually()


    def locate_ctrl_automatically_clicked(self):
        """ Locate the control area coordinates automatically """
        self.rustDaVinci.locate_control_area_automatically()


    def paint_image_clicked(self):
        """ Start the painting process """
        self.rustDaVinci.start_painting()


    def settings_clicked(self):
        """ Create an instance of a settings window """
        settings = Settings(self)
        settings.exec_()


    def preview_clicked(self):
        """ Expand the main window and create image object """
        if self.is_expanded:
            self.ui.preview_PushButton.setText("Show Image >>")
            self.is_expanded = False
            self.setMinimumSize(QSize(240, 450))
            self.setMaximumSize(QSize(240, 450))
            self.resize(240, 450)
            if self.label != None:
                self.label.hide()
                self.show_original_PushButton.hide()
                self.show_normal_PushButton.hide()
                self.show_high_PushButton.hide()
        else:
            self.expand_window()


    def expand_window(self):
        """ Expand the mainwindow to show preview images """
        self.is_expanded = True

        self.ui.preview_PushButton.setText("<< Hide Image")

        self.setMinimumSize(QSize(800, 450))
        self.setMaximumSize(QSize(800, 450))
        self.resize(800, 450)

        self.label = QLabel(self)
        self.label.setGeometry(QRect(240, 10, 550, 380))
        self.label.setFrameShape(QFrame.Panel)
        self.label.setLineWidth(1)
        self.label.show()

        if self.rustDaVinci.pixmap_on_display == 0:
            pixmap = self.rustDaVinci.org_img_pixmap
        elif self.rustDaVinci.pixmap_on_display == 1:
            pixmap = self.rustDaVinci.quantized_img_pixmap_normal
        elif self.rustDaVinci.pixmap_on_display == 2:
            pixmap = self.rustDaVinci.quantized_img_pixmap_high

        pixmap = pixmap.scaled(550, 380, Qt.KeepAspectRatio)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setPixmap(pixmap)

        self.show_original_PushButton = QPushButton("Original", self)
        self.show_original_PushButton.setGeometry(QRect(240, 400, 180, 21))
        self.show_original_PushButton.show()
        self.show_original_PushButton.clicked.connect(self.show_original_pixmap)

        self.show_normal_PushButton = QPushButton("Normal", self)
        self.show_normal_PushButton.setGeometry(QRect(425, 400, 180, 21))
        self.show_normal_PushButton.show()
        self.show_normal_PushButton.clicked.connect(self.show_normal_pixmap)

        self.show_high_PushButton = QPushButton("High", self)
        self.show_high_PushButton.setGeometry(QRect(610, 400, 180, 21))
        self.show_high_PushButton.show()
        self.show_high_PushButton.clicked.connect(self.show_high_pixmap)


    def show_original_pixmap(self):
        """ Show the original quality pixmap"""
        self.rustDaVinci.pixmap_on_display = 0
        self.label.hide()
        self.show_original_PushButton.hide()
        self.show_normal_PushButton.hide()
        self.show_high_PushButton.hide()
        self.expand_window()


    def show_normal_pixmap(self):
        """ Show the normal quality pixmap"""
        self.rustDaVinci.pixmap_on_display = 1
        self.label.hide()
        self.show_original_PushButton.hide()
        self.show_normal_PushButton.hide()
        self.show_high_PushButton.hide()
        self.expand_window()


    def show_high_pixmap(self):
        """ Show the high quality pixmap """
        self.rustDaVinci.pixmap_on_display = 2
        self.label.hide()
        self.show_original_PushButton.hide()
        self.show_normal_PushButton.hide()
        self.show_high_PushButton.hide()
        self.expand_window()


    def show(self):
        """ Show the main window """
        super(MainWindow, self).show()


    def hide(self):
        """ Hide the main window """
        super(MainWindow, self).hide()
