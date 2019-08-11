#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter
import pyautogui
import time
import datetime
import win32gui
import win32con
import ctypes
import cv2
import configparser

import numpy as np

from tkinter import filedialog
from PIL import Image
from colorama import init, Fore, Back, Style
from termcolor import colored
from pynput import keyboard

import rustPaletteData


# Read the configuration file
config = configparser.ConfigParser(comment_prefixes="/", allow_no_value=True)
config.read("config.ini")

# CONSTANT the colors that should be skipped
COLORS_TO_SKIP = []
COLORS_TO_SKIP.append(config.getint("General", "default_background_color"))
config_skip_color = config["General"]["skip_colors"].replace(",", "").split()
for skip_color in config_skip_color:
    COLORS_TO_SKIP.append(int(skip_color))

# CONSTANT CLICK DELAY
click_delay_ms = config.getint("Experimental", "click_delay")
if click_delay_ms <= 0: CLICK_DELAY = 0
elif click_delay_ms > 0: CLICK_DELAY = float(click_delay_ms / 1000)

# CONSTANT LINE DELAY
line_delay_ms = config.getint("Experimental", "line_delay")
if line_delay_ms <= 0: LINE_DELAY = 0
elif line_delay_ms > 0: LINE_DELAY = float(line_delay_ms / 1000)

# CONSTANT CHANGE COLOR DELAY
ctrl_area_delay_ms = config.getint("Experimental", "ctrl_area_delay")
if ctrl_area_delay_ms <= 0: CTRL_AREA_DELAY = 0
elif ctrl_area_delay_ms > 0: CTRL_AREA_DELAY = float(ctrl_area_delay_ms / 1000)


MINIMUM_LINE_WIDTH = config.getint("Experimental", "minimum_line_width")

# Variables for keyboard event
is_paused = False
is_skip_color = False
is_exit = False





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

    image_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

    tmpl = cv2.imread("opencv_template/rust_palette_template.png", 0)
    tmpl_w, tmpl_h = tmpl.shape[::-1]

    x_coord, y_coord = 0, 0
    threshold = 0.8

    for loop in range(50):
        matches = cv2.matchTemplate(image_gray, tmpl, cv2.TM_CCOEFF_NORMED)
        loc = np.where(matches >= threshold)

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



def calc_ctrl_tools_pos(x, y, w, h):
    """ This function calculates the positioning of the different controls in the painting control area.
    The brush size, type and opacity along with all the different colors.
    Returns:    ctrl_remove
                ctrl_update
                ctrl_size
                ctrl_brush
                ctrl_opacity
                ctrl_color
    """
    # Calculate the distance between two items on a row of six items (Size)
    first_x_coord_of_six_v1 = x + (w/6.5454)
    second_x_coord_of_six_v1 = x + (w/3.4285)
    dist_btwn_x_coords_of_six_v1 = second_x_coord_of_six_v1 - first_x_coord_of_six_v1

    # Calculate the distance between two items on a row of six items (Opacity)
    first_x_coord_of_six_v2 = x + (w/7.5789)
    second_x_coord_of_six_v2 = x + (w/3.5555)
    dist_btwn_x_coords_of_six_v2 = second_x_coord_of_six_v2 - first_x_coord_of_six_v2

    # Calculate the distance between two items on a row of four items (Colors width)
    first_x_coord_of_four = x + (w/6)
    second_x_coord_of_four = x + (w/2.5714)
    dist_btwn_x_coords_of_four = second_x_coord_of_four - first_x_coord_of_four

    # Calculate the distance between two items on a column of eight items (Colors height)
    first_y_coord_of_eight = y + (h/2.3220)
    second_y_coord_of_eight = y + (h/1.9855)
    dist_btwn_y_coords_of_eight = second_y_coord_of_eight - first_y_coord_of_eight

    # Set the point location of the remove & update buttons
    ctrl_remove = ((x + (w/2.7692)), (y + (h/19.5714)))
    ctrl_update = ((x + (w/1.5652)), (y + (h/19.5714)))


    ctrl_size = []
    for size in range(6):
        ctrl_size.append((  first_x_coord_of_six_v1 + 
                            (size * dist_btwn_x_coords_of_six_v1), 
                            (y + (h/6.9661))))

    ctrl_brush = []
    for brush in range(4):
        ctrl_brush.append(( first_x_coord_of_four + 
                            (brush * dist_btwn_x_coords_of_four), 
                            (y + (h/4.2371))))

    ctrl_opacity = []
    for opacity in range(6):
        ctrl_opacity.append((   first_x_coord_of_six_v2 + 
                                (opacity * dist_btwn_x_coords_of_six_v2), 
                                (y + (h/3.0332))))

    ctrl_color = []
    for row in range(8):
        for column in range(4):
            if (row == 0 or row == 4) and column == 3: continue
            if (row == 1 or row == 5) and (column == 2 or column == 3): continue
            if row == 2 and column == 0: continue
            if row == 3 and (column == 0 or column == 1): continue
            if row == 6 and column == 2: continue
            if row == 7 and (column == 1 or column == 2): continue
            ctrl_color.append(  (first_x_coord_of_four + (column * dist_btwn_x_coords_of_four),
                                (first_y_coord_of_eight + (row * dist_btwn_y_coords_of_eight))))

    # TODO: Experiment with positioning of new (hidden) colors. Append individual colors to the control_color list


    return ctrl_remove, ctrl_update, ctrl_size, ctrl_brush, ctrl_opacity, ctrl_color



