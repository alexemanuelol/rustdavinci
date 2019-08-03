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

import rustPalette




# Read from the configuration file
config = configparser.ConfigParser(comment_prefixes="/", allow_no_value=True)
config.read("config.ini")

# Select the palette to be used
palette_data = Image.new("P", (1, 1))
palette_data.putpalette(rustPalette.palette_80)
#palette_data.putpalette(rustPalette.palette_greyscale)

ctypes.windll.kernel32.SetConsoleTitleW("RustDaVinci")

init()  # Initilize colorama module


is_skip_colors = [16, 36, 56, 76]
is_skip_colors.append(config.getint("General", "default_background_color"))


click_delay_ms = config.getint("Experimental", "click_delay")
if click_delay_ms <= 0: click_delay = 0
elif click_delay_ms > 0: click_delay = float(click_delay_ms / 1000)

line_delay_ms = config.getint("Experimental", "line_delay")
if line_delay_ms <= 0: line_delay = 0
elif line_delay_ms > 0: line_delay = float(line_delay_ms / 1000)

loop_delay_ms = config.getint("Experimental", "loop_delay")
if loop_delay_ms <= 0: loop_delay = 0
elif loop_delay_ms > 0: loop_delay = float(loop_delay_ms / 1000)

control_area_delay_ms = config.getint("Experimental", "control_area_delay")
if control_area_delay_ms <= 0: control_area_delay = 0
elif control_area_delay_ms > 0: control_area_delay = float(control_area_delay_ms / 1000)


pyautogui.PAUSE = click_delay


minimum_line_width = config.getint("Experimental", "minimum_line_width")


is_paused = False
is_skip_color = False
is_exit = False




def auto_locate_control_area():
    """ Automatically tries to find the painting control area with opencv

    Returns:    control_area_x, control_area_y, control_area_width, control_area_height if found
                False, if no control area was found
    """
    image_screenshot = pyautogui.screenshot()
    screen_width, screen_height = image_screenshot.size

    image_gray = cv2.cvtColor(np.array(image_screenshot), cv2.COLOR_BGR2GRAY)

    template = cv2.imread("opencv_template/rust_palette_template.png", 0)
    template_width, template_height = template.shape[::-1]

    x_coordinate, y_coordinate = 0, 0
    threshold = 0.8

    for loop in range(50):
        matches = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(matches >= threshold)

        x_list, y_list = [], []
        for point in zip(*loc[::-1]):
            x_list.append(point[0])
            y_list.append(point[1])

        if x_list:
            x_coordinate = int(sum(x_list) / len(x_list))
            y_coordinate = int(sum(y_list) / len(y_list))
            return x_coordinate, y_coordinate, template_width, template_height
    
        template_width, template_height = int(template.shape[1]*1.035), int(template.shape[0]*1.035)
        template = cv2.resize(template, (int(template_width), int(template_height)))

        if template_width > screen_width or template_height > screen_height or loop == 49:
            print("No tool area was found...\n")
            return False


def locate_control_area():
    """ Locate the control area

    Returns:    control_area_x, control_area_y, control_area_width, control_area_height
    """
    global config

    remember_control_area_coordinates = config.getboolean("Painting", "remember_control_area_coordinates")
    auto_find_control_area = config.getboolean("Painting", "auto_find_control_area")

    if remember_control_area_coordinates:
        if config("Painting", "control_area_x") != "None":
            return  config.getint("Painting", "control_area_x"), \
                    config.getint("Painting", "control_area_y"), \
                    config.getint("Painting", "control_area_width"), \
                    config.getint("Painting", "control_area_height")

    if auto_find_control_area:
        print("Locating tool area automatically...\n")
        tool_area = auto_locate_control_area()

    if auto_find_control_area and tool_area is not False:
        print("Tool area found!\n")
    else:
        input("1. Move the mouse pointer to the top left corner of the tools area and click <ENTER>...")
        tool_area_TL = pyautogui.position()
        input("2. Move the mouse pointer to the bottom right corner of the tools area and click <ENTER>...")
        tool_area_BR = pyautogui.position()
        tool_area_width = tool_area_BR[0] - tool_area_TL[0]
        tool_area_height = tool_area_BR[1] - tool_area_TL[1]
        tool_area = (tool_area_TL[0], tool_area_TL[1], tool_area_width, tool_area_height)


    if remember_control_area_coordinates:
        config["Painting"]["control_area_x"] = str(tool_area[0])
        config["Painting"]["control_area_y"] = str(tool_area[1])
        config["Painting"]["control_area_width"] = str(tool_area[2])
        config["Painting"]["control_area_height"] = str(tool_area[3])
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    return  tool_area[0], tool_area[1], tool_area[2], tool_area[3]


