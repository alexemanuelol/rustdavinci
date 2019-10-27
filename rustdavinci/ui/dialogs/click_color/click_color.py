#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QListWidgetItem

from ui.settings.default_settings import default_settings
from ui.dialogs.click_color.click_colorui import Ui_Click_ColorUI
from lib.rustPaletteData import rust_palette
from lib.color_functions import rgb_to_hex

class Click_Color(QDialog):

    def __init__(self, parent):
        """ init Colors module """
        QDialog.__init__(self, parent)

        self.ui = Ui_Click_ColorUI()
        self.ui.setupUi(self)
        self.setWindowTitle("Click color")

        self.settings_window = parent
        self.main_window = self.settings_window.parent
        self.settings = QSettings()
        self.main_window.rustDaVinci.use_hidden_colors = bool(self.settings.value("hidden_colors", default_settings["hidden_colors"]))

        self.color_index = 0

        self.populate_list()
        self.connectAll()


    def connectAll(self):
        """ Connect the click button to the function """
        self.ui.click_color_PushButton.clicked.connect(self.click_color_clicked)


    def click_color_clicked(self):
        """ This will click the selected color in the in-game palette """
        brush_type = int(self.settings.value("brush_type", default_settings["brush_type"]))
        selected_color = self.ui.colors_ListWidget.currentItem().background().color()
        selected_color_rgb = (selected_color.red(), selected_color.green(), selected_color.blue())
        color = rust_palette.index(selected_color_rgb)
        self.main_window.rustDaVinci.choose_painting_controls(0, brush_type, color)


    def populate_list(self):
        """ Populates the colors list """
        use_hidden_colors = bool(self.settings.value("hidden_colors", default_settings["hidden_colors"]))
        use_brush_opacities = bool(self.settings.value("brush_opacities", default_settings["brush_opacities"]))

        if use_hidden_colors:
            if use_brush_opacities:
                for i, color in enumerate(rust_palette):
                    self.append_color(color)
            else:
                for i, color in enumerate(rust_palette):
                    if i == 64: break
                    self.append_color(color)
        else:
            if use_brush_opacities:
                for i, color in enumerate(rust_palette):
                    if (i >= 0 and i <= 19) or (i >= 64 and i <= 83) or (i >= 128 and i <= 147) or (i >= 192 and i <= 211):
                        self.append_color(color)
            else:
                for i, color in enumerate(rust_palette):
                    if i == 20: break
                    self.append_color(color)


    def append_color(self, color):
        """ Appends a color to the list """
        hex = rgb_to_hex(color)
        i = QListWidgetItem(str(self.color_index) + "\t" + str(hex))
        i.setBackground(QColor(color[0], color[1], color[2]))
        if (color[0]*0.299 + color[1]*0.587 + color[2]*0.114) > 186:
            i.setForeground(QColor(0, 0, 0))
        else:
            i.setForeground(QColor(255, 255, 255))
        self.ui.colors_ListWidget.addItem(i)
        self.color_index += 1
