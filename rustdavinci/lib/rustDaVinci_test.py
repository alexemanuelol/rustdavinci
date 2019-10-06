#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog

from lib.captureArea import capture_area
from lib.rustPaletteData import palette_80A

import pyautogui
import cv2
import numpy

from PIL import Image
from tkinter import filedialog

class rustDaVinci():

    def __init__(self):
        self.settings = QtCore.QSettings()


        self.skip_colors = []
    
        self.ctrl_x = 0
        self.ctrl_y = 0
        self.ctrl_w = 0
        self.ctrl_h = 0

        self.ctrl_remove = 0
        self.ctrl_update = 0
        self.ctrl_size = []
        self.ctrl_brush = []
        self.ctrl_opacity = []
        self.ctrl_color = []

        self.canvas_x = 0
        self.canvas_y = 0
        self.canvas_w = 0
        self.canvas_h = 0

        self.quantized_img = None
        self.pixel_arr = None

        self.img_colors = []
        self.tot_pixels = 0
        self.pixels = 0
        self.lines = 0

        self.est_time_lines = 0
        self.est_time_click = 0

        self.is_paused = False
        self.is_skip_color = False
        self.is_exit = False


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
        rmb_ctrl_coords = bool(self.settings.value("remember_control_area_coordinates", 1))
        auto_find_ctrl = bool(self.settings.value("auto_find_control_area", 1))

        if rmb_ctrl_coords:
            if self.settings.value("ctrl_w", "0") != "0":
                self.ctrl_x = int(self.settings.value("ctrl_x", "0"))
                self.ctrl_y = int(self.settings.value("ctrl_y", "0"))
                self.ctrl_w = int(self.settings.value("ctrl_w", "0"))
                self.ctrl_h = int(self.settings.value("ctrl_h", "0"))
                return
    
        if auto_find_ctrl:
            ctrl_area = self.auto_locate_control_area()
    
        if auto_find_ctrl and ctrl_area is not False: None
        else: ctrl_area = capture_area()
    
        if rmb_ctrl_coords:
            self.settings.setValue("ctrl_x", str(ctrl_area[0]))
            self.settings.setValue("ctrl_y", str(ctrl_area[1]))
            self.settings.setValue("ctrl_w", str(ctrl_area[2]))
            self.settings.setValue("ctrl_h", str(ctrl_area[3]))

        self.ctrl_x = ctrl_area[0]
        self.ctrl_y = ctrl_area[1]
        self.ctrl_w = ctrl_area[2]
        self.ctrl_h = ctrl_area[3]


    def locate_canvas_area(self):
        """ Locate the coordinates/ ratio of the canvas area.
        Updates:    self.canvas_x,
                    self.canvas_y,
                    self.canvas_w,
                    self.canvas_h
        """
        ctrl_area = capture_area()
        
        self.canvas_x = ctrl_area[0]
        self.canvas_y = ctrl_area[1]
        self.canvas_w = ctrl_area[2]
        self.canvas_h = ctrl_area[3]
    

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
    

    def convert_img(parent = None):
        """ Convert the image to fit the canvas and quantize the image.
        Updates:    quantized_img,
                    x_correction,
                    y_correction
        Returns:    False, if the image type is invalid.
        """
        img_path = QFileDialog.getOpenFileName(parent, "Select the image to be painted")[0]

        if img_path.endswith(('.png', '.jpg', 'jpeg', '.gif', '.bmp')):
            org_img = Image.open(img_path)
    
            org_img_w = org_img.size[0]
            org_img_h = org_img.size[1]
            
            wpercent = (self.canvas_w / float(org_img_w))
            hpercent = (self.canvas_h / float(org_img_h))
    
            hsize = int((float(org_img_h) * float(wpercent)))
            wsize = int((float(org_img_w) * float(hpercent)))
    
            x_correction = 0
            y_correction = 0
    
            if hsize <= self.canvas_h: 
                org_img = org_img.resize((self.canvas_w, hsize), Image.ANTIALIAS)
                y_correction = int((self.canvas_h - hsize)/2)
            elif wsize <= self.canvas_w: 
                org_img = org_img.resize((wsize, self.canvas_h), Image.ANTIALIAS)
                x_correction = int((self.canvas_w - wsize)/2)
            else: 
                org_img = org_img.resize((self.canvas_w, self.canvas_h), Image.ANTIALIAS)
    
            # Select the palette to be used
            palette_data = Image.new("P", (1, 1))
            palette_data.putpalette(rustPaletteData.palette_80)
    
            quantized_img = quantize_to_palette(org_img, palette_data)
            if quantized_img == False: return False
            
            self.pixel_arr = quantized_img.load()

            self.canvas_x += x_correction
            self.canvas_y += y_correction
            self.canvas_w = quantized_img.size[0]
            self.canvas_h = quantized_img.size[1]

        else:
            return False


    def calc_statistics(self):
        """ Calculate what colors, how many pixels and lines for the painting
        Updates:    self.img_colors, 
                    self.tot_pixels,
                    self.pixels,
                    self.lines
        """
        colors_to_skip = self.settings.value("skip_colors", "").replace(" ", "").split(",")

        for color in self.quantized_img.getcolors():
            if color[1] not in colors_to_skip:
                self.tot_pixels += color[0]
                self.img_colors.append(color[1])
    
        for color in img_colors:
            if color in colors_to_skip: continue
    
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
                        if self.pixel_arr[x, y] == color:
                            is_prev_color = True
                            pixels_in_line = 1
                        continue
    
                    if self.pixel_arr[x, y] == color:
                        if is_prev_color:
                            if is_last_point_of_row:
                                if pixels_in_line >= int(self.settings.value("minimum_line_width", "10")): self.lines += 1
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
                                    if pixels_in_line >= int(self.settings.valu("minimum_line_width", "10")): self.lines += 1
                                    else: 
                                        self.pixels += (pixels_in_line + 1)
                                    continue
    
                                if pixels_in_line >= int(self.settings.value("minimum_line_width", "10")): self.lines += 1
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
        change_color_time = self.colors * (int(self.settings.value("ctrl_area_delay", "100")) + (2 * int(self.settings.value("click_delay", "5"))))
        other_time = 0.5 + (3 * int(self.settings.value("click_delay", "5")))
        self.est_time_lines = int((self.pixels * one_click_time) + (self.lines * one_line_time) + change_color_time + other_time)
        self.est_time_click = int((self.tot_pixels * one_click_time) + change_color_time + other_time)


    def quantize_to_palette(org_img, palette):
        """ Convert an RGB, RGBA or L mode image to use a given P image's palette.
        Returns:    The quantized image
        """
        org_img.load()
        palette.load()
    
        if org_img.mode == "RGBA":
            print("\nWarning! This Image was RGBA, converting to RGB...\n")
            org_img = org_img.convert("RGB")
    
        if palette.mode != "P":
            raise ValueError("Bad mode for palette image")
    
        if org_img.mode != "RGB" and org_img.mode != "L":
            raise ValueError("Only RGB or L mode images can be quantized to a palette")
    
    
        quality = int(self.settings.value("painting_quality", 1))
        if quality == 0:
            im = org_img.im.convert("P", 0, palette.im)
        elif quality == 1:
            im = org_img.im.convert("P", 1, palette.im) # Dithering
    
        try: return org_img._new(im)
        except AttributeError: return org_img._makeself(im)


    def draw_line(point_A, point_B):
        """ Draws a line between point_A and point_B. """
        pyautogui.PAUSE = int(self.settings.value("line_delay", "25"))
        pyautogui.mouseDown(button="left", x=point_A[0], y=point_A[1])
        pyautogui.keyDown("shift")
        pyautogui.moveTo(point_B[0], point_B[1])
        pyautogui.keyUp("shift")
        pyautogui.mouseUp(button="left")
        pyautogui.PAUSE = int(self.settings.value("click_delay", "5"))


    def key_event(key):
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

    def paint(self):
        """ Start the painting """



