#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyautogui
import cv2
import numpy

from PyQt5 import QtCore


def auto_locate_control_area():
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

        if tmpl_w > screen_w or tmpl_h > screen_h or loop == 49:
            print("No control area was found...\n")
            return False



def locate_control_area():
    """ Locate the coordinates/ ratio of the painting control area.
    Returns:    ctrl_x,
                ctrl_y,
                ctrl_w,
                ctrl_h
    """
    global config

    rmb_ctrl_coords = config.getboolean("Painting", "remember_control_area_coordinates")
    auto_find_ctrl = config.getboolean("Painting", "auto_find_control_area")

    if rmb_ctrl_coords:
        if config("Painting", "ctrl_x") != "None":
            return  config.getint("Painting", "ctrl_x"), \
                    config.getint("Painting", "ctrl_y"), \
                    config.getint("Painting", "ctrl_w"), \
                    config.getint("Painting", "ctrl_h")

    if auto_find_ctrl:
        color_print("Locating control area automatically...\n", Fore.YELLOW)
        ctrl_area = auto_locate_control_area()

    if auto_find_ctrl and ctrl_area is not False:
        color_print("Control area found!\n", Fore.GREEN)
    else:
        input("1. Move the mouse pointer to the top left corner of the control area and click <ENTER>...")
        ctrl_TL = pyautogui.position()
        input("2. Move the mouse pointer to the bottom right corner of the control area and click <ENTER>...")
        ctrl_BR = pyautogui.position()
        ctrl_w = ctrl_BR[0] - ctrl_TL[0]
        ctrl_h = ctrl_BR[1] - ctrl_TL[1]
        ctrl_area = (ctrl_TL[0], ctrl_TL[1], ctrl_w, ctrl_h)

    if rmb_ctrl_coords:
        config["Painting"]["ctrl_x"] = str(ctrl_area[0])
        config["Painting"]["ctrl_y"] = str(ctrl_area[1])
        config["Painting"]["ctrl_w"] = str(ctrl_area[2])
        config["Painting"]["ctrl_h"] = str(ctrl_area[3])
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    return  ctrl_area[0], ctrl_area[1], ctrl_area[2], ctrl_area[3]
