#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pynput import keyboard
from io import BytesIO
from PIL import Image

import urllib.request
import pyautogui
import datetime
import numpy
import time
import cv2
import os

from lib.rustPaletteData import rust_palette
from lib.captureArea import capture_area


class rustDaVinci():

    def __init__(self, parent):
        """ RustDaVinci class init """
        self.parent = parent
        self.settings = QSettings()
        
        # PIL.Image images original/ quantized
        self.org_img = None
        self.quantized_img = None

        # Start painting booleans
        self.org_img_ok = False

        # Use double clicks
        self.use_double_click = False

        # Keyboard interrupt variables
        self.is_paused = False
        self.is_skip_color = False
        self.is_exit = False

        # Pixmaps
        self.pixmap_on_display = 0
        self.org_img_pixmap = None
        self.quantized_img_pixmap_normal = None
        self.quantized_img_pixmap_high = None

        # Painting control tools
        self.ctrl_remove = 0
        self.ctrl_update = 0
        self.ctrl_size = []
        self.ctrl_brush = []
        self.ctrl_opacity = []
        self.ctrl_color = []

        # Canvas coordinates/ ratio
        self.canvas_x = 0
        self.canvas_y = 0
        self.canvas_w = 0
        self.canvas_h = 0

        # Statistics
        self.img_colors = []
        self.tot_pixels = 0
        self.pixels = 0
        self.lines = 0
        self.estimated_time = 0

        # Delays
        self.click_delay = 0
        self.line_delay = 0
        self.ctrl_area_delay = 0

        # Hotkey display QLabel
        self.hotkey_label = None


    def update(self):
        """ Updates pyauogui delays, booleans and paint image button"""
        self.click_delay = float(int(self.settings.value("click_delay", "5"))/1000)
        self.line_delay = float(int(self.settings.value("line_delay", "25"))/1000)
        self.ctrl_area_delay = float(int(self.settings.value("ctrl_area_delay", "100"))/1000) 
        self.use_double_click = bool(self.settings.value("double_click", "0"))
        
        # Update the pyautogui delay
        pyautogui.PAUSE = self.click_delay

        if int(self.settings.value("ctrl_w", "0")) == 0 or int(self.settings.value("ctrl_h", "0")) == 0:
            self.parent.ui.paintImagePushButton.setEnabled(False)
        elif self.org_img_ok and int(self.settings.value("ctrl_w", "0")) != 0 and int(self.settings.value("ctrl_h", "0")) != 0:
            self.parent.ui.paintImagePushButton.setEnabled(True)


    def load_image_from_file(self):
        """ Load image from a file """
        title = "Select the image to be painted"
        fileformats = "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        path = QFileDialog.getOpenFileName(self.parent, title, None, fileformats)[0]

        if path.endswith(('.png', '.jpg', 'jpeg', '.gif', '.bmp')):
            # The original PIL.Image object
            self.org_img = Image.open(path)

            # Pixmap for original image
            self.org_img_pixmap = QPixmap(path)

            self.create_pixmaps()

        self.update()


    def load_image_from_url(self):
        """ Load image from url """
        dialog = QInputDialog(self.parent)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setLabelText("Load image from URL:")
        dialog.resize(500,100)
        ok_clicked = dialog.exec_()
        url = dialog.textValue()

        if ok_clicked and url != "":
            try:
                # The original PIL.Image object
                self.org_img = Image.open(urllib.request.urlopen(url))

                # Pixmap for original image
                urllib.request.urlretrieve(url, "temp_url_image.png")
                self.org_img_pixmap = QPixmap("temp_url_image.png", "1")
                os.remove("temp_url_image.png")

                self.create_pixmaps()
            except:
                self.org_img = None
                self.org_img_ok = False
                msg = QMessageBox(self.parent)
                msg.setIcon(QMessageBox.Critical)
                msg.setText("ERROR! Could not load the selected image...")
                msg.exec_()

        self.update()


    def create_pixmaps(self):
        """ Create quantized pixmaps """
        # Pixmap for quantized image of quality normal
        temp_normal = self.quantize_to_palette(self.org_img, True, 0)
        temp_normal.save("temp_normal.png")
        self.quantized_img_pixmap_normal = QPixmap("temp_normal.png")
        os.remove("temp_normal.png")

        # Pixmap for quantized image of quality high
        temp_high = self.quantize_to_palette(self.org_img, True, 1)
        temp_high.save("temp_high.png")
        self.quantized_img_pixmap_high = QPixmap("temp_high.png")
        os.remove("temp_high.png")

        self.pixmap_on_display = 0
        self.org_img_ok = True


    def convert_img(self):
        """ Convert the image to fit the canvas and quantize the image.
        Updates:    quantized_img,
                    x_correction,
                    y_correction
        Returns:    False, if the image type is invalid.
        """
        org_img_w = self.org_img.size[0]
        org_img_h = self.org_img.size[1]
            
        wpercent = (self.canvas_w / float(org_img_w))
        hpercent = (self.canvas_h / float(org_img_h))
    
        hsize = int((float(org_img_h) * float(wpercent)))
        wsize = int((float(org_img_w) * float(hpercent)))
    
        x_correction = 0
        y_correction = 0
    
        if hsize <= self.canvas_h: 
            resized_img = self.org_img.resize((self.canvas_w, hsize), Image.ANTIALIAS)
            y_correction = int((self.canvas_h - hsize)/2)
        elif wsize <= self.canvas_w: 
            resized_img = self.org_img.resize((wsize, self.canvas_h), Image.ANTIALIAS)
            x_correction = int((self.canvas_w - wsize)/2)
        else: 
            resized_img = self.org_img.resize((self.canvas_w, self.canvas_h), Image.ANTIALIAS)
    
        self.quantized_img = self.quantize_to_palette(resized_img)
        if self.quantized_img == False:
            self.org_img = None
            self.quantized_img = None
            self.org_img_ok = False
            return False

        self.canvas_x += x_correction
        self.canvas_y += y_correction
        self.canvas_w = self.quantized_img.size[0]
        self.canvas_h = self.quantized_img.size[1]
        return True


    def quantize_to_palette(self, image, pixmap = False, pixmap_q = 0):
        """ Convert an RGB, RGBA or L mode image to use a given P image's palette.
        Returns:    The quantized image
        """
        # Select the palette to be used
        palette_data = Image.new("P", (1, 1))


        palette = ()

        # Choose how many colors in the palette
        if bool(self.settings.value("use_hidden_colors", "0")):
            if bool(self.settings.value("use_brush_opacities", "1")):
                for data in rust_palette:
                    palette = palette + data
            else:
                for i, data in enumerate(rust_palette):
                    if i == 64:
                        palette = palette + (2, 2, 2) * 192
                        break
                    palette = palette + data
        else:
            if bool(self.settings.value("use_brush_opacities", "1")):
                for i, data in enumerate(rust_palette):
                    if (i >= 0 and i <= 19) or (i >= 64 and i <= 83) or (i >= 128 and i <= 147) or (i >= 192 and i <= 211):
                        palette = palette + data
                palette = palette + (2, 2, 2) * 176
            else:
                for i, data in enumerate(rust_palette):
                    if i == 20:
                        palette = palette + (2, 2, 2) * 236
                        break
                    palette = palette + data

        palette_data.putpalette(palette)

        palette_data.load()
        self.org_img = image
        self.org_img.load()

        if self.org_img.mode == "RGBA":
            self.org_img = image.convert("RGB")

        if not pixmap:
            quality = int(self.settings.value("painting_quality", 1))
            if quality == 0:
                im = image.im.convert("P", 0, palette_data.im)
            elif quality == 1:
                im = image.im.convert("P", 1, palette_data.im) # Dithering
        else:
            im = image.im.convert("P", pixmap_q, palette_data.im)
    
        try: return image._new(im)
        except AttributeError: return image._makeself(im)


    def clear_image(self):
        """ Clear the image """
        self.org_img = None
        self.quantized_img = None
        self.org_img_ok = False
        self.update()


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
            msg.setText("Invalid coordinates and ratio. Drag & drop the top left corner of the canvas to the bottom right corner.")
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
        return True


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
            "Would you like to update the painting controls area coordinates?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if btn == QMessageBox.Yes:
            self.settings.setValue("ctrl_x", str(ctrl_area[0]))
            self.settings.setValue("ctrl_y", str(ctrl_area[1]))
            self.settings.setValue("ctrl_w", str(ctrl_area[2]))
            self.settings.setValue("ctrl_h", str(ctrl_area[3]))

        self.update()


    def locate_control_area_automatically(self):
        """"""
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
                "Would you like to update the painting controls area coordinates?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if btn == QMessageBox.Yes:
                self.settings.setValue("ctrl_x", str(ctrl_area[0]))
                self.settings.setValue("ctrl_y", str(ctrl_area[1]))
                self.settings.setValue("ctrl_w", str(ctrl_area[2]))
                self.settings.setValue("ctrl_h", str(ctrl_area[3]))
            
            self.update()


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
        ctrl_x = int(self.settings.value("ctrl_x", "0"))
        ctrl_y = int(self.settings.value("ctrl_y", "0"))
        ctrl_w = int(self.settings.value("ctrl_w", "0"))
        ctrl_h = int(self.settings.value("ctrl_h", "0"))

        # Calculate the distance between two items on a row of six items (Size)
        first_x_coord_of_six_v1 = ctrl_x + (ctrl_w/6.5454)
        second_x_coord_of_six_v1 = ctrl_x + (ctrl_w/3.4285)
        dist_btwn_x_coords_of_six_v1 = second_x_coord_of_six_v1 - first_x_coord_of_six_v1
    
        # Calculate the distance between two items on a row of six items (Opacity)
        first_x_coord_of_six_v2 = ctrl_x + (ctrl_w/7.5789)
        second_x_coord_of_six_v2 = ctrl_x + (ctrl_w/3.5555)
        dist_btwn_x_coords_of_six_v2 = second_x_coord_of_six_v2 - first_x_coord_of_six_v2
    
        # Calculate the distance between two items on a row of four items (Colors width)
        first_x_coord_of_four = ctrl_x + (ctrl_w/6)
        second_x_coord_of_four = ctrl_x + (ctrl_w/2.5714)
        dist_btwn_x_coords_of_four = second_x_coord_of_four - first_x_coord_of_four
    
        # Calculate the distance between two items on a column of eight items (Colors height)
        first_y_coord_of_eight = ctrl_y + (ctrl_h/2.3220)
        second_y_coord_of_eight = ctrl_y + (ctrl_h/1.9855)
        dist_btwn_y_coords_of_eight = second_y_coord_of_eight - first_y_coord_of_eight
    
        # Set the point location of the remove & update buttons
        self.ctrl_remove = ((ctrl_x + (ctrl_w/2.7692)), (ctrl_y + (ctrl_h/19.5714)))
        self.ctrl_update = ((ctrl_x + (ctrl_w/1.5652)), (ctrl_y + (ctrl_h/19.5714)))
    
    
        for size in range(6):
            self.ctrl_size.append((  first_x_coord_of_six_v1 + 
                                     (size * dist_btwn_x_coords_of_six_v1), 
                                     (ctrl_y + (ctrl_h/6.9661))))
    
        for brush in range(4):
            self.ctrl_brush.append(( first_x_coord_of_four + 
                                     (brush * dist_btwn_x_coords_of_four), 
                                     (ctrl_y + (ctrl_h/4.2371))))
    
        for opacity in range(6):
            self.ctrl_opacity.append((   first_x_coord_of_six_v2 + 
                                         (opacity * dist_btwn_x_coords_of_six_v2), 
                                         (ctrl_y + (ctrl_h/3.0332))))
    
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
        
        # Hidden colors location
        if bool(self.settings.value("use_hidden_colors", "0")):
            self.ctrl_color.append((ctrl_x + (ctrl_w/18.0000), ctrl_y + (ctrl_h/2.1518)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/4.2353), ctrl_y + (ctrl_h/2.1406)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/13.0909), ctrl_y + (ctrl_h/1.8430)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/3.6923), ctrl_y + (ctrl_h/1.9116)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.8228), ctrl_y + (ctrl_h/1.8853)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.3714), ctrl_y + (ctrl_h/1.8348)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.0746), ctrl_y + (ctrl_h/1.9116)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.0667), ctrl_y + (ctrl_h/1.8430)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.8947), ctrl_y + (ctrl_h/1.6440)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.3333), ctrl_y + (ctrl_h/1.6181)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.2857), ctrl_y + (ctrl_h/1.6440)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.0827), ctrl_y + (ctrl_h/1.6506)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.0588), ctrl_y + (ctrl_h/1.6310)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.0588), ctrl_y + (ctrl_h/1.6118)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.8462), ctrl_y + (ctrl_h/1.4472)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.4545), ctrl_y + (ctrl_h/1.4784)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.3846), ctrl_y + (ctrl_h/1.4838)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.3333), ctrl_y + (ctrl_h/1.4784)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.1803), ctrl_y + (ctrl_h/1.4523)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.1077), ctrl_y + (ctrl_h/1.4421)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.0746), ctrl_y + (ctrl_h/1.4731)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/18.0000), ctrl_y + (ctrl_h/1.4679)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/3.7895), ctrl_y + (ctrl_h/1.4371)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/16.0000), ctrl_y + (ctrl_h/1.3258)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/3.8919), ctrl_y + (ctrl_h/1.3258)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/3.4286), ctrl_y + (ctrl_h/1.3301)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/16.0000), ctrl_y + (ctrl_h/1.2088)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/3.6923), ctrl_y + (ctrl_h/1.2342)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/4.0000), ctrl_y + (ctrl_h/1.2018)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/3.2000), ctrl_y + (ctrl_h/1.1983)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.9200), ctrl_y + (ctrl_h/1.2342)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.4845), ctrl_y + (ctrl_h/1.1844)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.3714), ctrl_y + (ctrl_h/1.1844)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.0746), ctrl_y + (ctrl_h/1.2053)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/16.0000), ctrl_y + (ctrl_h/1.1048)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/4.2353), ctrl_y + (ctrl_h/1.1078)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.3333), ctrl_y + (ctrl_h/1.1078)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.0667), ctrl_y + (ctrl_h/1.1048)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/3.3488), ctrl_y + (ctrl_h/1.0327)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/3.4286), ctrl_y + (ctrl_h/1.0512)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.4694), ctrl_y + (ctrl_h/1.0327)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/2.7692), ctrl_y + (ctrl_h/1.1982)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/2.0571), ctrl_y + (ctrl_h/1.2160)))
            self.ctrl_color.append((ctrl_x + (ctrl_w/1.3211), ctrl_y + (ctrl_h/1.4784)))


    def calc_statistics(self):
        """ Calculate what colors, how many pixels and lines for the painting
        Updates:    self.img_colors, 
                    self.tot_pixels,
                    self.pixels,
                    self.lines
        """
        minimum_line_width = int(self.settings.value("minimum_line_width", "10"))
        colors_to_skip = self.settings.value("skip_colors", "").replace(" ", "").split(",")
        if bool(self.settings.value("skip_default_background_color", "1")):
            colors_to_skip.append(self.settings.value("default_background_color", "16"))
        colors_to_skip = list(map(int, colors_to_skip))

        self.img_colors = []
        self.tot_pixels = 0
        self.pixels = 0
        self.lines = 0

        pixel_arr = self.quantized_img.load()


        for color in self.quantized_img.getcolors():
            if color[1] not in colors_to_skip:
                self.tot_pixels += color[0]
                self.img_colors.append(color[1])

        for color in self.img_colors:
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
        one_click_time = self.click_delay + 0.001
        one_click_time = one_click_time*2 if self.use_double_click else one_click_time
        one_line_time = self.line_delay * 5
        change_color_time = len(self.img_colors) * (self.ctrl_area_delay + (2 * self.click_delay))
        other_time = 0.5 + (3 * self.click_delay)
        est_time_lines = int((self.pixels * one_click_time) + (self.lines * one_line_time) + change_color_time + other_time)
        est_time_click = int((self.tot_pixels * one_click_time) + change_color_time + other_time)

        draw_lines = bool(self.settings.value("draw_lines", "1"))

        if not draw_lines:
            self.prefer_lines = False
            self.estimated_time = est_time_click
        elif est_time_lines < est_time_click:
            self.prefer_lines = True
            self.estimated_time = est_time_lines
        else:
            self.prefer_lines = False
            self.estimated_time = est_time_click

    
    def click_pixel(self, x = 0, y = 0):
        """"""
        if isinstance(x, tuple):
            pyautogui.click(x[0], x[1])
            if self.use_double_click:
                pyautogui.click(x[0], x[1])
        else:
            pyautogui.click(x, y)
            if self.use_double_click:
                pyautogui.click(x, y)


    def draw_line(self, point_A, point_B):
        """ Draws a line between point_A and point_B. """
        pyautogui.PAUSE = self.line_delay
        pyautogui.mouseDown(button="left", x=point_A[0], y=point_A[1])
        pyautogui.keyDown("shift")
        pyautogui.moveTo(point_B[0], point_B[1])
        pyautogui.keyUp("shift")
        pyautogui.mouseUp(button="left")
        pyautogui.PAUSE = self.click_delay


    def key_event(self, key):
        """ Key-press handler. """
        if key == keyboard.Key.f10:     # PAUSE
            self.is_paused = not self.is_paused
        elif key == keyboard.Key.f11:   # SKIP CURRENT COLOR
            self.is_paused = False
            self.is_skip_color = True
        elif key == keyboard.Key.esc:   # EXIT 
            self.is_paused = False
            self.is_exit = True


    def start_painting(self):
        """ Start the painting """
        # Load settings
        self.update()
        ctrl_x = int(self.settings.value("ctrl_x", "0"))
        ctrl_y = int(self.settings.value("ctrl_h", "0"))
        ctrl_w = int(self.settings.value("ctrl_w", "0"))
        ctrl_h = int(self.settings.value("ctrl_h", "0"))
        colors_to_skip = self.settings.value("skip_colors", "").replace(" ", "").split(",")
        if bool(self.settings.value("skip_default_background_color", "1")):
            colors_to_skip.append(self.settings.value("default_background_color", "16"))
        colors_to_skip = list(map(int, colors_to_skip))
        minimum_line_width = int(self.settings.value("minimum_line_width", "10"))
        auto_update_canvas = bool(self.settings.value("auto_update_canvas", 1))
        auto_update_canvas_completed = bool(self.settings.value("auto_update_canvas_completed", 1))

        use_hidden_colors = bool(self.settings.value("use_hidden_colors", "0"))
        use_brush_opacities = bool(self.settings.value("use_brush_opacities", "1"))

        # Boolean reset
        self.is_paused = False
        self.is_skip_color = False
        self.is_exit = False
        
        # Locate canvas, convert image, calculate tools positioning, statistics and estimated time
        if not self.locate_canvas_area(): return
        if not self.convert_img(): return

        self.parent.ui.logTextEdit.clear()
        self.parent.ui.logTextEdit.append("Calculating statistics...")
        QApplication.processEvents()

        self.calc_ctrl_tools_pos()
        self.calc_statistics()
        self.calc_est_time()

        question = "Dimensions: \t\t\t\t" + str(self.canvas_w) + " x " + str(self.canvas_h)
        question += "\nNumber of colors:\t\t\t" + str(len(self.img_colors))
        question += "\nTotal Number of pixels to paint: \t" + str(self.tot_pixels)
        question += "\nNumber of pixels to paint:\t\t" + str(self.pixels)
        question += "\nNumber of lines:\t\t\t" + str(self.lines)
        question += "\nEst. painting time:\t\t\t" + str(time.strftime("%H:%M:%S", time.gmtime(self.estimated_time)))
        question += "\n\nWould you like to start the painting?"
        btn = QMessageBox.question(self.parent, None, question, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if btn == QMessageBox.No:
            return


        self.parent.ui.logTextEdit.append("Est. time finished: " + str((datetime.datetime.now() + datetime.timedelta(seconds=self.estimated_time)).time().strftime("%H:%M:%S")))
        QApplication.processEvents()

        start_time = time.time()

        # Start keyboard listener
        listener = keyboard.Listener(on_press=self.key_event)
        listener.start()

        self.hotkey_label = QLabel(self.parent)
        self.hotkey_label.setGeometry(QRect(10, 425, 221, 21))
        self.hotkey_label.setText("F10 = Pause        F11 = Skip        ESC = Abort")
        self.hotkey_label.show()


        pixel_arr = self.quantized_img.load()

        self.click_pixel(self.ctrl_size[0]) # To set focus on the rust window
        time.sleep(.5)
        self.click_pixel(self.ctrl_size[0])
        self.click_pixel(self.ctrl_brush[self.settings.value("painting_brush", 1)])


        color_counter = 0
        for color in self.img_colors:
            self.is_skip_color = False
            self.parent.ui.logTextEdit.append("(" + str((color_counter+1)) + "/" + str((len(self.img_colors))) + ") Current color: " + str(color))
            QApplication.processEvents()
            color_counter += 1

            if color in colors_to_skip: continue

            first_point = (0, 0)
            is_first_point_of_row = True
            is_last_point_of_row = False
            is_prev_color = False
            is_line = False
            pixels_in_line = 0


            # Choose opacity
            time.sleep(self.ctrl_area_delay)
            if use_hidden_colors:
                if   color >= 0  and color < 64: self.click_pixel(self.ctrl_opacity[5])
                elif color >= 64 and color < 128: self.click_pixel(self.ctrl_opacity[4])
                elif color >= 128 and color < 192: self.click_pixel(self.ctrl_opacity[3])
                elif color >= 192 and color < 256: self.click_pixel(self.ctrl_opacity[2])
            else:
                if   color >= 0  and color < 20: self.click_pixel(self.ctrl_opacity[5])
                elif color >= 20 and color < 40: self.click_pixel(self.ctrl_opacity[4])
                elif color >= 40 and color < 60: self.click_pixel(self.ctrl_opacity[3])
                elif color >= 60 and color < 80: self.click_pixel(self.ctrl_opacity[2])
            time.sleep(self.ctrl_area_delay)

            # Choose color
            if use_hidden_colors:
                self.click_pixel(self.ctrl_color[color%64])
            else:
                self.click_pixel(self.ctrl_color[color%20])
            time.sleep(self.ctrl_area_delay)


            for y in range(self.canvas_h):
                if self.is_skip_color: break
                is_first_point_of_row = True
                is_last_point_of_row = False
                is_prev_color = False
                is_line = False
                pixels_in_line = 0

                for x in range(self.canvas_w):

                    while self.is_paused: None
                    if self.is_skip_color: break
                    if self.is_exit:
                        listener.stop()
                        elapsed_time = int(time.time() - start_time)
                        self.parent.ui.logTextEdit.append("Elapsed time: " + str(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))
                        self.parent.ui.logTextEdit.append("Aborted...")
                        QApplication.processEvents()
                        self.hotkey_label.hide()
                        return

                    if x == (self.canvas_w - 1):
                        is_last_point_of_row = True

                    if is_first_point_of_row and self.prefer_lines:
                        is_first_point_of_row = False
                        if pixel_arr[x, y] == color:
                            first_point = (self.canvas_x + x, self.canvas_y + y)
                            is_prev_color = True
                            pixels_in_line = 1
                        continue

                    if pixel_arr[x, y] == color:
                        if not self.prefer_lines: self.click_pixel(self.canvas_x + x, self.canvas_y + y); continue
                        if is_prev_color:
                            if is_last_point_of_row:
                                if pixels_in_line >= minimum_line_width:
                                    self.draw_line(first_point, (self.canvas_x + x, self.canvas_y + y))
                                else:
                                    for index in range(pixels_in_line):
                                        self.click_pixel(first_point[0] + index, self.canvas_y + y)
                                    self.click_pixel(self.canvas_x + x, self.canvas_y + y)
                            else:
                                is_line = True
                                pixels_in_line += 1
                        else:
                            if is_last_point_of_row:
                                self.click_pixel(self.canvas_x + x, self.canvas_y + y)
                            else:
                                first_point = (self.canvas_x + x, self.canvas_y + y)
                                is_prev_color = True
                                pixels_in_line = 1
                    else:
                        if not self.prefer_lines: continue
                        if is_prev_color:
                            if is_line:
                                is_line = False
                        
                                if is_last_point_of_row:
                                    if pixels_in_line >= minimum_line_width:
                                        self.draw_line(first_point, (self.canvas_x + (x-1), self.canvas_y + y))
                                    else:
                                        for index in range(pixels_in_line):
                                            self.click_pixel(first_point[0] + index, self.canvas_y + y)
                                    continue
    
                                if pixels_in_line >= minimum_line_width:
                                    self.draw_line(first_point, (self.canvas_x + (x-1), self.canvas_y + y))
                                else:
                                    for index in range(pixels_in_line):
                                        self.click_pixel(first_point[0] + index, self.canvas_y + y)
                                    self.click_pixel(self.canvas_x + x, self.canvas_y + y)
                                pixels_in_line = 0
    
                            else:
                                self.click_pixel(self.canvas_x + (x-1), self.canvas_y + y)
                            is_prev_color = False
                        else:
                            is_line = False
                            pixels_in_line = 0
    
            if auto_update_canvas:
                self.click_pixel(self.ctrl_update)
    
        if auto_update_canvas_completed:
            self.click_pixel(self.ctrl_update)
    
        listener.stop()

        elapsed_time = int(time.time() - start_time)

        self.parent.ui.logTextEdit.append("Elapsed time: " + str(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))
        QApplication.processEvents()
        self.hotkey_label.hide()
