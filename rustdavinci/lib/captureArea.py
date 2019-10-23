#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pynput import keyboard

import tkinter
import pyautogui
import win32api
import time

abort_capturing_mode = False


def key_event(key):
    """ Abort capturing mode """
    global abort_capturing_mode
    abort_capturing_mode = True


def capture_area():
    """ Capture an area on the screen by clicking and dragging the mouse to the bottom right corner.
    Returns:    area_x,
                area_y,
                area_width,
                area_height
    """
    global abort_capturing_mode
    listener = keyboard.Listener(on_press=key_event)
    listener.start()

    root = tkinter.Tk().withdraw()
    area = tkinter.Toplevel(root)
    area.overrideredirect(1)
    area.wm_attributes('-alpha',0.5)
    area.geometry("0x0")

    prev_state = win32api.GetKeyState(0x01)
    pressed, active = False, False

    while True:
        if abort_capturing_mode:
            abort_capturing_mode = False
            listener.stop()
            return False

        current_state = win32api.GetKeyState(0x01)
        mouse = pyautogui.position()

        if current_state != prev_state:
            prev_state = current_state
            pressed = True if current_state < 0 else False

        try:
            if pressed:
                if not active:
                    area_TL = mouse
                    active = True
                area.geometry(str(mouse[0] - area_TL[0])+ "x" + str(mouse[1] - area_TL[1]))
            elif not pressed:
                if active:
                    area.destroy()
                    if area_TL[0] >= mouse[0] or area_TL[1] >= mouse[1]:
                        listener.stop()
                        return 0, 0, 0, 0
                    listener.stop()
                    return area_TL[0], area_TL[1], mouse[0] - area_TL[0], mouse[1] - area_TL[1]
                area.geometry("+" + str(mouse[0])+ "+" + str(mouse[1]))

        except Exception: pass

        area.update_idletasks()
        area.update()


def show_area(x, y, w, h):
    """ Set a grey box at the coordinates """
    global abort_capturing_mode
    listener = keyboard.Listener(on_press=key_event)
    listener.start()

    root = tkinter.Tk().withdraw()
    area = tkinter.Toplevel(root)
    area.overrideredirect(1)
    area.wm_attributes('-alpha',0.5)
    area.geometry("0x0")

    area.geometry("%dx%d+%d+%d" % (w, h, x, y))

    area.update_idletasks()
    area.update()

    time.sleep(3)

    area.destroy()