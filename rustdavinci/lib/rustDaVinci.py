#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QLineEdit, QMessageBox
from PIL import Image

import pyautogui
import cv2
import numpy

from lib.captureArea import capture_area

class rustDaVinci():

    def __init__(self, parent):

        self.settings = QtCore.QSettings()
        self.parent = parent

        self.image_path = None

        self.canvas_x = 0
        self.canvas_y = 0
        self.canvas_w = 0
        self.canvas_h = 0

        self.ctrl_x = 0
        self.ctrl_y = 0
        self.ctrl_w = 0
        self.ctrl_h = 0

        self.canvas_located = False
        self.ctrl_located = False

        self.original_img = None
        self.quantized_img = None


    def load_image_from_file(self):
        """ Load image from a file """
        title = "Select the image to be painted"
        fileformats = "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        path = QFileDialog.getOpenFileName(self.parent, title, QtCore.QDir.homePath(), fileformats)[0]

        if path.endswith(('.png', '.jpg', 'jpeg', '.gif', '.bmp')): self.original_img = Image.open(path)
        elif path == "": self.original_img = None
        else:
            self.original_img = None
            msg = QMessageBox(self.parent)
            msg.setIcon(QMessageBox.Information)
            msg.setText("Invalid image format...")
            msg.setInformativeText("Valid formats: .png, .jpg, .jpeg, .gif, .bmp")
            msg.exec_()


    def load_image_from_url(self):
        """ Load image from url """
        dialog = QInputDialog(self.parent)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setLabelText("Load image from URL:")
        dialog.resize(500,100)
        ok_clicked = dialog.exec_()
        url = dialog.textValue()

        if ok_clicked and url != "":
            if url.endswith(('.png', '.jpg', 'jpeg', '.gif', '.bmp')):
                self.image_path = url
            elif path == "":
                None
            else:
                msg = QMessageBox(self.parent)
                msg.setIcon(QMessageBox.Information)
                msg.setText("Invalid image format...")
                msg.setInformativeText("Valid formats: .png, .jpg, .jpeg, .gif, .bmp")
                msg.exec_()


    def clear_image(self):
        """ Clear the image path """
        self.original_img = None


    def update_paint_button(self):
        """ If canvas and control area is located, enable the paint image button. """
        if self.ctrl_w > 0 and self.ctrl_h > 0: self.ctrl_located = True
        else: self.ctrl_located = False

        if self.canvas_w > 0 and self.canvas_h > 0: self.canvas_located = True
        else: self.canvas_located = False

        if self.canvas_located and self.ctrl_located:
            self.parent.ui.paintImagePushButton.setEnabled(True)
            self.parent.action_paintImage.setEnabled(True)
        else:
            self.parent.ui.paintImagePushButton.setEnabled(False)
            self.parent.action_paintImage.setEnabled(False)


    def locate_canvas_area(self):
        """ Locate the coordinates/ ratio of the canvas area.
        Updates:    self.canvas_x,
                    self.canvas_y,
                    self.canvas_w,
                    self.canvas_h
        """
        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Information)
        msg.setText("Manually capture the area by drag & drop the top left corner of the canvas to the bottom right corner.")
        msg.exec_()

        self.parent.hide()
        ctrl_area = capture_area()
        self.parent.show()

        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Information)
        msg.setText("Coordinates:\n" + 
                    "X =\t\t" + str(ctrl_area [0]) + "\n" +
                    "Y =\t\t" + str(ctrl_area [1]) + "\n" +
                    "Width =\t" + str(ctrl_area [2]) + "\n" +
                    "Height =\t" + str(ctrl_area [3]))
        msg.exec_()

        self.canvas_x = ctrl_area[0]
        self.canvas_y = ctrl_area[1]
        self.canvas_w = ctrl_area[2]
        self.canvas_h = ctrl_area[3]

        self.update_paint_button()
        

    def auto_locate_control_area(self):
        """ Automatically tries to find the painting control area with opencv.
        Returns:    ctrl_x,
                    ctrl_y,
                    ctrl_w,
                    ctrl_h
                    False, if no control area was found
        """
        screenshot = pyautogui.screenshot()
        screen_w, screen_h = screenshot.size

        image_gray = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_BGR2GRAY)

        tmpl = cv2.imread("opencv_template/rust_palette_template.png", 0)
        tmpl_w, tmpl_h = tmpl.shape[::-1]

        x_coord, y_coord = 0, 0
        threshold = 0.8

        for loop in range(50):
            matches = cv2.matchTemplate(image_gray, tmpl, cv2.TM_CCOEFF_NORMED)
            loc = numpy.where(matches >= threshold)

            x_list, y_list = [], []
            for point in zip(*loc[::-1]):
                x_list.append(point[0])
                y_list.append(point[1])

            if x_list:
                x_coord = int(sum(x_list) / len(x_list))
                y_coord = int(sum(y_list) / len(y_list))
                return x_coord, y_coord, tmpl_w, tmpl_h
    
            tmpl_w, tmpl_h = int(tmpl.shape[1]*1.035), int(tmpl.shape[0]*1.035)
            tmpl = cv2.resize(tmpl, (int(tmpl_w), int(tmpl_h)))

            if tmpl_w > screen_w or tmpl_h > screen_h or loop == 49: return False


    def locate_control_area(self):
        """ Locate the coordinates/ ratio of the painting control area.
        Updates:    self.ctrl_x,
                    self.ctrl_y,
                    self.ctrl_w,
                    self.ctrl_h
        """
        rmb_ctrl_coords = bool(self.settings.value("remember_control_area_coordinates", 0))
        auto_find_ctrl = bool(self.settings.value("auto_find_control_area", 0))

        if rmb_ctrl_coords:
            if not (self.settings.value("ctrl_w", "0") == "0" or self.settings.value("ctrl_h", "0") == "0"):
                self.ctrl_x = int(self.settings.value("ctrl_x", "0"))
                self.ctrl_y = int(self.settings.value("ctrl_y", "0"))
                self.ctrl_w = int(self.settings.value("ctrl_w", "0"))
                self.ctrl_h = int(self.settings.value("ctrl_h", "0"))
                return


        # Auto locate painting controls area
        if not auto_find_ctrl:
            question = "Would you like the application to automatically try to find the painting controls area coordinates?"
            msg = QMessageBox.question(self.parent, None, question, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if msg == QMessageBox.Yes:
                auto_find_ctrl = True
                self.settings.setValue("auto_find_control_area", 1)
        if auto_find_ctrl:
            self.parent.hide()
            ctrl_area = self.auto_locate_control_area()
            self.parent.show()


        # Manually locate painting controls area
        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Information)
        if auto_find_ctrl and ctrl_area == False:
            msg.setText("Couldn't locate the painting controls area...\n\n" +
                        "Manually capture the area by drag & drop the top left" +
                        "corner of the painting controls area to the bottom right corner.")
            msg.exec_()
            self.parent.hide()
            ctrl_area = capture_area()
            self.parent.show()
        elif not auto_find_ctrl:
            msg.setText("Manually capture the area by drag & drop the top left" +
                        "corner of the painting controls area to the bottom right corner.")
            msg.exec_()
            self.parent.hide()
            ctrl_area = capture_area()
            self.parent.show()


        #if rmb_ctrl_coords and int(self.settings.value("ctrl_w", "0")) > 0 and int(self.settings.value("ctrl_h", "0")) > 0:
        if ctrl_area[2] == 0 or ctrl_area[3] == 0:
            msg.setText("Invalid coordinates and ratio, please try again...")
            msg.exec_()
            return
        elif rmb_ctrl_coords:
            msg.setText("Coordinates:\n" + 
                        "X =\t\t" + str(ctrl_area [0]) + "\n" +
                        "Y =\t\t" + str(ctrl_area [1]) + "\n" +
                        "Width =\t" + str(ctrl_area [2]) + "\n" +
                        "Height =\t" + str(ctrl_area [3]))
            msg.exec_()
        else:
            msg = QMessageBox.question(self.parent, None, "Coordinates:\n" + 
                        "X =\t\t" + str(ctrl_area [0]) + "\n" +
                        "Y =\t\t" + str(ctrl_area [1]) + "\n" +
                        "Width =\t" + str(ctrl_area [2]) + "\n" +
                        "Height =\t" + str(ctrl_area [3]) + "\n\n" +
                        "Would you like to save the painting controls coordinates?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if msg == QMessageBox.Yes:
                rmb_ctrl_coords = True
                self.settings.setValue("remember_control_area_coordinates", 1)
            else:
                rmb_ctrl_coords = False
                self.settings.setValue("remember_control_area_coordinates", 0)

    
        if rmb_ctrl_coords:
            self.settings.setValue("ctrl_x", str(ctrl_area[0]))
            self.settings.setValue("ctrl_y", str(ctrl_area[1]))
            self.settings.setValue("ctrl_w", str(ctrl_area[2]))
            self.settings.setValue("ctrl_h", str(ctrl_area[3]))

        self.ctrl_x = ctrl_area[0]
        self.ctrl_y = ctrl_area[1]
        self.ctrl_w = ctrl_area[2]
        self.ctrl_h = ctrl_area[3]

        self.update_paint_button()