def calculate_control_positioning(x, y, width, height):
    # Calculate the distance between two items on a row of six items (Size)
    first_x_coordinate_of_six_v1 = x + (width/6.5454)
    second_x_coordinate_of_six_v1 = x + (width/3.4285)
    distance_between_x_coordinates_of_six_v1 = second_x_coordinate_of_six_v1 - first_x_coordinate_of_six_v1

    # Calculate the distance between two items on a row of six items (Opacity)
    first_x_coordinate_of_six_v2 = x + (width/7.5789)
    second_x_coordinate_of_six_v2 = x + (width/3.5555)
    distance_between_x_coordinates_of_six_v2 = second_x_coordinate_of_six_v2 - first_x_coordinate_of_six_v2

    # Calculate the distance between two items on a row of four items (Colors width)
    first_x_coordinate_of_four = x + (width/6)
    second_x_coordinate_of_four = x + (width/2.5714)
    distance_between_x_coordinates_of_four = second_x_coordinate_of_four - first_x_coordinate_of_four

    # Calculate the distance between two items on a column of eight items (Colors height)
    first_y_coordinate_of_eight = y + (height/2.3220)
    second_y_coordinate_of_eight = y + (height/1.9855)
    distance_between_y_coordinates_of_eight = second_y_coordinate_of_eight - first_y_coordinate_of_eight

    # Set the point location of the remove & update buttons
    tool_remove = ((x + (width/2.7692)), (y + (height/19.5714)))
    tool_update = ((x + (width/1.5652)), (y + (height/19.5714)))


    tool_size = []
    for size in range(6):
        tool_size.append( (first_x_coordinate_of_six_v1 + (size * distance_between_x_coordinates_of_six_v1), 
                          (y + (height/6.9661)))
                        )

    tool_brush = []
    for brush in range(4):
        tool_brush.append( (first_x_coordinate_of_four + (brush * distance_between_x_coordinates_of_four), 
                          (y + (height/4.2371)))
                        )

    tool_opacity = []
    for opacity in range(6):
        tool_opacity.append( (first_x_coordinate_of_six_v2 + (opacity * distance_between_x_coordinates_of_six_v2), 
                          (y + (height/3.0332)))
                        )

    tool_color = []
    for row in range(8):
        for column in range(4):
            if (row == 0 or row == 4) and column == 3: continue
            if (row == 1 or row == 5) and (column == 2 or column == 3): continue
            if row == 2 and column == 0: continue
            if row == 3 and (column == 0 or column == 1): continue
            if row == 6 and column == 2: continue
            if row == 7 and (column == 1 or column == 2): continue
            tool_color.append( (first_x_coordinate_of_four + (column * distance_between_x_coordinates_of_four),
                               (first_y_coordinate_of_eight + (row * distance_between_y_coordinates_of_eight)))
                        )

    # TODO: Experiment with positioning of new (hidden) colors. Append individual colors to the tool_color list

    return tool_remove, tool_update, tool_size, tool_brush, tool_opacity, tool_color


def select_image_for_painting(paint_area_width, paint_area_height):
    """ Select the image that is going to be painted

    Returns:    The dithered image
                False, if the image type is invalid
    """
    global palette_data
    image_path = filedialog.askopenfilename(title="Select the image to be painted")
    if image_path.endswith(('.png', '.jpg', 'jpeg', '.gif', '.bmp')):
        color_print("\nDithering process started...", Fore.YELLOW)
        original_image = Image.open(image_path)

        original_image_width = original_image.size[0]
        original_image_height = original_image.size[1]
        
        wpercent = (paint_area_width / float(original_image_width))
        hpercent = (paint_area_height / float(original_image_height))

        hsize = int((float(original_image_height) * float(wpercent)))
        wsize = int((float(original_image_width) * float(hpercent)))

        x_coordinate_correction = 0
        y_coordinate_correction = 0

        if hsize <= paint_area_height: 
            original_image = original_image.resize((paint_area_width, hsize), Image.ANTIALIAS)
            y_coordinate_correction = int((paint_area_height - hsize)/2)
        elif wsize <= paint_area_width: 
            original_image = original_image.resize((wsize, paint_area_height), Image.ANTIALIAS)
            x_coordinate_correction = int((paint_area_width - wsize)/2)
        else: 
            original_image = original_image.resize((paint_area_width, paint_area_height), Image.ANTIALIAS)

        dithered_image = quantize_to_palette(original_image, palette_data)

        if config.getboolean("Painting", "save_preview"):
            dithered_image.save(config("Painting", "path_for_preview_image") + "Preview.png")
        if config.getboolean("Painting", "show_preview"):
            dithered_image.show(title="Preview")

        return dithered_image, x_coordinate_correction, y_coordinate_correction
    else:
        color_print("Invalid picture format...", Fore.RED)
        return False


