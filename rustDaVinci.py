#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
import tkinter
from tkinter import filedialog
import pyautogui
import time
import win32gui
import win32con
import colorama
import termcolor

rust_palette_data = (
        46, 204, 113,   46, 157, 135,   39, 174, 96,    22, 160, 133,   29, 224, 25,
        52, 152, 218,   32, 203, 241,   74, 212, 189,   126, 76, 42,    68, 48, 34,
        241, 195, 15,   175, 122, 195,  240, 67, 49,    142, 68, 173,   230, 126, 34,
        152, 163, 163,  236, 240, 241,  49, 49, 49,     52, 73, 94,     2, 2, 2,

        91, 175, 118,   91, 144, 130,   89, 155, 109,   91, 148, 132,   87, 189, 86,
        93, 141, 185,   88, 174, 201,   99, 180, 164,   125, 100, 90,   98, 92, 88,
        202, 171, 90,   157, 126, 171,  202, 101, 96,   137, 102, 156,  195, 128, 93,
        143, 150, 150,  197, 200, 201,  92, 92, 92,     93, 100, 109,   84, 84, 84,

        111, 149, 121,  117, 138, 132,  116, 143, 123,  109, 134, 126,  110, 157, 109,
        111, 132, 155,  110, 149, 163,  114, 152, 144,  125, 114, 111,  113, 111, 110,
        163, 146, 109,  139, 123, 146,  155, 102, 99,   129, 113, 138,  159, 125, 110,
        137, 140, 140,  162, 163, 163,  111, 111, 111,  111, 114, 118,  109, 109, 109,

        126, 140, 129,  119, 127, 125,  126, 136, 128,  125, 134, 131,  126, 143, 125,
        120, 127, 136,  126, 139, 146,  127, 141, 138,  124, 120, 119,  120, 119, 119,
        146, 139, 125,  136, 130, 139,  145, 127, 126,  132, 127, 135,  138, 124, 119,
        127, 128, 128,  145, 145, 146,  119, 119, 119,  126, 127, 128,  119, 119, 119
)

click_delay = 0.020
line_delay = 0.020


def quantize_to_palette(original_image, palette):
    """ Convert an RGB or L mode image to use a given P image's palette.
    
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

    """
    pyautogui.PAUSE = line_delay
    pyautogui.mouseDown(button="left", x=point_A[0], y=point_A[1])
    pyautogui.keyDown("shift")
    pyautogui.moveTo(point_B[0], point_B[1])
    pyautogui.keyUp("shift")
    pyautogui.mouseUp(button="left")
    pyautogui.PAUSE = click_delay


