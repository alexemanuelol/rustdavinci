#!/usr/bin/env python3

import cv2
import numpy as np
import pyautogui
import time


def locate_palette():
    image_screenshot = pyautogui.screenshot()
    screen_width, screen_height = image_screenshot.size

    image_gray = cv2.cvtColor(np.array(image_screenshot), cv2.COLOR_BGR2GRAY)

    template = cv2.imread("rust_palette_template.png", 0)
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
            print("No match was found...")
            return False



if __name__ == "__main__":
    tool_area = locate_palette()

    if tool_area is not False:
        tool_area_TL = (tool_area[0], tool_area[1])
        tool_area_width = tool_area[2]
        tool_area_height = tool_area[3]

        print(tool_area_TL)
        print("width =  " + str(tool_area_width))
        print("height = " + str(tool_area_height))

        pyautogui.moveTo(tool_area_TL)
        time.sleep(3)
        pyautogui.moveTo(tool_area_TL[0] + tool_area_width, tool_area_TL[1] + tool_area_height)



# Youtube video
#https://www.youtube.com/watch?v=2CZltXv-Gpk