def count_color_pixel_line(pixel_array, image_width, image_height):
    """ Counting the colors, total amout of pixels to paint and lines
    
    Returns:    Number of colors
                Total amount of pixels to paint
                Number of pixels to paint
                Number of lines to be drawn
    """
    color_print("Counting colors...\nCounting pixels...", Fore.YELLOW)
    image_colors = []
    total_number_of_pixels_to_paint = 0
    for y in range(image_height):
        for x in range(image_width):
            if pixel_array[x, y] is not 16: total_number_of_pixels_to_paint += 1
            if pixel_array[x, y] not in image_colors: image_colors.append(pixel_array[x, y])
    number_of_image_colors = len(image_colors)

    color_print("Counting lines...", Fore.YELLOW)
    number_of_pixels_to_paint = 0
    number_of_lines = 0
    for color in image_colors:
        if color in is_skip_colors: continue
        is_first_point_of_row = True
        is_last_point_of_row = False
        prev_is_color = False
        is_line = False
        pixels_in_line = 0

        for y in range(image_height):
            is_first_point_of_row = True
            is_last_point_of_row = False
            is_prev_color = False
            is_line = False
            pixels_in_line = 0

            for x in range(image_width):
                if x == (image_width - 1): is_last_point_of_row = True

                if is_first_point_of_row:
                    is_first_point_of_row = False
                    if pixel_array[x, y] == color: prev_is_color = True
                    continue

                if pixel_array[x, y] == color:
                    if prev_is_color:
                        if is_last_point_of_row:
                            if pixels_in_line >= minimum_line_width: number_of_lines += 1
                            else:
                                number_of_pixels_to_paint += (pixels_in_line + 1)
                        else: is_line = True; pixels_in_line += 1
                    else:
                        if is_last_point_of_row: number_of_pixels_to_paint += 1
                        else:
                            prev_is_color = True
                            pixels_in_line += 1
                else:
                    if prev_is_color:
                        if is_line:
                            is_line = False
                            if pixels_in_line >= minimum_line_width: number_of_lines += 1
                            else: number_of_pixels_to_paint += (pixels_in_line + 1)
                            pixels_in_line = 0
                        else: number_of_pixels_to_paint += 1
                        prev_is_color = False
                    else:
                        is_line = False
                        pixels_in_line = 0

    return  image_colors, \
            number_of_image_colors, \
            total_number_of_pixels_to_paint, \
            number_of_pixels_to_paint, \
            number_of_lines


def calculate_estimated_time(colors, tot_pixels, pixels, lines):
    """ Calculate estimated time for the painting process

    Returns:    Estimated time for clicking and lines
                Estimated time for only clicking
    """
    one_line_time = (line_delay + 0.0036 +0.0025) * 5
    one_click_time = click_delay + loop_delay + 0.001
    change_color_time = colors * (control_area_delay + (2 * click_delay))
    other_time = 0.5 + (3 * click_delay) + (2 * loop_delay)
    estimated_time_lines = int((pixels * one_click_time) + (lines * one_line_time) + change_color_time + other_time)
    estimated_time_click = int((tot_pixels * one_click_time) + change_color_time + other_time)

    return estimated_time_lines, estimated_time_click


def quantize_to_palette(original_image, palette):
    """ Convert an RGB or L mode image to use a given P image's palette.

    Returns:    The converted image
    """
    original_image.load()
    palette.load()

    if palette.mode != "P":
        raise ValueError("Bad mode for palette image")

    if original_image.mode != "RGB" and silf.mode != "L":
        raise ValueError("Only RGB or L mode images can be quantized to a palette")

    im = original_image.im.convert("P", 1, palette.im)

    try: return original_image._new(im)
    except AttributeError: return original_image._makeself(im)


