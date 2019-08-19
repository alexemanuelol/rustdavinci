#!/usr/bin/env python3

import pyautogui
import PIL.ImageGrab
import time
import os


def main():
    pyautogui.PAUSE = 0.02

    tool_area_TL = (1474, 175)
    tool_area_BR = (1674, 751)

    paint_area_TL = (926, 295)

    tool_area_width = tool_area_BR[0] - tool_area_TL[0]
    tool_area_height = tool_area_BR[1] - tool_area_TL[1]

    print("Width = " +  str(tool_area_width))
    print("Height = " + str(tool_area_height))

    color_array = []

    pyautogui.screenshot("rust_palette.png", region=(1474, 390, 200, 361))
    pyautogui.screenshot("rust_palette_hidden.png", region=(926, 295, 200, 361))
    exit()

    for y in range(tool_area_height):
        for x in range(tool_area_width):
            pyautogui.click(tool_area_TL[0] + x, tool_area_TL[1] + y + 215)
            pyautogui.click(paint_area_TL[0] + x, paint_area_TL[1] + y)
            #current = PIL.ImageGrab.grab().load()[1376, 974]
            #if current not in color_array:
            #    color_array.append(current)
            #    print(current)
            #time.sleep(.1)


if __name__ == "__main__":
    main()