def main():
    """ The main application
    
    """
    print("██████╗ ██╗   ██╗███████╗████████╗    ██████╗  █████╗     ██╗   ██╗██╗███╗   ██╗ ██████╗██╗")
    print("██╔══██╗██║   ██║██╔════╝╚══██╔══╝    ██╔══██╗██╔══██╗    ██║   ██║██║████╗  ██║██╔════╝██║")
    print("██████╔╝██║   ██║███████╗   ██║       ██║  ██║███████║    ██║   ██║██║██╔██╗ ██║██║     ██║")
    print("██╔══██╗██║   ██║╚════██║   ██║       ██║  ██║██╔══██║    ╚██╗ ██╔╝██║██║╚██╗██║██║     ██║")
    print("██║  ██║╚██████╔╝███████║   ██║       ██████╔╝██║  ██║     ╚████╔╝ ██║██║ ╚████║╚██████╗██║")
    print("╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝       ╚═════╝ ╚═╝  ╚═╝      ╚═══╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚═╝\n")

    print("Hello & Welcome to RustDaVinci!\n")
    
    print("Beneath follows the application instructions:\n")
    print("\t1. Firstly the application needs to capture the rust palette tools area.")
    print("\t2. Then it needs to capture the area in which the image will be painted.")
    print("\t3. Make sure that the console window is in focus when capturing the areas.")
    print("\t4. Make sure that the console window does not cover those two areas.\n")
    print("Follow the instructions below to begin the area capturing...\n")


    screen_size = pyautogui.size()

    palette_data = Image.new("P", (1, 1))
    palette_data.putpalette(rust_palette_data + (2,2,2)*176)

    pyautogui.PAUSE = click_delay

    hwnd = win32gui.GetForegroundWindow()


    input("1. Move the mouse pointer to the top left corner of the tools area and click <ENTER>...")
    tool_area_TL = pyautogui.position()
    input("2. Move the mouse pointer to the bottom right corner of the tools area and click <ENTER>...")
    tool_area_BR = pyautogui.position()

    input("3. Move the mouse pointer to the top left corner of the paint window and click <ENTER>...")
    paint_area_TL = pyautogui.position()
    input("4. Move the mouse pointer to the bottom right corner of the paint window and click <ENTER>...")
    paint_area_BR = pyautogui.position()


    # Set the console window as an overlay and place it on the left of the painting area
    # Uncomment the line below at your own risk, this might be the reason why I got banned...
    #win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0, (paint_area_TL[0] - 25), screen_size[1],0)

    tool_area_width = tool_area_BR[0] - tool_area_TL[0]
    tool_area_height = tool_area_BR[1] - tool_area_TL[1]

    paint_area_width = paint_area_BR[0] - paint_area_TL[0]
    paint_area_height = paint_area_BR[1] - paint_area_TL[1]


    # Initilize the tkinter module
    root = tkinter.Tk()
    root.withdraw()


    # Calculate the distance between two items on a row of six items (Size)
    first_x_coordinate_of_six_v1 = tool_area_TL[0] + (tool_area_width/6.7619)
    second_x_coordinate_of_six_v1 = tool_area_TL[0] + (tool_area_width/3.4634)
    distance_between_x_coordinates_of_six_v1 = second_x_coordinate_of_six_v1 - first_x_coordinate_of_six_v1

    # Calculate the distance between two items on a row of six items (Opacity)
    first_x_coordinate_of_six_v2 = tool_area_TL[0] + (tool_area_width/7.8888)
    second_x_coordinate_of_six_v2 = tool_area_TL[0] + (tool_area_width/3.6410)
    distance_between_x_coordinates_of_six_v2 = second_x_coordinate_of_six_v2 - first_x_coordinate_of_six_v2

    # Calculate the distance between two items on a row of four items
    first_x_coordinate_of_four = tool_area_TL[0] + (tool_area_width/6.1739)
    second_x_coordinate_of_four = tool_area_TL[0] + (tool_area_width/2.5818)
    distance_between_x_coordinates_of_four = second_x_coordinate_of_four - first_x_coordinate_of_four

    # Calculate the distance between two items on a column of eight items
    first_y_coordinate_of_eight = tool_area_TL[1] + (tool_area_height/2.3238)
    second_y_coordinate_of_eight = tool_area_TL[1] + (tool_area_height/1.9854)
    distance_between_y_coordinates_of_eight = second_y_coordinate_of_eight - first_y_coordinate_of_eight

    # Set the point location of the remove & update buttons
    tool_remove = ((tool_area_TL[0] + (tool_area_width/2.7843)), (tool_area_TL[1] + (tool_area_height/20.45)))
    tool_update = ((tool_area_TL[0] + (tool_area_width/1.5604)), (tool_area_TL[1] + (tool_area_height/20.45)))


    tool_size = []
    for size in range(6):
        tool_size.append( (first_x_coordinate_of_six_v1 + (size * distance_between_x_coordinates_of_six_v1), 
                          (tool_area_TL[1] + (tool_area_height/7.0517)))
                        )

    tool_brush = []
    for brush in range(4):
        tool_brush.append( (first_x_coordinate_of_four + (brush * distance_between_x_coordinates_of_four), 
                          (tool_area_TL[1] + (tool_area_height/4.2604)))
                        )

    tool_opacity = []
    for opacity in range(6):
        tool_opacity.append( (first_x_coordinate_of_six_v2 + (opacity * distance_between_x_coordinates_of_six_v2), 
                          (tool_area_TL[1] + (tool_area_height/3.0296)))
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


    image_path = filedialog.askopenfilename()
    if image_path.endswith(('.png', '.jpg', 'jpeg', '.gif', '.bmp')):
        print("\nDithering process started...")
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
        #dithered_image.save("Preview.png")
        dithered_image.show(title="Preview")
    else:
        print("Invalid picture format...")
        exit()

    dithered_image_width = dithered_image.size[0]
    dithered_image_height = dithered_image.size[1]
        
    pixel = dithered_image.load()

    print("Counting colors...\nCounting pixels...")
    image_colors = []
    total_number_of_pixels_to_paint = 0
    for y in range(dithered_image_height):
        for x in range(dithered_image_width):
            if pixel[x, y] is not 16:
                total_number_of_pixels_to_paint += 1
            if pixel[x, y] not in image_colors:
                image_colors.append(pixel[x, y])
    number_of_image_colors = len(image_colors)

    print("Counting lines...")
    number_of_pixels_to_paint = 0
    number_of_lines = 0
    for color in image_colors:
        if color == 16: continue
        is_first_point_of_row = True
        is_last_point_of_row = False
        prev_is_color = False
        is_line = False

        for y in range(dithered_image_height):
            is_first_point_of_row = True
            is_last_point_of_row = False
            is_prev_color = False
            is_line = False

            for x in range(dithered_image_width):
                if x == dithered_image_width: is_last_point_of_row = True

                if is_first_point_of_row:
                    is_first_point_of_row = False
                    if pixel[x, y] == color: prev_is_color = True
                    continue

                if pixel[x, y] == color:
                    if prev_is_color:
                        if is_last_point_of_row: number_of_lines += 1
                        else: is_line = True
                    else:
                        if is_last_point_of_row: number_of_pixels_to_paint += 1
                        else: prev_is_color = True
                else:
                    if prev_is_color:
                        if is_line: is_line = False; number_of_lines += 1
                        else: number_of_pixels_to_paint += 1
                        prev_is_color = False


    # Calculate the estimated time of the paint
    one_line_time = (line_delay + 0.0036) * 5
    one_click_time = click_delay + 0.001
    change_color_time = number_of_image_colors * 0.342
    other_time = 0.563
    estimated_time = int((number_of_pixels_to_paint * one_click_time) + (number_of_lines * one_line_time) + change_color_time + other_time)

    # Information
    print("\nImage Width  = " + str(dithered_image.size[0]))
    print("Image Height = " + str(dithered_image.size[1]))
    print("\nNumber of colors:\t\t" + str(number_of_image_colors))
    print("Number of pixels to paint:\t" + str(number_of_pixels_to_paint))
    print("Number of lines:\t\t" + str(number_of_lines))
    print("Est. painting time:\t\t" + str(estimated_time))

    print("\nPress <ENTER> to start the painting process..."); input()

    start_time = time.time()


    pyautogui.click(tool_size[0]); # To set focus on the rust window
    time.sleep(.5)
    pyautogui.click(tool_size[0]);
    pyautogui.click(tool_brush[1]);


    color_counter = 0
    for color in image_colors:
        print("(" + str((color_counter+1)) + "/" + str((number_of_image_colors)) + ") Current color: " + str(color))
        color_counter += 1

        if color == 16: continue

        time.sleep(.1)
        if   color >= 0  and color < 20: pyautogui.click(tool_opacity[5])
        elif color >= 20 and color < 40: pyautogui.click(tool_opacity[4])
        elif color >= 40 and color < 60: pyautogui.click(tool_opacity[3])
        elif color >= 60 and color < 80: pyautogui.click(tool_opacity[2])
        time.sleep(.1)

        final_x_coordinate = paint_area_TL[0] + x_coordinate_correction
        final_y_coordinate = paint_area_TL[1] + y_coordinate_correction

        first_point = (0, 0)
        is_first_point_of_row = True
        is_last_point_of_row = False
        prev_is_color = False
        is_line = False

        pyautogui.click(tool_color[color%20])
        time.sleep(.1)

        for y in range(dithered_image_height):
            is_first_point_of_row = True
            is_last_point_of_row = False
            is_prev_color = False
            is_line = False

            for x in range(dithered_image_width):

                if x == dithered_image_width:
                    is_last_point_of_row = True

                if is_first_point_of_row:
                    is_first_point_of_row = False
                    if pixel[x, y] == color:
                        first_point = (final_x_coordinate + x, final_y_coordinate + y)
                        prev_is_color = True
                    continue

                if pixel[x, y] == color:
                    if prev_is_color:
                        if is_last_point_of_row:
                            draw_line(first_point, (final_x_coorindate + x, final_y_coordinate + y))
                        else:
                            is_line = True
                    else:
                        if is_last_point_of_row:
                            pyautogui.click(final_x_coordinate + x, final_y_coordinate + y)
                        else:
                            prev_is_color = True
                            first_point = (final_x_coordinate + x, final_y_coordinate + y)
                else:
                    if prev_is_color:
                        if is_line:
                            is_line = False
                            draw_line(first_point, (final_x_coordinate + (x-1), final_y_coordinate + y))
                        else:
                            pyautogui.click(final_x_coordinate + (x-1), final_y_coordinate + y)
                        prev_is_color = False



    #########################################################

    elapsed_time = int(time.time() - start_time)

    print("Elapsed time: {}".format(elapsed_time))

    pyautogui.hotkey("alt", "tab")

    input("Press <ENTER> to exit...")







if __name__ == "__main__":
    main()
