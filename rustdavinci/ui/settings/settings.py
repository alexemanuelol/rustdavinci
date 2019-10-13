#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from ui.settings.settingsui import Ui_SettingsUI


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

        # Checkboxes
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
        self._settings_int_to_checkbox("skip_default_background_color", self.ui.skipDefaultColorCheckBox, 1)
        self._settings_int_to_checkbox("auto_update_canvas", self.ui.autoUpdateCanvasCheckBox, 1)
        self._settings_int_to_checkbox("auto_update_canvas_completed", self.ui.autoUpdateCanvasWhenCompletedCheckBox, 1)
        self._settings_int_to_checkbox("use_brush_opacities", self.ui.useBrushOpacitiesCheckBox, 1)
        self._settings_int_to_checkbox("draw_lines", self.ui.drawLinesCheckBox, 1)
        self._settings_int_to_checkbox("double_click", self.ui.doubleClickCheckBox, 0)
        self._settings_int_to_checkbox("use_hidden_colors", self.ui.useHiddenColorsCheckBox, 0)

        # Comboboxes
        index = self.settings.value("painting_quality", 1)
        self.ui.paintingQualityComboBox.setCurrentIndex(index)

        index = self.settings.value("painting_brush", 1)
        self.ui.paintingBrushTypeComboBox.setCurrentIndex(index)

        # Lineedits
        ctrl_x = self.settings.value("ctrl_x", "0")
        self.ui.controlAreaXLineEdit.setText(ctrl_x)
        ctrl_y = self.settings.value("ctrl_y", "0")
        self.ui.controlAreaYLineEdit.setText(ctrl_y)
        ctrl_w = self.settings.value("ctrl_w", "0")
        self.ui.controlAreaWidthLineEdit.setText(ctrl_w)
        ctrl_h = self.settings.value("ctrl_h", "0")
        self.ui.controlAreaHeightLineEdit.setText(ctrl_h)
        pause_key = self.settings.value("pause_key", "F10")
        self.ui.pauseKeyLineEdit.setText(pause_key)
        skip_key = self.settings.value("skip_key", "F11")
        self.ui.skipColorKeyLineEdit.setText(skip_key)
        cancel_key = self.settings.value("cancel_key", "Escape")
        self.ui.cancelKeyLineEdit.setText(cancel_key)
        default_background_color = self.settings.value("default_background_color", "16")
        self.ui.backgroundColorLineEdit.setText(default_background_color)
        skip_colors = self.settings.value("skip_colors", "36, 56, 76")
        self.ui.skipColorsLineEdit.setText(skip_colors)
        click_delay = self.settings.value("click_delay", "5")
        self.ui.mouseClickDelayLineEdit.setText(click_delay)
        line_delay = self.settings.value("line_delay", "25")
        self.ui.lineDrawingDelayLineEdit.setText(line_delay)
        ctrl_area_delay = self.settings.value("ctrl_area_delay", "100")
        self.ui.controlAreaDelayLineEdit.setText(ctrl_area_delay)
        minimum_line_width = self.settings.value("minimum_line_width", "10")
        self.ui.minimumLineWidthLineEdit.setText(minimum_line_width)


    def _settings_int_to_checkbox(self, name, checkBox, default):
        """ Settings integer values converted to checkbox """
        val = int(self.settings.value(name, default))
        if val: checkBox.setCheckState(QtCore.Qt.Checked)
        else: checkBox.setCheckState(QtCore.Qt.Unchecked)
        

    def saveSettings(self):
        """ Save settings. """
        # Checkboxes
        self._settings_checkbox_to_int("skip_default_background_color", self.ui.skipDefaultColorCheckBox.isChecked())
        self._settings_checkbox_to_int("auto_update_canvas", self.ui.autoUpdateCanvasCheckBox.isChecked())
        self._settings_checkbox_to_int("auto_update_canvas_completed", self.ui.autoUpdateCanvasWhenCompletedCheckBox.isChecked())
        self._settings_checkbox_to_int("use_brush_opacities", self.ui.useBrushOpacitiesCheckBox.isChecked())
        self._settings_checkbox_to_int("draw_lines", self.ui.drawLinesCheckBox.isChecked())
        self._settings_checkbox_to_int("double_click", self.ui.doubleClickCheckBox.isChecked())
        self._settings_checkbox_to_int("use_hidden_colors", self.ui.useHiddenColorsCheckBox.isChecked())

        # Comboboxes
        self.settings.setValue("painting_quality", self.ui.paintingQualityComboBox.currentIndex())
        self.settings.setValue("painting_brush", self.ui.paintingBrushTypeComboBox.currentIndex())

        #  Lineedits
        self.settings.setValue("ctrl_x", self.ui.controlAreaXLineEdit.text())
        self.settings.setValue("ctrl_y", self.ui.controlAreaYLineEdit.text())
        self.settings.setValue("ctrl_w", self.ui.controlAreaWidthLineEdit.text())
        self.settings.setValue("ctrl_h", self.ui.controlAreaHeightLineEdit.text())
        self.settings.setValue("pause_key", self.ui.pauseKeyLineEdit.text())
        self.settings.setValue("skip_key", self.ui.skipColorKeyLineEdit.text())
        self.settings.setValue("cancel_key", self.ui.cancelKeyLineEdit.text())
        self.settings.setValue("default_background_color", self.ui.backgroundColorLineEdit.text())
        self.settings.setValue("skip_colors", self.ui.skipColorsLineEdit.text())
        self.settings.setValue("click_delay", self.ui.mouseClickDelayLineEdit.text())
        self.settings.setValue("line_delay", self.ui.lineDrawingDelayLineEdit.text())
        self.settings.setValue("ctrl_area_delay", self.ui.controlAreaDelayLineEdit.text())
        self.settings.setValue("minimum_line_width", self.ui.minimumLineWidthLineEdit.text())

        self.parent.rustDaVinci.update()


    def _settings_checkbox_to_int(self, name, val):
        """ Settings save checkbox to integer """
        if val: self.settings.setValue(name, 1)
        else: self.settings.setValue(name, 0)


    def default_clicked(self):
        """ Set everything to the default values. """
        # Checkboxes
        self.ui.skipDefaultColorCheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.autoUpdateCanvasCheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.autoUpdateCanvasWhenCompletedCheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.useBrushOpacitiesCheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.drawLinesCheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.doubleClickCheckBox.setCheckState(QtCore.Qt.Unchecked)
        self.ui.useHiddenColorsCheckBox.setCheckState(QtCore.Qt.Unchecked)

        # Comboboxes
        self.ui.paintingQualityComboBox.setCurrentIndex(1)
        self.ui.paintingBrushTypeComboBox.setCurrentIndex(1)

        # Lineedits
        self.ui.controlAreaXLineEdit.setText("0")
        self.ui.controlAreaYLineEdit.setText("0")
        self.ui.controlAreaWidthLineEdit.setText("0")
        self.ui.controlAreaHeightLineEdit.setText("0")
        self.ui.pauseKeyLineEdit.setText("F10")
        self.ui.skipColorKeyLineEdit.setText("F11")
        self.ui.cancelKeyLineEdit.setText("Escape")
        self.ui.backgroundColorLineEdit.setText("16")
        self.ui.skipColorsLineEdit.setText("36, 56, 76")
        self.ui.mouseClickDelayLineEdit.setText("5")
        self.ui.lineDrawingDelayLineEdit.setText("25")
        self.ui.controlAreaDelayLineEdit.setText("100")
        self.ui.minimumLineWidthLineEdit.setText("10")


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
        self.ui.controlAreaXLineEdit.setText("0")
        self.ui.controlAreaYLineEdit.setText("0")
        self.ui.controlAreaWidthLineEdit.setText("0")
        self.ui.controlAreaHeightLineEdit.setText("0")