def convert_img(img_path, canvas_w, canvas_h):
    """ Convert the image to fit the canvas and dither the image.
    Returns:    dithered_img,
                x_correction,
                y_correction
                False, if the image type is invalid.
    """
    if img_path.endswith(('.png', '.jpg', 'jpeg', '.gif', '.bmp')):
        color_print("\nDithering process started...", Fore.YELLOW)
        org_img = Image.open(img_path)

        org_img_w = org_img.size[0]
        org_img_h = org_img.size[1]
        
        wpercent = (canvas_w / float(org_img_w))
        hpercent = (canvas_h / float(org_img_h))

        hsize = int((float(org_img_h) * float(wpercent)))
        wsize = int((float(org_img_w) * float(hpercent)))

        x_correction = 0
        y_correction = 0

        if hsize <= canvas_h: 
            org_img = org_img.resize((canvas_w, hsize), Image.ANTIALIAS)
            y_correction = int((canvas_h - hsize)/2)
        elif wsize <= canvas_w: 
            org_img = org_img.resize((wsize, canvas_h), Image.ANTIALIAS)
            x_correction = int((canvas_w - wsize)/2)
        else: 
            org_img = org_img.resize((canvas_w, canvas_h), Image.ANTIALIAS)

        # Select the palette to be used
        palette_data = Image.new("P", (1, 1))
        palette_data.putpalette(rustPaletteData.palette_80)

        dithered_img = quantize_to_palette(org_img, palette_data)
        if dithered_img == False: return False

        if config.getboolean("Painting", "save_preview"):
            dithered_img.save(config("Painting", "path_for_preview_image") + "Preview.png")
        if config.getboolean("Painting", "show_preview"):
            dithered_img.show(title="Preview")

        return dithered_img, x_correction, y_correction
    else:
        color_print("Invalid picture format...", Fore.RED)
        return False



