#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QListWidgetItem

from ui.dialogs.colors.colorsui import Ui_ColorsUI
from lib.rustPaletteData import rust_palette
from lib.color_functions import rgb_to_hex

class Colors(QDialog):

    def __init__(self, parent):
        """ init Colors module """
        QDialog.__init__(self, parent)

        self.ui = Ui_ColorsUI()
        self.ui.setupUi(self)
        self.setWindowTitle("Colors")

        self.parent = parent

        self.populate_list()


    def populate_list(self):
        """ Populates the colors list """
        for i, color in enumerate(rust_palette):
            hex = rgb_to_hex(color)
            i = QListWidgetItem(str(i) + "\t" + str(hex))
            i.setBackground(QColor(color[0], color[1], color[2]))
            if (color[0]*0.299 + color[1]*0.587 + color[2]*0.114) > 186:
                i.setForeground(QColor(0, 0, 0))
            else:
                i.setForeground(QColor(255, 255, 255))
            self.ui.colors_ListWidget.addItem(i)
