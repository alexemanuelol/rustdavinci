#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QColorDialog, QListWidgetItem

from ui.settings.settingsui import Ui_SettingsUI
from lib.rustPaletteData import rust_palette
from lib.color_functions import hex_to_rgb, rgb_to_hex, closest_color
from ui.settings.default_settings import default_settings


class Settings(QtWidgets.QDialog):

    def __init__(self, parent):
        """ Settings init module """
        QtWidgets.QDialog.__init__(self, parent)
        
        # Setup UI
        self.ui = Ui_SettingsUI()
        self.ui.setupUi(self)
        
        # Setup parent object
        self.parent = parent

        # Setup Settings
        self.settings = QtCore.QSettings()
        self.isSettingsChanged = False

        self.qpalette = QPalette()

        # Uncomment line below if you want to clear the settings everytime you start an instance
        #self.settings.clear()

        # Load settings and connect UI modules
        self.loadSettings()
        self.connectAll()


    def connectAll(self):
        """ Connect all buttons/checkboxes/comboboxes/lineedits. """
        # Buttons
        self.ui.defaultPushButton.clicked.connect(self.default_clicked)
        self.ui.okPushButton.clicked.connect(self.ok_clicked)
        self.ui.cancelPushButton.clicked.connect(self.close)
        self.ui.applyPushButton.clicked.connect(self.apply_clicked)
        self.ui.clearCoordinatesPushButton.clicked.connect(self.clear_ctrl_coords_clicked)
        self.ui.colorPickerPushButton.clicked.connect(self.color_picker_clicked)
        self.ui.addSkipColorPushButton.clicked.connect(self.addSkipColor_clicked)
        self.ui.removeSkipColorPushButton.clicked.connect(self.removeSkipColor_clicked)

        # Checkboxes
        self.ui.setTopmostPaintingCheckBox.stateChanged.connect(self.enableApply)
        self.ui.skipDefaultColorCheckBox.stateChanged.connect(self.enableApply)
        self.ui.autoUpdateCanvasCheckBox.stateChanged.connect(self.enableApply)
        self.ui.autoUpdateCanvasWhenCompletedCheckBox.stateChanged.connect(self.enableApply)
        self.ui.useBrushOpacitiesCheckBox.stateChanged.connect(self.enableApply)
        self.ui.drawLinesCheckBox.stateChanged.connect(self.enableApply)
        self.ui.doubleClickCheckBox.stateChanged.connect(self.enableApply)
        self.ui.useHiddenColorsCheckBox.stateChanged.connect(self.enableApply)

        # Comboboxes
        self.ui.paintingQualityComboBox.currentIndexChanged.connect(self.enableApply)
        self.ui.paintingBrushTypeComboBox.currentIndexChanged.connect(self.enableApply)

        # Lineedits
        self.ui.controlAreaXLineEdit.textChanged.connect(self.enableApply)
        self.ui.controlAreaYLineEdit.textChanged.connect(self.enableApply)
        self.ui.controlAreaWidthLineEdit.textChanged.connect(self.enableApply)
        self.ui.controlAreaHeightLineEdit.textChanged.connect(self.enableApply)
        self.ui.pauseKeyLineEdit.textChanged.connect(self.enableApply)
        self.ui.skipColorKeyLineEdit.textChanged.connect(self.enableApply)
        self.ui.cancelKeyLineEdit.textChanged.connect(self.enableApply)
        self.ui.backgroundColorLineEdit.textChanged.connect(self.enableApply)
        self.ui.skipColorsLineEdit.textChanged.connect(self.enableApply)
        self.ui.mouseClickDelayLineEdit.textChanged.connect(self.enableApply)
        self.ui.lineDrawingDelayLineEdit.textChanged.connect(self.enableApply)
        self.ui.controlAreaDelayLineEdit.textChanged.connect(self.enableApply)
        self.ui.minimumLineWidthLineEdit.textChanged.connect(self.enableApply)


    def enableApply(self):
        """ When a settings is changed, enable the apply button. """
        self.isSettingsChanged = True
        self.ui.applyPushButton.setEnabled(True)

    def loadSettings(self):
        """ Load the saved settings or the default settings. """
        # Checkboxes
        self.setting_to_checkbox("window_topmost", self.ui.setTopmostPaintingCheckBox, default_settings["window_topmost"])
        self.setting_to_checkbox("skip_background_color", self.ui.skipDefaultColorCheckBox, default_settings["skip_background_color"])
        self.setting_to_checkbox("update_canvas", self.ui.autoUpdateCanvasCheckBox, default_settings["update_canvas"])
        self.setting_to_checkbox("update_canvas_completed", self.ui.autoUpdateCanvasWhenCompletedCheckBox, default_settings["update_canvas_completed"])
        self.setting_to_checkbox("brush_opacities", self.ui.useBrushOpacitiesCheckBox, default_settings["brush_opacities"])
        self.setting_to_checkbox("draw_lines", self.ui.drawLinesCheckBox, default_settings["draw_lines"])
        self.setting_to_checkbox("double_click", self.ui.doubleClickCheckBox, default_settings["double_click"])
        self.setting_to_checkbox("hidden_colors", self.ui.useHiddenColorsCheckBox, default_settings["hidden_colors"])

        # Comboboxes
        index = self.settings.value("quality", default_settings["quality"])
        self.ui.paintingQualityComboBox.setCurrentIndex(index)

        index = self.settings.value("brush", default_settings["brush"])
        self.ui.paintingBrushTypeComboBox.setCurrentIndex(index)

        # Lineedits
        ctrl_x = str(self.settings.value("ctrl_x", default_settings["ctrl_x"]))
        self.ui.controlAreaXLineEdit.setText(ctrl_x)
        ctrl_y = str(self.settings.value("ctrl_y", default_settings["ctrl_y"]))
        self.ui.controlAreaYLineEdit.setText(ctrl_y)
        ctrl_w = str(self.settings.value("ctrl_w", default_settings["ctrl_w"]))
        self.ui.controlAreaWidthLineEdit.setText(ctrl_w)
        ctrl_h = str(self.settings.value("ctrl_h", default_settings["ctrl_h"]))
        self.ui.controlAreaHeightLineEdit.setText(ctrl_h)
        pause_key = self.settings.value("pause_key", default_settings["pause_key"])
        self.ui.pauseKeyLineEdit.setText(pause_key)
        skip_key = self.settings.value("skip_key", default_settings["skip_key"])
        self.ui.skipColorKeyLineEdit.setText(skip_key)
        cancel_key = self.settings.value("abort_key", default_settings["abort_key"])
        self.ui.cancelKeyLineEdit.setText(cancel_key)

        default_background_color = self.settings.value("background_color", default_settings["background_color"])
        rgb = hex_to_rgb(default_background_color)
        if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186:
            self.qpalette.setColor(QPalette.Text, QColor(0, 0, 0))
        else:
            self.qpalette.setColor(QPalette.Text, QColor(255, 255, 255))
        self.qpalette.setColor(QPalette.Base, QColor(rgb[0], rgb[1], rgb[2]))
        self.ui.backgroundColorLineEdit.setPalette(self.qpalette)
        self.ui.backgroundColorLineEdit.setText(default_background_color)

        skip_colors = self.settings.value("skip_colors", default_settings["skip_colors"])
        self.ui.skipColorsLineEdit.setText(skip_colors)
        click_delay = str(self.settings.value("click_delay", default_settings["click_delay"]))
        self.ui.mouseClickDelayLineEdit.setText(click_delay)
        line_delay = str(self.settings.value("line_delay", default_settings["line_delay"]))
        self.ui.lineDrawingDelayLineEdit.setText(line_delay)
        ctrl_area_delay = str(self.settings.value("ctrl_area_delay", default_settings["ctrl_area_delay"]))
        self.ui.controlAreaDelayLineEdit.setText(ctrl_area_delay)
        minimum_line_width = str(self.settings.value("minimum_line_width", default_settings["minimum_line_width"]))
        self.ui.minimumLineWidthLineEdit.setText(minimum_line_width)

        # Skip color list
        skip_colors2 = self.settings.value("skip_colors2", [], "QStringList")
        if len(skip_colors2) != 0:
            for color in skip_colors2:
                rgb = hex_to_rgb(color)
                i = QListWidgetItem(color)
                i.setBackground(QColor(rgb[0], rgb[1], rgb[2]))
                if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186:
                    i.setForeground(QColor(0, 0, 0))
                else:
                    i.setForeground(QColor(255, 255, 255))
                self.ui.skipColorsListWidget.addItem(i)


    def setting_to_checkbox(self, name, checkBox, default):
        """ Settings integer values converted to checkbox """
        val = int(self.settings.value(name, default))
        if val: checkBox.setCheckState(QtCore.Qt.Checked)
        else: checkBox.setCheckState(QtCore.Qt.Unchecked)
        

    def saveSettings(self):
        """ Save settings. """
        # Checkboxes
        self.checkbox_to_setting("window_topmost", self.ui.setTopmostPaintingCheckBox.isChecked())
        self.checkbox_to_setting("skip_background_color", self.ui.skipDefaultColorCheckBox.isChecked())
        self.checkbox_to_setting("update_canvas", self.ui.autoUpdateCanvasCheckBox.isChecked())
        self.checkbox_to_setting("update_canvas_completed", self.ui.autoUpdateCanvasWhenCompletedCheckBox.isChecked())
        self.checkbox_to_setting("brush_opacities", self.ui.useBrushOpacitiesCheckBox.isChecked())
        self.checkbox_to_setting("draw_lines", self.ui.drawLinesCheckBox.isChecked())
        self.checkbox_to_setting("double_click", self.ui.doubleClickCheckBox.isChecked())
        self.checkbox_to_setting("hidden_colors", self.ui.useHiddenColorsCheckBox.isChecked())

        # Comboboxes
        self.settings.setValue("quality", self.ui.paintingQualityComboBox.currentIndex())
        self.settings.setValue("brush", self.ui.paintingBrushTypeComboBox.currentIndex())

        #  Lineedits
        self.settings.setValue("ctrl_x", self.ui.controlAreaXLineEdit.text())
        self.settings.setValue("ctrl_y", self.ui.controlAreaYLineEdit.text())
        self.settings.setValue("ctrl_w", self.ui.controlAreaWidthLineEdit.text())
        self.settings.setValue("ctrl_h", self.ui.controlAreaHeightLineEdit.text())
        self.settings.setValue("pause_key", self.ui.pauseKeyLineEdit.text())
        self.settings.setValue("skip_key", self.ui.skipColorKeyLineEdit.text())
        self.settings.setValue("abort_key", self.ui.cancelKeyLineEdit.text())
        self.settings.setValue("background_color", self.ui.backgroundColorLineEdit.text())
        self.settings.setValue("skip_colors", self.ui.skipColorsLineEdit.text())
        self.settings.setValue("click_delay", self.ui.mouseClickDelayLineEdit.text())
        self.settings.setValue("line_delay", self.ui.lineDrawingDelayLineEdit.text())
        self.settings.setValue("ctrl_area_delay", self.ui.controlAreaDelayLineEdit.text())
        self.settings.setValue("minimum_line_width", self.ui.minimumLineWidthLineEdit.text())

        # Skip color list
        if self.ui.skipColorsListWidget.count() != 0:
            temp_list = []
            for i in range(self.ui.skipColorsListWidget.count()):
                temp_list.append(self.ui.skipColorsListWidget.item(i).text())
            self.settings.setValue("skip_colors2", temp_list)
        else:
            self.settings.setValue("skip_colors2", [])


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
        self.ui.setTopmostPaintingCheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.skipDefaultColorCheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.autoUpdateCanvasCheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.autoUpdateCanvasWhenCompletedCheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.useBrushOpacitiesCheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.drawLinesCheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.doubleClickCheckBox.setCheckState(QtCore.Qt.Unchecked)
        self.ui.useHiddenColorsCheckBox.setCheckState(QtCore.Qt.Unchecked)

        # Comboboxes
        self.ui.paintingQualityComboBox.setCurrentIndex(default_settings["quality"])
        self.ui.paintingBrushTypeComboBox.setCurrentIndex(default_settings["brush"])

        # Lineedits
        self.ui.controlAreaXLineEdit.setText(str(default_settings["ctrl_x"]))
        self.ui.controlAreaYLineEdit.setText(str(default_settings["ctrl_y"]))
        self.ui.controlAreaWidthLineEdit.setText(str(default_settings["ctrl_w"]))
        self.ui.controlAreaHeightLineEdit.setText(str(default_settings["ctrl_h"]))
        self.ui.pauseKeyLineEdit.setText(default_settings["pause_key"])
        self.ui.skipColorKeyLineEdit.setText(default_settings["skip_key"])
        self.ui.cancelKeyLineEdit.setText(default_settings["abort_key"])

        rgb = hex_to_rgb(default_settings["background_color"])
        if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186:
            self.qpalette.setColor(QPalette.Text, QColor(0, 0, 0))
        else:
            self.qpalette.setColor(QPalette.Text, QColor(255, 255, 255))
        self.qpalette.setColor(QPalette.Base, QColor(rgb[0], rgb[1], rgb[2]))
        self.ui.backgroundColorLineEdit.setPalette(self.qpalette)
        self.ui.backgroundColorLineEdit.setText(default_settings["background_color"])

        self.ui.skipColorsLineEdit.setText(default_settings["skip_colors"])
        self.ui.mouseClickDelayLineEdit.setText(str(default_settings["click_delay"]))
        self.ui.lineDrawingDelayLineEdit.setText(str(default_settings["line_delay"]))
        self.ui.controlAreaDelayLineEdit.setText(str(default_settings["ctrl_area_delay"]))
        self.ui.minimumLineWidthLineEdit.setText(str(default_settings["minimum_line_width"]))

        # Set skip color list to default
        self.ui.skipColorsListWidget.clear()
        if default_settings["skip_colors2"] != []:
            for hex in default_settings["skip_colors2"]:
                rgb = hex_to_rgb(hex)
                i = QListWidgetItem(hex)
                i.setBackground(QColor(rgb[0], rgb[1], rgb[2]))
                if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186:
                    i.setForeground(QColor(0, 0, 0))
                else:
                    i.setForeground(QColor(255, 255, 255))
                self.ui.skipColorsListWidget.addItem(i)


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
        self.ui.applyPushButton.setEnabled(False)


    def clear_ctrl_coords_clicked(self):
        """ Clear the control area coordinates. """
        self.ui.controlAreaXLineEdit.setText(str(default_settings["ctrl_x"]))
        self.ui.controlAreaYLineEdit.setText(str(default_settings["ctrl_y"]))
        self.ui.controlAreaWidthLineEdit.setText(str(default_settings["ctrl_w"]))
        self.ui.controlAreaHeightLineEdit.setText(str(default_settings["ctrl_h"]))


    def color_picker_clicked(self):
        """"""
        rgb = hex_to_rgb(self.ui.backgroundColorLineEdit.text())
        colorDialog = QColorDialog()
        selected_color = colorDialog.getColor(QColor(rgb[0], rgb[1], rgb[2]), self.parent, "Select a color")
        if selected_color.isValid():
            color = closest_color(hex_to_rgb(selected_color.name()))
            if (color[0]*0.299 + color[1]*0.587 + color[2]*0.114) > 186:
                self.qpalette.setColor(QPalette.Text, QColor(0, 0, 0))
            else:
                self.qpalette.setColor(QPalette.Text, QColor(255, 255, 255))
            self.qpalette.setColor(QPalette.Base, QColor(color[0], color[1], color[2]))
            self.ui.backgroundColorLineEdit.setPalette(self.qpalette)
            hex = rgb_to_hex(color)
            self.ui.backgroundColorLineEdit.setText(hex)


    def addSkipColor_clicked(self):
        colorDialog = QColorDialog()
        selected_color = colorDialog.getColor(QColor(255, 255, 255), self.parent, "Select a color to skip")
        if selected_color.isValid():
            color = closest_color(hex_to_rgb(selected_color.name()))
            hex = rgb_to_hex(color)

            # Verify that the color does not already exist in the list
            for i in range(self.ui.skipColorsListWidget.count()):
                if self.ui.skipColorsListWidget.item(i).text() == hex:
                    return

            i = QListWidgetItem(hex)
            i.setBackground(QColor(color[0], color[1], color[2]))
            if (color[0]*0.299 + color[1]*0.587 + color[2]*0.114) > 186:
                i.setForeground(QColor(0, 0, 0))
            else:
                i.setForeground(QColor(255, 255, 255))
            self.ui.skipColorsListWidget.addItem(i)
            self.enableApply()


    def removeSkipColor_clicked(self):
        listItems = self.ui.skipColorsListWidget.selectedItems()
        if not listItems: return
        for item in listItems:
            self.ui.skipColorsListWidget.takeItem(self.ui.skipColorsListWidget.row(item))
            self.enableApply()