def calc_statistics(dithered_img, img_w, img_h):
    """ Calculate what colors, how many pixels and lines for the painting
    Returns:    img_colors, 
                tot_pixels,
                pixels,
                lines
    """
    color_print("Counting colors...\nCounting pixels...", Fore.YELLOW)

    img_colors = []
    tot_pixels = 0
    pixels = 0
    lines = 0

    for color in dithered_img.getcolors():
        if color[1] not in COLORS_TO_SKIP:
            tot_pixels += color[0]
            img_colors.append(color[1])

    pixel_arr = dithered_img.load()


    color_print("Counting lines...", Fore.YELLOW)

    for color in img_colors:
        if color in COLORS_TO_SKIP: continue

        is_first_point_of_row = True
        is_last_point_of_row = False
        is_prev_color = False
        is_line = False
        pixels_in_line = 0

        for y in range(img_h):
            is_first_point_of_row = True
            is_last_point_of_row = False
            is_prev_color = False
            is_line = False
            pixels_in_line = 0

            for x in range(img_w):
                if x == (img_w - 1): is_last_point_of_row = True

                if is_first_point_of_row:
                    is_first_point_of_row = False
                    if pixel_arr[x, y] == color:
                        is_prev_color = True
                        pixels_in_line = 1
                    continue

                if pixel_arr[x, y] == color:
                    if is_prev_color:
                        if is_last_point_of_row:
                            if pixels_in_line >= MINIMUM_LINE_WIDTH: lines += 1
                            else:
                                pixels += (pixels_in_line + 1)
                        else: is_line = True; pixels_in_line += 1
                    else:
                        if is_last_point_of_row: pixels += 1
                        else:
                            is_prev_color = True
                            pixels_in_line = 1
                else:
                    if is_prev_color:
                        if is_line:
                            is_line = False

                            if is_last_point_of_row:
                                if pixels_in_line >= MINIMUM_LINE_WIDTH: lines += 1
                                else: 
                                    pixels += (pixels_in_line + 1)
                                continue

                            if pixels_in_line >= MINIMUM_LINE_WIDTH: lines += 1
                            else: pixels += (pixels_in_line + 1)
                            pixels_in_line = 0
                        else: pixels += 1
                        is_prev_color = False
                    else:
                        is_line = False
                        pixels_in_line = 0

    return  img_colors, \
            tot_pixels, \
            pixels, \
            lines



def calc_est_time(colors, tot_pixels, pixels, lines):
    """ Calculate estimated time for the painting process.
    Returns:    Estimated time for clicking and lines
                Estimated time for only clicking
    """
    one_line_time = LINE_DELAY * 5
    one_click_time = CLICK_DELAY + 0.001
    change_color_time = colors * (CTRL_AREA_DELAY + (2 * CLICK_DELAY))
    other_time = 0.5 + (3 * CLICK_DELAY)
    est_time_lines = int((pixels * one_click_time) + (lines * one_line_time) + change_color_time + other_time)
    est_time_click = int((tot_pixels * one_click_time) + change_color_time + other_time)

    return est_time_lines, est_time_click



def quantize_to_palette(org_img, palette):
    """ Convert an RGB, RGBA or L mode image to use a given P image's palette.
    Returns:    The quantized image
    """
    org_img.load()
    palette.load()

    if org_img.mode == "RGBA":
        color_print("\nWarning! This Image was RGBA, converting to RGB...\n", Fore.RED)
        org_img = org_img.convert("RGB")

    if palette.mode != "P":
        raise ValueError("Bad mode for palette image")

    if org_img.mode != "RGB" and org_img.mode != "L":
        raise ValueError("Only RGB or L mode images can be quantized to a palette")


    quality = config.getint("Painting", "painting_accuracy")
    if quality == 1:
        im = org_img.im.convert("P", 0, palette.im)
    elif quality == 2:
        im = org_img.im.convert("P", 1, palette.im) # Dithering
    else:
        color_print("The quality variable in config.ini is invalid!", Fore.RED)
        return False

    try: return org_img._new(im)
    except AttributeError: return org_img._makeself(im)



def draw_line(point_A, point_B):
    """ Draws a line between point_A and point_B. """
    pyautogui.PAUSE = LINE_DELAY
    pyautogui.mouseDown(button="left", x=point_A[0], y=point_A[1])
    pyautogui.keyDown("shift")
    pyautogui.moveTo(point_B[0], point_B[1])
    pyautogui.keyUp("shift")
    pyautogui.mouseUp(button="left")
    pyautogui.PAUSE = CLICK_DELAY



def key_event(key):
    """ Key-press handler. """
    global is_paused, is_skip_color, is_exit
    if key == keyboard.Key.f10:
        is_paused = not is_paused
        if is_paused:
            color_print("PAUSED\t\tF10 = Continue, F11 = Skip color, ESC = Exit", Fore.YELLOW)
    elif key == keyboard.Key.f11:
        color_print("Skipping current color...", Fore.YELLOW)
        is_paused = False
        is_skip_color = True
    elif key == keyboard.Key.esc:
        is_paused = False
        is_exit = True



