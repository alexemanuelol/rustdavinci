#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QLineEdit, QMessageBox
from PIL import Image
from pynput import keyboard

import pyautogui
import cv2
import numpy
import time
import datetime

from lib.captureArea import capture_area
from lib.rustPaletteData import palette_80

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

        self.is_org_img_ok = False
        self.is_quantized_img_ok = False
        self.is_ctrl_area_located = False

        self.ctrl_remove = 0
        self.ctrl_update = 0
        self.ctrl_size = []
        self.ctrl_brush = []
        self.ctrl_opacity = []
        self.ctrl_color = []

        self.original_img = None
        self.quantized_img = None
        self.pixel_arr = None

        self.img_colors = []
        self.tot_pixels = 0
        self.pixels = 0
        self.lines = 0

        self.est_time_lines = 0
        self.est_time_click = 0

        self.mouse_click_delay = 0
        self.lines_draw_delay = 0

        self.is_paused = False
        self.is_skip_color = False
        self.is_exit = False


    def update_status(self):
        """"""
        if self.settings.value("use_saved_control_area", "1") and not (self.settings.value("ctrl_w", "0") == 0 or self.settings.value("ctrl_h", "0") == 0):
            self.ctrl_x = int(self.settings.value("ctrl_x", "0"))
            self.ctrl_y = int(self.settings.value("ctrl_y", "0"))
            self.ctrl_w = int(self.settings.value("ctrl_w", "0"))
            self.ctrl_h = int(self.settings.value("ctrl_h", "0"))
            self.is_ctrl_area_located = True

        self.mouse_click_delay = int(self.settings.value("click_delay", "5"))
        self.lines_draw_delay = int(self.settings.value("line_delay", "25"))

        if self.is_org_img_ok and self.is_quantized_img_ok and self.is_ctrl_area_located:
            self.parent.ui.paintImagePushButton.setEnabled(True)
        else:
            self.parent.ui.paintImagePushButton.setEnabled(False)



    def load_image_from_file(self):
        """ Load image from a file """
        title = "Select the image to be painted"
        fileformats = "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        path = QFileDialog.getOpenFileName(self.parent, title, QtCore.QDir.homePath(), fileformats)[0]

        if path.endswith(('.png', '.jpg', 'jpeg', '.gif', '.bmp')):
            self.original_img = Image.open(path)
            self.check_image_compatibility(self.original_img)
            self.is_org_img_ok = True
        elif path == "":
            self.original_img = None
            self.is_org_img_ok = False
        else:
            self.original_img = None
            self.is_org_img_ok = False
            msg = QMessageBox(self.parent)
            msg.setIcon(QMessageBox.Information)
            msg.setText("Invalid image format...")
            msg.setInformativeText("Valid formats: .png, .jpg, .jpeg, .gif, .bmp")
            msg.exec_()

        self.update_status()


    def load_image_from_url(self):
        # TODO
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
                self.is_org_img_ok = True
            elif path == "":
                self.original_img = None
                self.is_org_img_ok = False
            else:
                self.original_img = None
                self.is_org_img_ok = False
                msg = QMessageBox(self.parent)
                msg.setIcon(QMessageBox.Information)
                msg.setText("Invalid image format...")
                msg.setInformativeText("Valid formats: .png, .jpg, .jpeg, .gif, .bmp")
                msg.exec_()

        self.update_status()


    def check_image_compatibility(self, image):
        """"""
        image.load()

        if image.mode == "RGBA":
            msg = QMessageBox(self.parent)
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Warning! This image was RGBA, converting to RGB...")
            msg.exec_()

            self.original_img = image.convert("RGB")
        elif image.mode != "RGB" and image.mode != "L":
            msg = QMessageBox(self.parent)
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Only RGB or L mode images can be quantized to a palette, please choose a different image...")
            msg.exec_()

            self.original_img = None
            self.is_org_img_ok = False
            return

        self.is_quantized_img_ok = True
            

    def clear_image(self):
        """ Clear the image path """
        self.original_img = None
        self.is_org_img_ok = False
        self.update_status()


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
        canvas_area = capture_area()
        self.parent.show()

        if canvas_area[2] == 0 or canvas_area[3] == 0:
            msg = QMessageBox(self.parent)
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Invalid coordinates and ratio, please try again...")
            msg.exec_()
            return False

        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Information)
        msg.setText("Coordinates:\n" + 
                    "X =\t\t" + str(canvas_area[0]) + "\n" +
                    "Y =\t\t" + str(canvas_area[1]) + "\n" +
                    "Width =\t" + str(canvas_area[2]) + "\n" +
                    "Height =\t" + str(canvas_area[3]))
        msg.exec_()

        self.canvas_x = canvas_area[0]
        self.canvas_y = canvas_area[1]
        self.canvas_w = canvas_area[2]
        self.canvas_h = canvas_area[3]

        self.update_status()


    def locate_control_area_manually(self):
        """"""
        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Information)
        msg.setText("Manually capture the area by drag & drop the top left" +
                    "corner of the painting controls area to the bottom right corner.")
        msg.exec_()
        self.parent.hide()
        ctrl_area = capture_area()
        self.parent.show()

        btn = QMessageBox.question(self.parent, None,
                "Coordinates:\n" + 
                "X =\t\t" + str(ctrl_area [0]) + "\n" +
                "Y =\t\t" + str(ctrl_area [1]) + "\n" +
                "Width =\t" + str(ctrl_area [2]) + "\n" +
                "Height =\t" + str(ctrl_area [3]) + "\n\n" +
                "Would you like to save the painting controls area coordinates?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if btn == QMessageBox.Yes:
            self.settings.setValue("use_saved_area_coordinates", 1)
            self.settings.setValue("ctrl_x", str(ctrl_area[0]))
            self.settings.setValue("ctrl_y", str(ctrl_area[1]))
            self.settings.setValue("ctrl_w", str(ctrl_area[2]))
            self.settings.setValue("ctrl_h", str(ctrl_area[3]))
        else:
            self.settings.setValue("use_saved_area_coordinates", 0)

        self.ctrl_x = ctrl_area[0]
        self.ctrl_y = ctrl_area[1]
        self.ctrl_w = ctrl_area[2]
        self.ctrl_h = ctrl_area[3]

        self.is_ctrl_area_located = True

        self.calc_ctrl_tools_pos()
        self.update_status()


    def locate_control_area_automatically(self):
        """"""
        use_saved_coords = bool(self.settings.value("use_saved_control_area", 1))

        self.parent.hide()
        ctrl_area = self.locate_control_area_opencv()
        self.parent.show()

        msg = QMessageBox(self.parent)
        if ctrl_area == False:
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Couldn't find the painting control area automatically... Please try to manually capture it instead...")
            msg.exec_()
        else:
            btn = QMessageBox.question(self.parent, None,
                    "Coordinates:\n" + 
                    "X =\t\t" + str(ctrl_area [0]) + "\n" +
                    "Y =\t\t" + str(ctrl_area [1]) + "\n" +
                    "Width =\t" + str(ctrl_area [2]) + "\n" +
                    "Height =\t" + str(ctrl_area [3]) + "\n\n" +
                    "Would you like to save the painting controls area coordinates?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if btn == QMessageBox.Yes:
                self.settings.setValue("use_saved_area_coordinates", 1)
                self.settings.setValue("ctrl_x", str(ctrl_area[0]))
                self.settings.setValue("ctrl_y", str(ctrl_area[1]))
                self.settings.setValue("ctrl_w", str(ctrl_area[2]))
                self.settings.setValue("ctrl_h", str(ctrl_area[3]))
            else:
                self.settings.setValue("use_saved_area_coordinates", 0)

            self.ctrl_x = ctrl_area[0]
            self.ctrl_y = ctrl_area[1]
            self.ctrl_w = ctrl_area[2]
            self.ctrl_h = ctrl_area[3]

            self.is_ctrl_area_located = True
            
            self.calc_ctrl_tools_pos()
            self.update_status()


    def locate_control_area_opencv(self):
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


    def calc_ctrl_tools_pos(self):
        """ This function calculates the positioning of the different controls in the painting control area.
        The brush size, type and opacity along with all the different colors.
        Updates:    self.ctrl_remove
                    self.ctrl_update
                    self.ctrl_size
                    self.ctrl_brush
                    self.ctrl_opacity
                    self.ctrl_color
        """
        # Calculate the distance between two items on a row of six items (Size)
        first_x_coord_of_six_v1 = self.ctrl_x + (self.ctrl_w/6.5454)
        second_x_coord_of_six_v1 = self.ctrl_x + (self.ctrl_w/3.4285)
        dist_btwn_x_coords_of_six_v1 = second_x_coord_of_six_v1 - first_x_coord_of_six_v1
    
        # Calculate the distance between two items on a row of six items (Opacity)
        first_x_coord_of_six_v2 = self.ctrl_x + (self.ctrl_w/7.5789)
        second_x_coord_of_six_v2 = self.ctrl_x + (self.ctrl_w/3.5555)
        dist_btwn_x_coords_of_six_v2 = second_x_coord_of_six_v2 - first_x_coord_of_six_v2
    
        # Calculate the distance between two items on a row of four items (Colors width)
        first_x_coord_of_four = self.ctrl_x + (self.ctrl_w/6)
        second_x_coord_of_four = self.ctrl_x + (self.ctrl_w/2.5714)
        dist_btwn_x_coords_of_four = second_x_coord_of_four - first_x_coord_of_four
    
        # Calculate the distance between two items on a column of eight items (Colors height)
        first_y_coord_of_eight = self.ctrl_y + (self.ctrl_h/2.3220)
        second_y_coord_of_eight = self.ctrl_y + (self.ctrl_h/1.9855)
        dist_btwn_y_coords_of_eight = second_y_coord_of_eight - first_y_coord_of_eight
    
        # Set the point location of the remove & update buttons
        self.ctrl_remove = ((self.ctrl_x + (self.ctrl_w/2.7692)), (self.ctrl_y + (self.ctrl_h/19.5714)))
        self.ctrl_update = ((self.ctrl_x + (self.ctrl_w/1.5652)), (self.ctrl_y + (self.ctrl_h/19.5714)))
    
    
        for size in range(6):
            self.ctrl_size.append((  first_x_coord_of_six_v1 + 
                                     (size * dist_btwn_x_coords_of_six_v1), 
                                     (self.ctrl_y + (self.ctrl_h/6.9661))))
    
        for brush in range(4):
            self.ctrl_brush.append(( first_x_coord_of_four + 
                                     (brush * dist_btwn_x_coords_of_four), 
                                     (self.ctrl_y + (self.ctrl_h/4.2371))))
    
        for opacity in range(6):
            self.ctrl_opacity.append((   first_x_coord_of_six_v2 + 
                                         (opacity * dist_btwn_x_coords_of_six_v2), 
                                         (self.ctrl_y + (self.ctrl_h/3.0332))))
    
        for row in range(8):
            for column in range(4):
                if (row == 0 or row == 4) and column == 3: continue
                if (row == 1 or row == 5) and (column == 2 or column == 3): continue
                if row == 2 and column == 0: continue
                if row == 3 and (column == 0 or column == 1): continue
                if row == 6 and column == 2: continue
                if row == 7 and (column == 1 or column == 2): continue
                self.ctrl_color.append(  (first_x_coord_of_four + (column * dist_btwn_x_coords_of_four),
                                         (first_y_coord_of_eight + (row * dist_btwn_y_coords_of_eight))))
    
        # TODO: Experiment with positioning of new (hidden) colors. Append individual colors to the control_color list


    def convert_img(self):
        """ Convert the image to fit the canvas and quantize the image.
        Updates:    quantized_img,
                    x_correction,
                    y_correction
        Returns:    False, if the image type is invalid.
        """
        org_img_w = self.original_img.size[0]
        org_img_h = self.original_img.size[1]
            
        wpercent = (self.canvas_w / float(org_img_w))
        hpercent = (self.canvas_h / float(org_img_h))
    
        hsize = int((float(org_img_h) * float(wpercent)))
        wsize = int((float(org_img_w) * float(hpercent)))
    
        x_correction = 0
        y_correction = 0
    
        if hsize <= self.canvas_h: 
            resized_img = self.original_img.resize((self.canvas_w, hsize), Image.ANTIALIAS)
            y_correction = int((self.canvas_h - hsize)/2)
        elif wsize <= self.canvas_w: 
            resized_img = self.original_img.resize((wsize, self.canvas_h), Image.ANTIALIAS)
            x_correction = int((self.canvas_w - wsize)/2)
        else: 
            resized_img = self.original_img.resize((self.canvas_w, self.canvas_h), Image.ANTIALIAS)
    
        self.quantized_img = self.quantize_to_palette(resized_img)
        #if self.quantized_img == False:
        #    self.quantized_img = None
        #    return False
            
        self.canvas_x += x_correction
        self.canvas_y += y_correction
        self.canvas_w = self.quantized_img.size[0]
        self.canvas_h = self.quantized_img.size[1]


    def quantize_to_palette(self, image):
        """ Convert an RGB, RGBA or L mode image to use a given P image's palette.
        Returns:    The quantized image
        """
        # Select the palette to be used
        palette = Image.new("P", (1, 1))
        palette.putpalette(palette_80)
        palette.load()

        image.load()
    
        quality = int(self.settings.value("painting_quality", 1))
        if quality == 0:
            im = image.im.convert("P", 0, palette.im)
        elif quality == 1:
            im = image.im.convert("P", 1, palette.im) # Dithering
    
        try: return image._new(im)
        except AttributeError: return image._makeself(im)


    def calc_statistics(self):
        """ Calculate what colors, how many pixels and lines for the painting
        Updates:    self.img_colors, 
                    self.tot_pixels,
                    self.pixels,
                    self.lines
        """
        self.img_colors = []
        self.tot_pixels = 0
        self.pixels = 0
        self.lines = 0

        pixel_arr = self.quantized_img.load()

        colors_to_skip = self.settings.value("skip_colors", "").replace(" ", "").split(",")
        minimum_line_width = int(self.settings.value("minimum_line_width", "10"))

        for color in self.quantized_img.getcolors():
            if color[1] not in colors_to_skip:
                self.tot_pixels += color[0]
                self.img_colors.append(color[1])
    
        for color in self.img_colors:
            #if color in colors_to_skip: continue
    
            is_first_point_of_row = True
            is_last_point_of_row = False
            is_prev_color = False
            is_line = False
            pixels_in_line = 0
    
            for y in range(self.canvas_h):
                is_first_point_of_row = True
                is_last_point_of_row = False
                is_prev_color = False
                is_line = False
                pixels_in_line = 0
    
                for x in range(self.canvas_w):
                    if x == (self.canvas_w - 1): is_last_point_of_row = True
    
                    if is_first_point_of_row:
                        is_first_point_of_row = False
                        if pixel_arr[x, y] == color:
                            is_prev_color = True
                            pixels_in_line = 1
                        continue
    
                    if pixel_arr[x, y] == color:
                        if is_prev_color:
                            if is_last_point_of_row:
                                if pixels_in_line >= minimum_line_width: self.lines += 1
                                else:
                                    self.pixels += (pixels_in_line + 1)
                            else: is_line = True; pixels_in_line += 1
                        else:
                            if is_last_point_of_row: self.pixels += 1
                            else:
                                is_prev_color = True
                                pixels_in_line = 1
                    else:
                        if is_prev_color:
                            if is_line:
                                is_line = False
    
                                if is_last_point_of_row:
                                    if pixels_in_line >= minimum_line_width: self.lines += 1
                                    else: 
                                        self.pixels += (pixels_in_line + 1)
                                    continue
    
                                if pixels_in_line >= minimum_line_width: self.lines += 1
                                else: self.pixels += (pixels_in_line + 1)
                                pixels_in_line = 0
                            else: self.pixels += 1
                            is_prev_color = False
                        else:
                            is_line = False
                            pixels_in_line = 0


    def calc_est_time(self):
        """ Calculate estimated time for the painting process.
        Updates:    Estimated time for clicking and lines
                    Estimated time for only clicking
        """
        one_line_time = int(self.settings.value("line_delay", "25")) * 5
        one_click_time = int(self.settings.value("click_delay", "5")) + 0.001
        change_color_time = len(self.img_colors) * (int(self.settings.value("ctrl_area_delay", "100")) + (2 * int(self.settings.value("click_delay", "5"))))
        other_time = 0.5 + (3 * int(self.settings.value("click_delay", "5")))
        self.est_time_lines = int((self.pixels * one_click_time) + (self.lines * one_line_time) + change_color_time + other_time)
        self.est_time_click = int((self.tot_pixels * one_click_time) + change_color_time + other_time)


    def draw_line(point_A, point_B):
        """ Draws a line between point_A and point_B. """
        pyautogui.PAUSE = self.line_draw_delay
        pyautogui.mouseDown(button="left", x=point_A[0], y=point_A[1])
        pyautogui.keyDown("shift")
        pyautogui.moveTo(point_B[0], point_B[1])
        pyautogui.keyUp("shift")
        pyautogui.mouseUp(button="left")
        pyautogui.PAUSE = self.mouse_click_delay


    def key_event(self,key):
        """ Key-press handler. """
        if key == keyboard.Key.f10:     # PAUSE
            self.is_paused = not self.is_paused
            if self.is_paused:
                print("PAUSED\t\tF10 = Continue, F11 = Skip color, ESC = Exit")
        elif key == keyboard.Key.f11:   # SKIP CURRENT COLOR
            print("Skipping current color...")
            self.is_paused = False
            self.is_skip_color = True
        elif key == keyboard.Key.esc:   # EXIT 
            self.is_paused = False
            self.is_exit = True


    def start_painting(self):
        """ Start the painting """
        self.locate_canvas_area()
        self.convert_img()
        self.calc_statistics()
        self.calc_est_time()


        question = "\nDimensions: \t\t\t\t" + str(self.canvas_w) + " x " + str(self.canvas_h) + "\nNumber of colors:\t\t\t" + str(len(self.img_colors)) + "Total Number of pixels to paint: \t" + str(self.tot_pixels) + "Number of pixels to paint:\t\t" + str(self.pixels) + "Number of lines:\t\t\t" + str(self.lines) + "Est. painting time (click only):\t" + str(time.strftime("%H:%M:%S", time.gmtime(self.est_time_click))) + "Est. painting time (with lines):\t" + str(time.strftime("%H:%M:%S", time.gmtime(self.est_time_lines))) + "\n Would you like to start the painting?"
        btn = QMessageBox.question(self.parent, None, question, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if btn == QMessageBox.Yes:
            print("STARTING THE PAINT!")
        else:
            print("EXITING THE PAINT!")
            return

        # Start keyboard listener
        listener = keyboard.Listener(on_press=self.key_event)
        listener.start()


        while True:
            if self.is_exit:
                break
        print("Done")
        return





