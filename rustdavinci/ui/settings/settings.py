#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QDialog, QColorDialog, QListWidgetItem

import sys

from ui.settings.default_settings import default_settings
from ui.settings.settingsui import Ui_SettingsUI
from lib.color_functions import hex_to_rgb, rgb_to_hex, closest_color
from lib.captureArea import show_area
from ui.dialogs.colors.colors import Colors


class Settings(QDialog):
    def __init__(self, parent):
        """ Settings init module """
        QDialog.__init__(self, parent)
        
        # Setup UI
        self.ui = Ui_SettingsUI()
        self.ui.setupUi(self)
        
        # Setup parent object
        self.parent = parent

        # Setup Settings
        self.settings = QSettings()
        self.isSettingsChanged = False
        self.isColorsOpened = False

        if int(self.settings.value("ctrl_w", default_settings["ctrl_w"])) == 0 or int(self.settings.value("ctrl_h", default_settings["ctrl_h"])) == 0:
            self.ui.show_ctrl_PushButton.setEnabled(False)
        else: self.ui.show_ctrl_PushButton.setEnabled(True)

        self.qpalette = QPalette()

        self.availableColors = Colors(self)

        # Uncomment line below if you want to clear the settings everytime you start an instance
        #self.settings.clear()

        # Load settings and connect UI modules
        self.loadSettings()
        self.connectAll()


    def connectAll(self):
        """ Connect all buttons/checkboxes/comboboxes/lineedits. """
        # Buttons
        self.ui.default_PushButton.clicked.connect(self.default_clicked)
        self.ui.ok_PushButton.clicked.connect(self.ok_clicked)
        self.ui.cancel_PushButton.clicked.connect(self.close)
        self.ui.apply_PushButton.clicked.connect(self.apply_clicked)
        self.ui.clear_coords_PushButton.clicked.connect(self.clear_coords_clicked)
        self.ui.show_ctrl_PushButton.clicked.connect(self.show_ctrl_clicked)
        self.ui.color_picker_PushButton.clicked.connect(self.color_picker_clicked)
        self.ui.add_skip_color_PushButton.clicked.connect(self.add_skip_color_clicked)
        self.ui.remove_skip_color_PushButton.clicked.connect(self.remove_skip_color_clicked)
        self.ui.available_colors_PushButton.clicked.connect(self.available_colors_clicked)

        # Checkboxes
        self.ui.topmost_CheckBox.stateChanged.connect(self.enableApply)
        self.ui.skip_background_CheckBox.stateChanged.connect(self.enableApply)
        self.ui.update_canvas_CheckBox.stateChanged.connect(self.enableApply)
        self.ui.update_canvas_end_CheckBox.stateChanged.connect(self.enableApply)
        self.ui.draw_lines_CheckBox.stateChanged.connect(self.enableApply)
        self.ui.double_click_CheckBox.stateChanged.connect(self.enableApply)
        self.ui.show_info_CheckBox.stateChanged.connect(self.enableApply)
        self.ui.show_preview_CheckBox.stateChanged.connect(self.enableApply)
        self.ui.hide_preview_CheckBox.stateChanged.connect(self.enableApply)
        self.ui.paint_background_CheckBox.stateChanged.connect(self.enableApply)
        self.ui.opacities_CheckBox.stateChanged.connect(self.enableApply)
        self.ui.hidden_colors_CheckBox.stateChanged.connect(self.enableApply)

        # Comboboxes
        self.ui.quality_ComboBox.currentIndexChanged.connect(self.enableApply)
        self.ui.brush_type_ComboBox.currentIndexChanged.connect(self.enableApply)

        # Lineedits
        self.ui.ctrl_x_LineEdit.textChanged.connect(self.enableApply)
        self.ui.ctrl_y_LineEdit.textChanged.connect(self.enableApply)
        self.ui.ctrl_w_LineEdit.textChanged.connect(self.enableApply)
        self.ui.ctrl_h_LineEdit.textChanged.connect(self.enableApply)
        self.ui.pause_key_LineEdit.textChanged.connect(self.enableApply)
        self.ui.skip_key_LineEdit.textChanged.connect(self.enableApply)
        self.ui.abort_key_LineEdit.textChanged.connect(self.enableApply)
        self.ui.background_LineEdit.textChanged.connect(self.enableApply)
        self.ui.click_delay_LineEdit.textChanged.connect(self.enableApply)
        self.ui.ctrl_delay_LineEdit.textChanged.connect(self.enableApply)
        self.ui.line_delay_LineEdit.textChanged.connect(self.enableApply)
        self.ui.min_line_width_LineEdit.textChanged.connect(self.enableApply)


    def enableApply(self):
        """ When a settings is changed, enable the apply button. """
        self.isSettingsChanged = True
        self.ui.apply_PushButton.setEnabled(True)


    def loadSettings(self):
        """ Load the saved settings or the default settings. """
        # Checkboxes
        self.setting_to_checkbox("window_topmost", self.ui.topmost_CheckBox, default_settings["window_topmost"])
        self.setting_to_checkbox("skip_background_color", self.ui.skip_background_CheckBox, default_settings["skip_background_color"])
        self.setting_to_checkbox("update_canvas", self.ui.update_canvas_CheckBox, default_settings["update_canvas"])
        self.setting_to_checkbox("update_canvas_end", self.ui.update_canvas_end_CheckBox, default_settings["update_canvas_end"])
        self.setting_to_checkbox("draw_lines", self.ui.draw_lines_CheckBox, default_settings["draw_lines"])
        self.setting_to_checkbox("double_click", self.ui.double_click_CheckBox, default_settings["double_click"])
        self.setting_to_checkbox("show_information", self.ui.show_info_CheckBox, default_settings["show_information"])
        self.setting_to_checkbox("show_preview_load", self.ui.show_preview_CheckBox, default_settings["show_preview_load"])
        self.setting_to_checkbox("hide_preview_paint", self.ui.hide_preview_CheckBox, default_settings["hide_preview_paint"])
        self.setting_to_checkbox("paint_background", self.ui.paint_background_CheckBox, default_settings["paint_background"])
        self.setting_to_checkbox("brush_opacities", self.ui.opacities_CheckBox, default_settings["brush_opacities"])
        self.setting_to_checkbox("hidden_colors", self.ui.hidden_colors_CheckBox, default_settings["hidden_colors"])

        # Comboboxes
        index = self.settings.value("quality", default_settings["quality"])
        self.ui.quality_ComboBox.setCurrentIndex(index)
        index = self.settings.value("brush_type", default_settings["brush_type"])
        self.ui.brush_type_ComboBox.setCurrentIndex(index)

        # Lineedits
        ctrl_x = str(self.settings.value("ctrl_x", default_settings["ctrl_x"]))
        self.ui.ctrl_x_LineEdit.setText(ctrl_x)
        ctrl_y = str(self.settings.value("ctrl_y", default_settings["ctrl_y"]))
        self.ui.ctrl_y_LineEdit.setText(ctrl_y)
        ctrl_w = str(self.settings.value("ctrl_w", default_settings["ctrl_w"]))
        self.ui.ctrl_w_LineEdit.setText(ctrl_w)
        ctrl_h = str(self.settings.value("ctrl_h", default_settings["ctrl_h"]))
        self.ui.ctrl_h_LineEdit.setText(ctrl_h)
        pause_key = self.settings.value("pause_key", default_settings["pause_key"])
        self.ui.pause_key_LineEdit.setText(pause_key)
        skip_key = self.settings.value("skip_key", default_settings["skip_key"])
        self.ui.skip_key_LineEdit.setText(skip_key)
        abort_key = self.settings.value("abort_key", default_settings["abort_key"])
        self.ui.abort_key_LineEdit.setText(abort_key)

        background_color = self.settings.value("background_color", default_settings["background_color"])
        rgb = hex_to_rgb(background_color)
        if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186:
            self.qpalette.setColor(QPalette.Text, QColor(0, 0, 0))
        else:
            self.qpalette.setColor(QPalette.Text, QColor(255, 255, 255))
        self.qpalette.setColor(QPalette.Base, QColor(rgb[0], rgb[1], rgb[2]))
        self.ui.background_LineEdit.setPalette(self.qpalette)
        self.ui.background_LineEdit.setText(background_color)

        click_delay = str(self.settings.value("click_delay", default_settings["click_delay"]))
        self.ui.click_delay_LineEdit.setText(click_delay)
        ctrl_area_delay = str(self.settings.value("ctrl_area_delay", default_settings["ctrl_area_delay"]))
        self.ui.ctrl_delay_LineEdit.setText(ctrl_area_delay)
        line_delay = str(self.settings.value("line_delay", default_settings["line_delay"]))
        self.ui.line_delay_LineEdit.setText(line_delay)
        minimum_line_width = str(self.settings.value("minimum_line_width", default_settings["minimum_line_width"]))
        self.ui.min_line_width_LineEdit.setText(minimum_line_width)

        # Listwidgets
        skip_colors = self.settings.value("skip_colors", default_settings["skip_colors"], "QStringList")
        if len(skip_colors) != 0:
            for color in skip_colors:
                rgb = hex_to_rgb(color)
                i = QListWidgetItem(color)
                i.setBackground(QColor(rgb[0], rgb[1], rgb[2]))
                if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186:
                    i.setForeground(QColor(0, 0, 0))
                else:
                    i.setForeground(QColor(255, 255, 255))
                self.ui.skip_colors_ListWidget.addItem(i)


    def setting_to_checkbox(self, name, checkBox, default):
        """ Settings integer values converted to checkbox """
        val = int(self.settings.value(name, default))
        if val: checkBox.setCheckState(Qt.Checked)
        else: checkBox.setCheckState(Qt.Unchecked)
        

    def saveSettings(self):
        """ Save settings. """
        # Checkboxes
        self.checkbox_to_setting("window_topmost", self.ui.topmost_CheckBox.isChecked())
        self.checkbox_to_setting("skip_background_color", self.ui.skip_background_CheckBox.isChecked())
        self.checkbox_to_setting("update_canvas", self.ui.update_canvas_CheckBox.isChecked())
        self.checkbox_to_setting("update_canvas_end", self.ui.update_canvas_end_CheckBox.isChecked())
        self.checkbox_to_setting("draw_lines", self.ui.draw_lines_CheckBox.isChecked())
        self.checkbox_to_setting("double_click", self.ui.double_click_CheckBox.isChecked())
        self.checkbox_to_setting("show_information", self.ui.show_info_CheckBox.isChecked())
        self.checkbox_to_setting("show_preview_load", self.ui.show_preview_CheckBox.isChecked())
        self.checkbox_to_setting("hide_preview_paint", self.ui.hide_preview_CheckBox.isChecked())
        self.checkbox_to_setting("paint_background", self.ui.paint_background_CheckBox.isChecked())
        self.checkbox_to_setting("brush_opacities", self.ui.opacities_CheckBox.isChecked())
        self.checkbox_to_setting("hidden_colors", self.ui.hidden_colors_CheckBox.isChecked())

        # Comboboxes
        self.settings.setValue("quality", self.ui.quality_ComboBox.currentIndex())
        self.settings.setValue("brush_type", self.ui.brush_type_ComboBox.currentIndex())

        #  Lineedits
        self.settings.setValue("ctrl_x", self.ui.ctrl_x_LineEdit.text())
        self.settings.setValue("ctrl_y", self.ui.ctrl_y_LineEdit.text())
        self.settings.setValue("ctrl_w", self.ui.ctrl_w_LineEdit.text())
        self.settings.setValue("ctrl_h", self.ui.ctrl_h_LineEdit.text())
        self.settings.setValue("pause_key", self.ui.pause_key_LineEdit.text())
        self.settings.setValue("skip_key", self.ui.skip_key_LineEdit.text())
        self.settings.setValue("abort_key", self.ui.abort_key_LineEdit.text())
        self.settings.setValue("background_color", self.ui.background_LineEdit.text())
        self.settings.setValue("click_delay", self.ui.click_delay_LineEdit.text())
        self.settings.setValue("ctrl_area_delay", self.ui.ctrl_delay_LineEdit.text())
        self.settings.setValue("line_delay", self.ui.line_delay_LineEdit.text())
        self.settings.setValue("minimum_line_width", self.ui.min_line_width_LineEdit.text())

        # Skip color list
        if self.ui.skip_colors_ListWidget.count() != 0:
            temp_list = []
            for i in range(self.ui.skip_colors_ListWidget.count()):
                temp_list.append(self.ui.skip_colors_ListWidget.item(i).text())
            self.settings.setValue("skip_colors", temp_list)
        else:
            self.settings.setValue("skip_colors", [])


        self.parent.rustDaVinci.update()

        if self.parent.rustDaVinci.org_img != None:
            self.parent.rustDaVinci.convert_transparency()
            self.parent.rustDaVinci.create_pixmaps()
        if self.parent.is_expanded:
            self.parent.label.hide()
            self.parent.expand_window()


    def checkbox_to_setting(self, name, val):
        """ Settings save checkbox to integer """
        if val: self.settings.setValue(name, 1)
        else: self.settings.setValue(name, 0)


    def default_clicked(self):
        """ Set everything to the default values. """
        # Checkboxes
        self.ui.topmost_CheckBox.setCheckState(Qt.Checked)
        self.ui.skip_background_CheckBox.setCheckState(Qt.Checked)
        self.ui.update_canvas_CheckBox.setCheckState(Qt.Checked)
        self.ui.update_canvas_end_CheckBox.setCheckState(Qt.Checked)
        self.ui.draw_lines_CheckBox.setCheckState(Qt.Checked)
        self.ui.double_click_CheckBox.setCheckState(Qt.Unchecked)
        self.ui.show_info_CheckBox.setCheckState(Qt.Checked)
        self.ui.show_preview_CheckBox.setCheckState(Qt.Unchecked)
        self.ui.hide_preview_CheckBox.setCheckState(Qt.Unchecked)
        self.ui.paint_background_CheckBox.setCheckState(Qt.Unchecked)
        self.ui.opacities_CheckBox.setCheckState(Qt.Checked)
        self.ui.hidden_colors_CheckBox.setCheckState(Qt.Unchecked)

        # Comboboxes
        self.ui.quality_ComboBox.setCurrentIndex(default_settings["quality"])
        self.ui.brush_type_ComboBox.setCurrentIndex(default_settings["brush_type"])

        # Lineedits
        self.ui.ctrl_x_LineEdit.setText(str(default_settings["ctrl_x"]))
        self.ui.ctrl_y_LineEdit.setText(str(default_settings["ctrl_y"]))
        self.ui.ctrl_w_LineEdit.setText(str(default_settings["ctrl_w"]))
        self.ui.ctrl_h_LineEdit.setText(str(default_settings["ctrl_h"]))
        self.ui.pause_key_LineEdit.setText(default_settings["pause_key"])
        self.ui.skip_key_LineEdit.setText(default_settings["skip_key"])
        self.ui.abort_key_LineEdit.setText(default_settings["abort_key"])

        rgb = hex_to_rgb(default_settings["background_color"])
        if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186:
            self.qpalette.setColor(QPalette.Text, QColor(0, 0, 0))
        else:
            self.qpalette.setColor(QPalette.Text, QColor(255, 255, 255))
        self.qpalette.setColor(QPalette.Base, QColor(rgb[0], rgb[1], rgb[2]))
        self.ui.background_LineEdit.setPalette(self.qpalette)
        self.ui.background_LineEdit.setText(default_settings["background_color"])

        self.ui.click_delay_LineEdit.setText(str(default_settings["click_delay"]))
        self.ui.ctrl_delay_LineEdit.setText(str(default_settings["ctrl_area_delay"]))
        self.ui.line_delay_LineEdit.setText(str(default_settings["line_delay"]))
        self.ui.min_line_width_LineEdit.setText(str(default_settings["minimum_line_width"]))

        # Set skip color list to default
        self.ui.skip_colors_ListWidget.clear()
        if default_settings["skip_colors"] != []:
            for hex in default_settings["skip_colors"]:
                rgb = hex_to_rgb(hex)
                i = QListWidgetItem(hex)
                i.setBackground(QColor(rgb[0], rgb[1], rgb[2]))
                if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186:
                    i.setForeground(QColor(0, 0, 0))
                else:
                    i.setForeground(QColor(255, 255, 255))
                self.ui.skip_colors_ListWidget.addItem(i)


    def ok_clicked(self):
        """ Save and quit settings. """
        if self.isSettingsChanged: self.saveSettings()
        self.close()


    def cancel_clicked(self):
        """ quit settings. """
        self.close()


    def apply_clicked(self):
        """ Apply the settings. """
        self.saveSettings()
        self.isSettingsChanged = False
        self.ui.apply_PushButton.setEnabled(False)


    def clear_coords_clicked(self):
        """ Clear the control area coordinates. """
        self.ui.ctrl_x_LineEdit.setText(str(default_settings["ctrl_x"]))
        self.ui.ctrl_y_LineEdit.setText(str(default_settings["ctrl_y"]))
        self.ui.ctrl_w_LineEdit.setText(str(default_settings["ctrl_w"]))
        self.ui.ctrl_h_LineEdit.setText(str(default_settings["ctrl_h"]))


    def show_ctrl_clicked(self):
        """ Show where control area is located """
        x = int(self.settings.value("ctrl_x", default_settings["ctrl_x"]))
        y = int(self.settings.value("ctrl_y", default_settings["ctrl_y"]))
        w = int(self.settings.value("ctrl_w", default_settings["ctrl_w"]))
        h = int(self.settings.value("ctrl_h", default_settings["ctrl_h"]))
        show_area(x, y, w, h)


    def color_picker_clicked(self):
        """ Open a QColorDialog window """
        rgb = hex_to_rgb(self.ui.background_LineEdit.text())
        colorDialog = QColorDialog()
        selected_color = colorDialog.getColor(QColor(rgb[0], rgb[1], rgb[2]), self, "Select the default background color")
        if selected_color.isValid():
            color = closest_color(hex_to_rgb(selected_color.name()))
            if (color[0]*0.299 + color[1]*0.587 + color[2]*0.114) > 186:
                self.qpalette.setColor(QPalette.Text, QColor(0, 0, 0))
            else:
                self.qpalette.setColor(QPalette.Text, QColor(255, 255, 255))
            self.qpalette.setColor(QPalette.Base, QColor(color[0], color[1], color[2]))
            self.ui.background_LineEdit.setPalette(self.qpalette)
            hex = rgb_to_hex(color)
            self.ui.background_LineEdit.setText(hex)


    def add_skip_color_clicked(self):
        """ Add a color to skip_colors """
        colorDialog = QColorDialog()
        selected_color = colorDialog.getColor(QColor(255, 255, 255), self, "Select a color that should be skipped in the painting process")
        if selected_color.isValid():
            color = closest_color(hex_to_rgb(selected_color.name()))
            hex = rgb_to_hex(color)

            # Verify that the color does not already exist in the list
            for i in range(self.ui.skip_colors_ListWidget.count()):
                if self.ui.skip_colors_ListWidget.item(i).text() == hex:
                    return

            i = QListWidgetItem(hex)
            i.setBackground(QColor(color[0], color[1], color[2]))
            if (color[0]*0.299 + color[1]*0.587 + color[2]*0.114) > 186:
                i.setForeground(QColor(0, 0, 0))
            else:
                i.setForeground(QColor(255, 255, 255))
            self.ui.skip_colors_ListWidget.addItem(i)
            self.enableApply()


    def remove_skip_color_clicked(self):
        """ Remove a color from skip_colors """
        listItems = self.ui.skip_colors_ListWidget.selectedItems()
        if not listItems: return
        for item in listItems:
            self.ui.skip_colors_ListWidget.takeItem(self.ui.skip_colors_ListWidget.row(item))
            self.enableApply()


    def available_colors_clicked(self):
        """ Opens a dialog with all available colors """
        if not self.availableColors.isVisible():
            self.availableColors.show()


    def closeEvent(self, event):
        """ CloseEvent """
        self.availableColors.hide()