def draw_line(point_A, point_B):
    """ Draws a line between point_A and point_B.

    Returns:    None
    """
    pyautogui.PAUSE = line_delay
    pyautogui.mouseDown(button="left", x=point_A[0], y=point_A[1])
    pyautogui.keyDown("shift")
    pyautogui.moveTo(point_B[0], point_B[1])
    pyautogui.keyUp("shift")
    pyautogui.mouseUp(button="left")
    pyautogui.PAUSE = click_delay
    time.sleep(.0025)


def on_press(key):
    """ Key-press handler
    
    Returns:    None
    """
    global is_paused, is_skip_color, is_exit
    if key == keyboard.Key.f10:
        is_paused = not is_paused
        if is_paused:
            color_print("PAUSED\t\tF10 = Continue, F11 = Skip color, ESC = Exit", Fore.YELLOW)
    elif key == keyboard.Key.f11:
        is_paused = False
        is_skip_color = True
    elif key == keyboard.Key.esc:
        is_paused = False
        is_exit = True


def color_print(message, color):
    """ Print function with different colors

    Colors:     BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE

    Returns:    None
    """
    print(color + message + Fore.RESET)


def main():
    """ The main application
    """
    print("")
    color_print("██████╗ ██╗   ██╗███████╗████████╗    ██████╗  █████╗     ██╗   ██╗██╗███╗   ██╗ ██████╗██╗", Fore.RED)
    color_print("██╔══██╗██║   ██║██╔════╝╚══██╔══╝    ██╔══██╗██╔══██╗    ██║   ██║██║████╗  ██║██╔════╝██║", Fore.RED)
    color_print("██████╔╝██║   ██║███████╗   ██║       ██║  ██║███████║    ██║   ██║██║██╔██╗ ██║██║     ██║", Fore.RED)
    color_print("██╔══██╗██║   ██║╚════██║   ██║       ██║  ██║██╔══██║    ╚██╗ ██╔╝██║██║╚██╗██║██║     ██║", Fore.RED)
    color_print("██║  ██║╚██████╔╝███████║   ██║       ██████╔╝██║  ██║     ╚████╔╝ ██║██║ ╚████║╚██████╗██║", Fore.RED)
    color_print("╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝       ╚═════╝ ╚═╝  ╚═╝      ╚═══╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚═╝\n", Fore.RED)

    color_print("Hello & Welcome to RustDaVinci!\n", Fore.RED)
    
    color_print("Beneath follows the application instructions:\n", Fore.RED)
    color_print("\t1. Firstly the application needs to capture the rust palette tools area.", Fore.RED)
    color_print("\t2. Then it needs to capture the area in which the image will be painted.", Fore.RED)
    color_print("\t3. Make sure that the console window is in focus when capturing the areas.", Fore.RED)
    color_print("\t4. Make sure that the console window does not cover those two areas.\n", Fore.RED)
    color_print("Follow the instructions below to begin the area capturing...\n", Fore.RED)


    # Get the tool area coordinates and ratio
    control_area_x, control_area_y, control_area_width, control_area_height = locate_control_area()
    #print("control_area_x:      " + str(control_area_x))
    #print("control_area_y:      " + str(control_area_y))
    #print("control_area_width:  " + str(control_area_width))
    #print("control_area_height: " + str(control_area_height))
    #time.sleep(1)
    #pyautogui.moveTo(control_area_x, control_area_y)
    #time.sleep(3)
    #pyautogui.moveTo(control_area_x + control_area_width, control_area_y + control_area_height)
    #time.sleep(3)


    # Get the paint area coordinates and ratio
    input("3. Move the mouse pointer to the top left corner of the paint window and click <ENTER>...")
    paint_area_TL = pyautogui.position()
    input("4. Move the mouse pointer to the bottom right corner of the paint window and click <ENTER>...")
    paint_area_BR = pyautogui.position()

    paint_area_x, paint_area_y = paint_area_TL[0], paint_area_TL[1]
    paint_area_width = paint_area_BR[0] - paint_area_TL[0]
    paint_area_height = paint_area_BR[1] - paint_area_TL[1]




    screen_size = pyautogui.size()
    # Set the console window as an overlay and place it on the left of the painting area
    if config.getboolean("General", "window_on_top"):
        hwnd = win32gui.GetForegroundWindow()
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0, (paint_area_TL[0] - 25), screen_size[1],0)


    # Initilize the tkinter module
    root = tkinter.Tk()
    root.withdraw()

    # Calculate the control positions
    tool_remove, \
    tool_update, \
    tool_size, \
    tool_brush, \
    tool_opacity, \
    tool_color = calculate_control_positioning( control_area_x, 
                                                control_area_y, 
                                                control_area_width, 
                                                control_area_height)

    # Debug purposes
    #pyautogui.moveTo(tool_remove)
    #time.sleep(1)
    #pyautogui.moveTo(tool_update)
    #time.sleep(1)

    #for i in range(6):
    #    pyautogui.moveTo(tool_size[i])
    #    time.sleep(1)

    #for i in range(4):
    #    pyautogui.moveTo(tool_brush[i])
    #    time.sleep(1)

    #for i in range(6):
    #    pyautogui.moveTo(tool_opacity[i])
    #    time.sleep(1)

    #for i in range(20):
    #    pyautogui.moveTo(tool_color[i])
    #    time.sleep(1)


    # Select the image to be dithered and painted
    dithered_image, x_coordinate_correction, y_coordinate_correction = select_image_for_painting(paint_area_width, paint_area_height)
    paint_area_x += x_coordinate_correction
    paint_area_y += y_coordinate_correction

    if dithered_image == False: exit()

    dithered_image_width = dithered_image.size[0]
    dithered_image_height = dithered_image.size[1]
        
    pixel_array = dithered_image.load()


    # Counter statistics (Tot amount of pixels, lines, colors etc...)
    statistics = count_color_pixel_line(pixel_array,
                                        dithered_image_width,
                                        dithered_image_height)

    image_colors = statistics[0]
    num_of_image_colors = statistics[1]
    tot_num_pixels_to_paint = statistics[2]
    num_pixels_to_paint = statistics[3]
    num_of_lines = statistics[4]


    # Calculate the estimated time of the paint
    estimated_time_line, estimated_time_click = calculate_estimated_time(   num_of_image_colors,
                                                                            tot_num_pixels_to_paint,
                                                                            num_pixels_to_paint,
                                                                            num_of_lines)

    prefer_lines = False
    if estimated_time_line < estimated_time_click:
        print("\nGoing for lines...")
        prefer_lines = True
        estimated_time = estimated_time_line
    else:
        print("\nGoing for clicks...")
        estimated_time = estimated_time_click


    # Print information about the paint
    color_print("\nDimensions: \t\t\t\t" + str(dithered_image_width) + " x " + str(dithered_image_height), Fore.GREEN)
    color_print("\nNumber of colors:\t\t\t" + str(num_of_image_colors), Fore.GREEN)
    color_print("Total Number of pixels to paint: \t" + str(tot_num_pixels_to_paint), Fore.GREEN)
    color_print("Number of pixels to paint:\t\t" + str(num_pixels_to_paint), Fore.GREEN)
    color_print("Number of lines:\t\t\t" + str(num_of_lines), Fore.GREEN)
    color_print("Est. painting time (click only):\t" + str(time.strftime("%H:%M:%S", time.gmtime(estimated_time_click))), Fore.GREEN)
    color_print("Est. painting time (with lines):\t" + str(time.strftime("%H:%M:%S", time.gmtime(estimated_time_line))), Fore.GREEN)

    color_print("\nPress <ENTER> to start the painting process...\n", Fore.YELLOW); input()


    color_print("Est. time finished:\t\t" + str((datetime.datetime.now() + datetime.timedelta(seconds=estimated_time)).time().strftime("%H:%M:%S")) + "\n", Fore.GREEN)

    color_print("F10 = Continue, F11 = Skip color, ESC = Exit\n", Fore.GREEN)

    start_time = time.time()


    # Start listening for key-presses
    listener = keyboard.Listener(on_press=on_press)
    listener.start()


    pyautogui.click(tool_size[0]) # To set focus on the rust window
    time.sleep(.5)
    pyautogui.click(tool_size[0]); time.sleep(loop_delay)
    pyautogui.click(tool_brush[config.getint("Painting", "default_brush")]); time.sleep(loop_delay)


    color_counter = 0
    for color in image_colors:
        is_skip_color = False
        color_print("(" + str((color_counter+1)) + "/" + str((num_of_image_colors)) + ") Current color: " + str(color), Fore.MAGENTA)
        color_counter += 1

        if color in is_skip_colors: continue

        time.sleep(0 if control_area_delay == 0 else control_area_delay / 3)
        if   color >= 0  and color < 20: pyautogui.click(tool_opacity[5])
        elif color >= 20 and color < 40: pyautogui.click(tool_opacity[4])
        elif color >= 40 and color < 60: pyautogui.click(tool_opacity[3])
        elif color >= 60 and color < 80: pyautogui.click(tool_opacity[2])
        time.sleep(0 if control_area_delay == 0 else control_area_delay / 3)


        first_point = (0, 0)
        is_first_point_of_row = True
        is_last_point_of_row = False
        prev_is_color = False
        is_line = False
        pixels_in_line = 0

        pyautogui.click(tool_color[color%20])
        time.sleep(0 if control_area_delay == 0 else control_area_delay / 3)

        for y in range(dithered_image_height):
            if is_skip_color: break
            is_first_point_of_row = True
            is_last_point_of_row = False
            is_prev_color = False
            is_line = False
            pixels_in_line = 0

            for x in range(dithered_image_width):

                while is_paused: None

                if is_skip_color: color_print("Skipping current color...", Fore.YELLOW); break
                if is_exit:
                    elapsed_time = int(time.time() - start_time)
                    color_print("\nElapsed time:\t\t\t" + str(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))), Fore.GREEN)
                    color_print("\nExiting...", Fore.RED)
                    exit()

                if x == (dithered_image_width - 1):
                    is_last_point_of_row = True

                if is_first_point_of_row and prefer_lines:
                    is_first_point_of_row = False
                    if pixel_array[x, y] == color:
                        first_point = (paint_area_x + x, paint_area_y + y)
                        prev_is_color = True
                        pixels_in_line = 1
                    continue

                if pixel_array[x, y] == color:
                    if not prefer_lines: pyautogui.click(paint_area_x + x, paint_area_y + y); time.sleep(loop_delay); continue
                    if prev_is_color:
                        if is_last_point_of_row:
                            if pixels_in_line >= minimum_line_width:
                                draw_line(first_point, (paint_area_x + x, paint_area_y + y))
                            else:
                                for index in range(pixels_in_line):
                                    pyautogui.click(first_point[0] + index, paint_area_y + y); time.sleep(loop_delay)
                                pyautogui.click(paint_area_x + x, paint_area_y + y)
                        else:
                            is_line = True
                            pixels_in_line += 1
                    else:
                        if is_last_point_of_row:
                            pyautogui.click(paint_area_x + x, paint_area_y + y)
                            time.sleep(loop_delay)
                        else:
                            first_point = (paint_area_x + x, paint_area_y + y)
                            prev_is_color = True
                            pixels_in_line = 1
                else:
                    if not prefer_lines: continue
                    if prev_is_color:
                        if is_line:
                            is_line = False
                            if pixels_in_line >= minimum_line_width:
                                draw_line(first_point, (paint_area_x + (x-1), paint_area_y + y))
                            else:
                                for index in range(pixels_in_line):
                                    pyautogui.click(first_point[0] + index, paint_area_y + y)
                                    time.sleep(loop_delay)
                                pyautogui.click(paint_area_x + x, paint_area_y + y)
                            pixels_in_line = 0

                        else:
                            pyautogui.click(paint_area_x + (x-1), paint_area_y + y)
                            time.sleep(loop_delay)
                        prev_is_color = False
                    else:
                        is_line = False
                        pixels_in_line = 0
        if config.getboolean("Painting", "save_while_painting"):
            pyautogui.click(tool_update); time.sleep(loop_delay)



    listener.stop()

    if config.getboolean("Painting", "save_when_completed"):
        pyautogui.click(tool_update); time.sleep(loop_delay)

    elapsed_time = int(time.time() - start_time)

    color_print("\nElapsed time:\t\t\t" + str(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))), Fore.GREEN)

    pyautogui.hotkey("alt", "tab")

    color_print("\nPress <ENTER> to exit...", Fore.YELLOW); input()





if __name__ == "__main__":
    main()
