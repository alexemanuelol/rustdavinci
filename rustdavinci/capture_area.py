import tkinter as tk
import pyautogui
import win32api


# Super sexy function, I love it
def capture_area():
    """ Capture an area on the screen by clicking and dragging the mouse to the bottom right corner.
    Returns:    area_x,
                area_y,
                area_width,
                area_height
    """
    root = tk.Tk().withdraw()
    window = tk.Toplevel(root)
    window.overrideredirect(1)
    window.wm_attributes('-alpha',0.5)
    window.geometry("0x0")

    prev_state = win32api.GetKeyState(0x01)
    pressed, active = False, False

    while True:
        current_state = win32api.GetKeyState(0x01)
        mouse = pyautogui.position()

        if current_state != prev_state:
            prev_state = current_state
            pressed = True if current_state < 0 else False

        if pressed:
            if not active: area_TL = mouse; active = True
            winposdiff = (mouse[0] - winpos[0], mouse[1] - winpos[1])
            winsize = str(winposdiff[0])+ "x" + str(winposdiff[1])
            window.geometry(winsize)
                    
        elif not pressed:
            if active:
                area_BR = mouse
                window.destroy()
                return area_TL[0], area_TL[1], area_BR[0] - area_TL[0], area_BR[1] - area_TL[1]

            winpos = (mouse[0], mouse[1])
            window.geometry("+" + str(mouse[0])+ "+" + str(mouse[1]))

        window.update_idletasks()
        window.update()


if __name__ == "__main__":
    print(capture_area())