def color_print(message, color):
    """ Print function with different colors.
    Colors:     BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
    """
    print(color + message + Fore.RESET)



def main():
    """ The main application
    """

    init()  # Initilize colorama module

    print("")
    color_print("██████╗ ██╗   ██╗███████╗████████╗    ██████╗  █████╗     ██╗   ██╗██╗███╗   ██╗ ██████╗██╗", Fore.RED)
    color_print("██╔══██╗██║   ██║██╔════╝╚══██╔══╝    ██╔══██╗██╔══██╗    ██║   ██║██║████╗  ██║██╔════╝██║", Fore.RED)
    color_print("██████╔╝██║   ██║███████╗   ██║       ██║  ██║███████║    ██║   ██║██║██╔██╗ ██║██║     ██║", Fore.RED)
    color_print("██╔══██╗██║   ██║╚════██║   ██║       ██║  ██║██╔══██║    ╚██╗ ██╔╝██║██║╚██╗██║██║     ██║", Fore.RED)
    color_print("██║  ██║╚██████╔╝███████║   ██║       ██████╔╝██║  ██║     ╚████╔╝ ██║██║ ╚████║╚██████╗██║", Fore.RED)
    color_print("╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝       ╚═════╝ ╚═╝  ╚═╝      ╚═══╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚═╝\n", Fore.RED)

    color_print("Hello & Welcome to RustDaVinci!\n", Fore.RED)
    
    color_print("Beneath follows the application instructions:\n", Fore.RED)
    color_print("\t1. Firstly the application needs to capture the rust palette control area.", Fore.RED)
    color_print("\t2. Then it needs to capture the canvas.", Fore.RED)
    color_print("\t3. Make sure that the application window is in focus when capturing the areas.", Fore.RED)
    color_print("\t4. Make sure that the application window does not cover those two areas.\n", Fore.RED)
    color_print("Follow the instructions below to begin the area capturing...\n", Fore.RED)


    ctypes.windll.kernel32.SetConsoleTitleW("RustDaVinci") # Set window title

    screen_x, screen_y = pyautogui.size()
    # Set the console window as an overlay and place it on the left of the painting area
    if config.getboolean("General", "window_on_top"):
        hwnd = win32gui.GetForegroundWindow()
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, (canvas_x - 25), screen_y, 0)


    pyautogui.PAUSE = CLICK_DELAY




    # Get the control area coordinates and ratio
    ctrl_x, ctrl_y, ctrl_w, ctrl_h = locate_control_area()

    # Calculate the control tools positions
    pos = calc_ctrl_tools_pos(ctrl_x, ctrl_y, ctrl_w, ctrl_h)

    ctrl_remove = pos[0]
    ctrl_update = pos[1]
    ctrl_size = pos[2]
    ctrl_brush = pos[3]
    ctrl_opacity = pos[4]
    ctrl_color = pos[5]

    # Debug purpose
    #print("control_area_x:      " + str(ctrl_x))
    #print("control_area_y:      " + str(ctrl_y))
    #print("control_area_width:  " + str(ctrl_w))
    #print("control_area_height: " + str(ctrl_h))
    #time.sleep(1)
    #pyautogui.moveTo(ctrl_x, ctrl_y)
    #time.sleep(3)
    #pyautogui.moveTo(ctrl_x + ctrl_w, ctrl_y + ctrl_h)
    #time.sleep(3)

    # Debug purpose
    #pyautogui.moveTo(ctrl_remove)
    #time.sleep(1)
    #pyautogui.moveTo(ctrl_update)
    #time.sleep(1)

    #for i in range(6):
    #    pyautogui.moveTo(ctrl_size[i])
    #    time.sleep(1)

    #for i in range(4):
    #    pyautogui.moveTo(ctrl_brush[i])
    #    time.sleep(1)

    #for i in range(6):
    #    pyautogui.moveTo(ctrl_opacity[i])
    #    time.sleep(1)

    #for i in range(20):
    #    pyautogui.moveTo(ctrl_color[i])
    #    time.sleep(1)



    # Get the canvas coordinates and ratio
    input("3. Move the mouse pointer to the top left corner of the canvas and click <ENTER>...")
    canvas_TL = pyautogui.position()
    input("4. Move the mouse pointer to the bottom right corner of the canvas and click <ENTER>...")
    canvas_BR = pyautogui.position()

    canvas_x, canvas_y = canvas_TL[0], canvas_TL[1]
    canvas_w = canvas_BR[0] - canvas_TL[0]
    canvas_h = canvas_BR[1] - canvas_TL[1]



    # Initilize the tkinter module
    root = tkinter.Tk()
    root.withdraw()



    # Select the image to be dithered and painted
    img_path = filedialog.askopenfilename(title="Select the image to be painted")

    dithered_img, x_correction, y_correction = convert_img(img_path, canvas_w, canvas_h)
    if dithered_img == False: exit()

    pixel_arr = dithered_img.load()

    canvas_x += x_correction
    canvas_y += y_correction
    canvas_w = dithered_img.size[0]
    canvas_h = dithered_img.size[1]

        


    # Counter statistics (Total amount of pixels, lines, colors etc...)
    statistics = calc_statistics(dithered_img, canvas_w, canvas_h)

    img_colors = statistics[0]
    tot_pixels = statistics[1]
    pixels = statistics[2]
    lines = statistics[3]




    # Calculate the estimated time of the paint
    est_time_line, est_time_click = calc_est_time(  len(img_colors),
                                                    tot_pixels,
                                                    pixels,
                                                    lines)


    prefer_lines = False
    if est_time_line < est_time_click:
        print("\nGoing for lines...")
        prefer_lines = True
        est_time = est_time_line
    else:
        print("\nGoing for clicks...")
        est_time = est_time_click




    # Print information about the paint
    color_print("\nDimensions: \t\t\t\t" + str(canvas_w) + " x " + str(canvas_h), Fore.GREEN)
    color_print("\nNumber of colors:\t\t\t" + str(len(img_colors)), Fore.GREEN)
    color_print("Total Number of pixels to paint: \t" + str(tot_pixels), Fore.GREEN)
    color_print("Number of pixels to paint:\t\t" + str(pixels), Fore.GREEN)
    color_print("Number of lines:\t\t\t" + str(lines), Fore.GREEN)
    color_print("Est. painting time (click only):\t" + str(time.strftime("%H:%M:%S", time.gmtime(est_time_click))), Fore.GREEN)
    color_print("Est. painting time (with lines):\t" + str(time.strftime("%H:%M:%S", time.gmtime(est_time_line))), Fore.GREEN)
    color_print("\nPress <ENTER> to start the painting process...\n", Fore.YELLOW); input()
    color_print("Est. time finished:\t\t" + str((datetime.datetime.now() + datetime.timedelta(seconds=est_time)).time().strftime("%H:%M:%S")) + "\n", Fore.GREEN)



    color_print("F10 = Continue, F11 = Skip color, ESC = Exit\n", Fore.GREEN)

    start_time = time.time()


    # Start listening for key-presses
    listener = keyboard.Listener(on_press=key_event)
    listener.start()



    pyautogui.click(ctrl_size[0]) # To set focus on the rust window
    time.sleep(.5)
    pyautogui.click(ctrl_size[0])
    pyautogui.click(ctrl_brush[config.getint("Painting", "default_brush")])



    color_counter = 0
    for color in img_colors:
        is_skip_color = False
        color_print("(" + str((color_counter+1)) + "/" + str((len(img_colors))) + ") Current color: " + str(color), Fore.MAGENTA)
        color_counter += 1

        if color in COLORS_TO_SKIP: continue

        time.sleep(0 if CTRL_AREA_DELAY == 0 else CTRL_AREA_DELAY / 3)
        if   color >= 0  and color < 20: pyautogui.click(ctrl_opacity[5])
        elif color >= 20 and color < 40: pyautogui.click(ctrl_opacity[4])
        elif color >= 40 and color < 60: pyautogui.click(ctrl_opacity[3])
        elif color >= 60 and color < 80: pyautogui.click(ctrl_opacity[2])
        time.sleep(0 if CTRL_AREA_DELAY == 0 else CTRL_AREA_DELAY / 3)


        first_point = (0, 0)
        is_first_point_of_row = True
        is_last_point_of_row = False
        is_prev_color = False
        is_line = False
        pixels_in_line = 0

        pyautogui.click(ctrl_color[color%20])
        time.sleep(0 if CTRL_AREA_DELAY == 0 else CTRL_AREA_DELAY / 3)

        for y in range(canvas_h):
            if is_skip_color: break
            is_first_point_of_row = True
            is_last_point_of_row = False
            is_prev_color = False
            is_line = False
            pixels_in_line = 0

            for x in range(canvas_w):

                while is_paused: None

                if is_skip_color: break

                if is_exit:
                    elapsed_time = int(time.time() - start_time)
                    color_print("\nElapsed time:\t\t\t" + str(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))), Fore.GREEN)
                    color_print("\nExiting...", Fore.RED)
                    exit()

                if x == (canvas_w - 1):
                    is_last_point_of_row = True

                if is_first_point_of_row and prefer_lines:
                    is_first_point_of_row = False
                    if pixel_arr[x, y] == color:
                        first_point = (canvas_x + x, canvas_y + y)
                        is_prev_color = True
                        pixels_in_line = 1
                    continue

                if pixel_arr[x, y] == color:
                    if not prefer_lines: pyautogui.click(canvas_x + x, canvas_y + y); continue
                    if is_prev_color:
                        if is_last_point_of_row:
                            if pixels_in_line >= MINIMUM_LINE_WIDTH:
                                draw_line(first_point, (canvas_x + x, canvas_y + y))
                            else:
                                for index in range(pixels_in_line):
                                    pyautogui.click(first_point[0] + index, canvas_y + y)
                                pyautogui.click(canvas_x + x, canvas_y + y)
                        else:
                            is_line = True
                            pixels_in_line += 1
                    else:
                        if is_last_point_of_row:
                            pyautogui.click(canvas_x + x, canvas_y + y)
                        else:
                            first_point = (canvas_x + x, canvas_y + y)
                            is_prev_color = True
                            pixels_in_line = 1
                else:
                    if not prefer_lines: continue
                    if is_prev_color:
                        if is_line:
                            is_line = False
                    
                            if is_last_point_of_row:
                                if pixels_in_line >= MINIMUM_LINE_WIDTH:
                                    draw_line(first_point, (canvas_x + (x-1), canvas_y + y))
                                else:
                                    for index in range(pixels_in_line):
                                        pyautogui.click(first_point[0] + index, canvas_y + y)
                                continue

                            if pixels_in_line >= MINIMUM_LINE_WIDTH:
                                #print(str((paint_area_x + (x-1)) - first_point[0]))
                                #print(str(first_point[0])+"\t"+str(paint_area_x + (x-1)))
                                draw_line(first_point, (canvas_x + (x-1), canvas_y + y))
                            else:
                                for index in range(pixels_in_line):
                                    pyautogui.click(first_point[0] + index, canvas_y + y)
                                pyautogui.click(canvas_x + x, canvas_y + y)
                            pixels_in_line = 0

                        else:
                            pyautogui.click(canvas_x + (x-1), canvas_y + y)
                        is_prev_color = False
                    else:
                        is_line = False
                        pixels_in_line = 0

        if config.getboolean("Painting", "save_while_painting"):
            pyautogui.click(ctrl_update)



    listener.stop()

    if config.getboolean("Painting", "save_when_completed"):
        pyautogui.click(ctrl_update)

    elapsed_time = int(time.time() - start_time)

    color_print("\nElapsed time:\t\t\t" + str(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))), Fore.GREEN)

    pyautogui.hotkey("alt", "tab")

    color_print("\nPress <ENTER> to exit...", Fore.YELLOW); input()





if __name__ == "__main__":
    main()
