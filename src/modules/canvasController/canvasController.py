#!/usr/bin/env python3

import cv2
import json
import keyboard
import numpy as np
import os
import pyautogui
import time

from PIL import ImageGrab
from enum import Enum
from typing import Optional, Tuple, List, Dict


CANVAS_CONTROLS_TIMEOUT_S = 0.5

# Tuple: control name, similarity threashold
CLEAR_CANVAS_TEMPLATE = ('clear_canvas_template', .9)
SAVE_TO_DESKTOP_TEMPLATE = ('save_to_desktop_template', .9)
SAVE_CHANGES_CONTINUE_TEMPLATE = ('save_changes_continue_template', .9)
UNDO_ACTIVE_TEMPLATE = ('undo_template', .9)
REDO_ACTIVE_TEMPLATE = ('redo_template', .9)
RESET_CAMERA_POSITION_TEMPLATE = ('reset_camera_position_template', .9)
TOGGLE_LIGHT_TEMPLATE = ('toggle_light_template', .9)
TOGGLE_CHAT_TEMPLATE = ('toggle_chat_template', .9)

TOOLS_MENU_TEMPLATE = ('tools_menu_template', .8)
BRUSH_MENU_TEMPLATE = ('brush_menu_template', .8)
COLOUR_MENU_TEMPLATE = ('colour_menu_template', .9)
SAVE_CHANGES_CANCEL_TEMPLATE = ('save_changes_cancel_template', .8)
COLOUR_DISPLAY_TEMPLATE = ('colour_display_template', .8)

TEMPLATES = [
    CLEAR_CANVAS_TEMPLATE,
    SAVE_TO_DESKTOP_TEMPLATE,
    SAVE_CHANGES_CONTINUE_TEMPLATE,
    UNDO_ACTIVE_TEMPLATE,
    REDO_ACTIVE_TEMPLATE,
    RESET_CAMERA_POSITION_TEMPLATE,
    TOGGLE_LIGHT_TEMPLATE,
    TOGGLE_CHAT_TEMPLATE,
    TOOLS_MENU_TEMPLATE,
    BRUSH_MENU_TEMPLATE,
    COLOUR_MENU_TEMPLATE,
    SAVE_CHANGES_CANCEL_TEMPLATE,
    COLOUR_DISPLAY_TEMPLATE
]

BRUSH_SIZE_MIN = 1
BRUSH_SIZE_MAX = 32
BRUSH_SPACING_MIN = .01
BRUSH_SPACING_MAX = 1
BRUSH_OPACITY_MIN = .01
BRUSH_OPACITY_MAX = 1

COLOUR_NUMBER_OF_ROWS = 16
COLOUR_NUMBER_OF_COLUMNS = 4

class Tools(Enum):
    PAINT_BRUSH = 0
    ERASER = 1
    COLOUR_PICKER = 2

class BrushType(Enum):
    TYPE_1 = 0
    TYPE_2 = 1
    TYPE_3 = 2
    TYPE_4 = 3
    TYPE_5 = 4
    TYPE_6 = 5
    TYPE_7 = 6

class Buttons(Enum):
    CLEAR_CANVAS = 0
    SAVE_TO_DESKTOP = 1
    SAVE_CHANGES_CONTINUE = 2
    UNDO = 3
    REDO = 4
    RESET_CAMERA_POSITION = 5
    TOGGLE_LIGHT = 6
    TOGGLE_CHAT = 7
    SAVE_CHANGES_EXIT = 8
    CANCEL = 9
    COLOUR_DISPLAY = 10


class CanvasController:

    """
    Controls the canvas tools.
    """

    def __init__(self):
        """
        Init of CanvasController.
        """
        self._screen_width, self._screen_height = pyautogui.size()

        self.is_calibrated = False

        # Top Bar
        self._clear_canvas_coord = None
        self._save_to_desktop_coord = None
        self._save_changes_continue_coord = None
        self._undo_coord = None
        self._redo_coord = None
        self._reset_camera_position_coord = None
        self._toggle_light_coord = None
        self._toggle_chat_coord = None

        # Tools
        self._tools_coord = [None] * len(Tools)

        # Brush
        self._brush_types_coord = [None] * len(BrushType)
        self._brush_size_coord = None
        self._brush_spacing_coord = None
        self._brush_opacity_coord = None

        # Colour
        self._colour_coord = [[None for _ in range(COLOUR_NUMBER_OF_COLUMNS)] for _ in range(COLOUR_NUMBER_OF_ROWS)]

        self._save_changes_exit_coord = None
        self._cancel_coord = None
        self._colour_display_coord = None


    """
    PUBLIC METHODS
    """

    def update_controls_coordinates(self, controls: List[str] = [], force: bool = False) -> Tuple[List[str], List[str]]:
        """
        Update canvas controls coordinates and save them to config.json.

        Args:
            controls (List[str]): A list containing all controls that should be updated. If empty, all controls
                                  will be updated if needed.
            force (bool): Should coordinates be forcefully updated?

        Returns:
            Tuple[List[str], List[str]]: First list contain updated controls, second list contain controls that
            could not be identified.
        """
        updated, failed = [], []

        config = self._read_config()
        screenshot = self._get_screenshot(True)

        if len(controls) != 0:
            temp = []
            for item in controls:
                for control, threshold in TEMPLATES:
                    if item == control:
                        temp.append((control, threshold))
                        break
            controls = temp

        if len(controls) == 0:
            controls = controls + TEMPLATES

        for control, threshold in controls:
            if force or config['canvas_controls_template_coordinates'][control] == None:
                match = self._identify_template(self._get_template_path(control), screenshot, threshold)
                if match != None:
                    config['canvas_controls_template_coordinates'][control] = match
                    updated.append(control)
                else:
                    failed.append(control)

        self._write_config(config)

        return updated, failed


    def calibrate_controls(self) -> bool:
        """
        Calibrates different controls by setting their coordinates based on predefined templates.

        Returns:
            bool: True if calibration successful, else False.
        """
        if self.is_all_template_coordinates_set() == False:
            return False

        self._calibrate_top_bar_controls()
        self._calibrate_tools_controls()
        self._calibrate_brush_controls()
        self._calibrate_colour_controls()
        self._calibrate_save_changes_cancel_and_colour_display_controls()

        self.is_calibrated = True
        return True


    def is_all_template_coordinates_set(self) -> bool:
        """
        Check to see if all canvas controls template coordinates are set.

        Returns:
            bool: True if all are set, else False.
        """
        config = self._read_config()

        for control, coordinates in config['canvas_controls_template_coordinates'].items():
            if coordinates == None:
                return False

        return True


    def click_button(self, button: Buttons) -> bool:
        """
        Performs a click action on a specific button within the application interface.

        Args:
            button (Buttons): An enumeration representing the button to be clicked.

        Returns:
            bool: True if the action was successful, False otherwise.
        """
        if not self.is_calibrated:
            return False

        x, y = None, None
        if button.value == Buttons.CLEAR_CANVAS.value:
            x, y = self._clear_canvas_coord
        elif button.value == Buttons.SAVE_TO_DESKTOP.value:
            x, y = self._save_to_desktop_coord
        elif button.value == Buttons.SAVE_CHANGES_CONTINUE.value:
            x, y = self._save_changes_continue_coord
        elif button.value == Buttons.UNDO.value:
            x, y = self._undo_coord
        elif button.value == Buttons.REDO.value:
            x, y = self._redo_coord
        elif button.value == Buttons.RESET_CAMERA_POSITION.value:
            x, y = self._reset_camera_position_coord
        elif button.value == Buttons.TOGGLE_LIGHT.value:
            x, y = self._toggle_light_coord
        elif button.value == Buttons.TOGGLE_CHAT.value:
            x, y = self._toggle_chat_coord
        elif button.value == Buttons.SAVE_CHANGES_EXIT.value:
            x, y = self._save_changes_exit_coord
        elif button.value == Buttons.CANCEL.value:
            x, y = self._cancel_coord
        elif button.value == Buttons.COLOUR_DISPLAY.value:
            x, y = self._colour_display_coord

        if x == None or y == None:
            return False

        pyautogui.click(x=x, y=y)
        time.sleep(CANVAS_CONTROLS_TIMEOUT_S)
        pyautogui.click(x=x, y=y)

        return True


    def click_tools(self, tool: Tools) -> bool:
        """
        Click on a tool.

        Args:
            tool (Tools): The tool to click on.

        Returns:
            bool: True if successful, else False.
        """
        if not self.is_calibrated:
            return False

        x, y = self._tools_coord[tool.value]
        pyautogui.click(x=x, y=y)
        time.sleep(CANVAS_CONTROLS_TIMEOUT_S)
        pyautogui.click(x=x, y=y)

        return True


    def click_brush_type(self, brush_type: BrushType) -> bool:
        """
        Click on a brush type.

        Args:
            brush_type (BrushType): The brush type to click.

        Returns:
            bool: True if successful, else False.
        """
        if not self.is_calibrated:
            return False

        x, y = self._brush_types_coord[brush_type.value]
        pyautogui.click(x=x, y=y)
        time.sleep(CANVAS_CONTROLS_TIMEOUT_S)
        pyautogui.click(x=x, y=y)

        return True


    def set_brush_size(self, size: float) -> bool:
        """
        Sets the size of the brush used within the application.

        Args:
            size (float): The desired size of the brush.

        Returns:
            bool: True if the brush size is successfully set within the acceptable range, False otherwise.

        """
        if not self.is_calibrated:
            return False

        if size < BRUSH_SIZE_MIN or size > BRUSH_SIZE_MAX:
            return False

        size = round(size, 2)

        x, y = self._brush_size_coord
        pyautogui.click(x=x, y=y)
        time.sleep(CANVAS_CONTROLS_TIMEOUT_S)
        pyautogui.write(str(size))

        return True


    def set_brush_spacing(self, spacing: float) -> bool:
        """
        Sets the spacing of the brush used within the application.

        Args:
            spacing (float): The desired spacing of the brush.

        Returns:
            bool: True if the brush spacing is successfully set within the acceptable range, False otherwise.

        """
        if not self.is_calibrated:
            return False

        if spacing < BRUSH_SPACING_MIN or spacing > BRUSH_SPACING_MAX:
            return False

        spacing = round(spacing, 2)

        x, y = self._brush_spacing_coord
        pyautogui.click(x=x, y=y)
        time.sleep(CANVAS_CONTROLS_TIMEOUT_S)
        pyautogui.write(str(spacing))

        return True


    def set_brush_opacity(self, opacity: float) -> bool:
        """
        Sets the opacity of the brush used within the application.

        Args:
            opacity (float): The desired opacity of the brush.

        Returns:
            bool: True if the brush opacity is successfully set within the acceptable range, False otherwise.

        """
        if not self.is_calibrated:
            return False

        if opacity < BRUSH_OPACITY_MIN or opacity > BRUSH_OPACITY_MAX:
            return False

        opacity = round(opacity, 2)

        x, y = self._brush_opacity_coord
        pyautogui.click(x=x, y=y)
        time.sleep(CANVAS_CONTROLS_TIMEOUT_S)
        pyautogui.write(str(opacity))

        return True


    def click_colour(self, row: int, column: int) -> bool:
        """
        Click on a color within a grid of colors on the application interface.

        Args:
            row (int): The row index of the color in the grid.
            column (int): The column index of the color in the grid.

        Returns:
            bool: True if the click action is successfully performed on the specified color, False otherwise.
        """
        if not self.is_calibrated:
            return False

        if row < 0 or row >= COLOUR_NUMBER_OF_ROWS:
            return False
        if column < 0 or column >= COLOUR_NUMBER_OF_COLUMNS:
            return False

        x, y = self._colour_coord[row][column]
        pyautogui.click(x=x, y=y)

        return True


    def get_pixel_rgb(self, x: int, y: int, screenshot: np.ndarray = None) -> Tuple[int, int, int]:
        """
        Retrieve the RGB value of a pixel at the specified coordinates.

        Args:
            x (int): X-coordinate of the pixel.
            y (int): Y-coordinate of the pixel.
            screenshot (np.ndarray): Screenshot to get the RGB from.

        Returns:
            Tuple[int, int, int]: RGB value of the pixel at (x, y).
        """
        if screenshot is None:
            screenshot = self._get_screenshot(False)
        return screenshot[y, x].tolist()


    def update_calibrate_colours(self) -> bool:
        """
        Update and calibrate color settings. Press ESC to abort calibration.

        Returns:
            bool: True if calibration is successful, False otherwise.
        """
        if not self.is_calibrated:
            return False

        def on_key_press(event):
            nonlocal stop_calibration
            if event.name == 'esc':
                stop_calibration = True

        stop_calibration = False
        keyboard.on_press(on_key_press)

        colours_file = self._read_colours_file()
        config = self._read_config()
        sleep_time_s = config['colour_settings']['calibration_timeout_s']

        self.click_tools(Tools.PAINT_BRUSH)
        self.click_brush_type(BrushType.TYPE_3)
        self.set_brush_size(BRUSH_SIZE_MAX)
        time.sleep(CANVAS_CONTROLS_TIMEOUT_S)

        colours = []
        number_of_opacity_jumps = config['colour_settings']['number_of_opacity_jumps_calibration']
        opacity_jump_length = config['colour_settings']['opacity_jump_length_calibration']
        current_opacity = 1

        # Start with highest opacity and then go downwards
        for i in range(number_of_opacity_jumps):
            self.set_brush_opacity(current_opacity)
            time.sleep(CANVAS_CONTROLS_TIMEOUT_S)

            for i in range(COLOUR_NUMBER_OF_ROWS):
                for j in range(COLOUR_NUMBER_OF_COLUMNS):
                    if stop_calibration:
                        keyboard.unhook_all()
                        return False

                    self.click_colour(i, j)
                    time.sleep(sleep_time_s)

                    x1, y1, x2, y2 = config['canvas_controls_template_coordinates']['colour_display_template']
                    screenshot = self._get_screenshot_box(x1, y1, x2, y2, False)
                    colour = self.get_pixel_rgb((x2 - x1) // 2, (y2 - y1) // 2, screenshot)
                    colours.append(colour)
                    time.sleep(sleep_time_s)

            current_opacity = round(current_opacity - opacity_jump_length, 2)

        colours_file['colours'] = colours

        self._write_colours_file(colours_file)

        keyboard.unhook_all()
        return True


    def reset_colours_to_default(self):
        """
        Reset the colours in colours.json to default colours.
        """
        colours = self._read_colours_file()
        colours['colours'] = colours['default_colours']
        self._write_colours_file(colours)



    """
    PRIVATE METHODS
    """

    def _read_config(self) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Read the config.

        Returns:
            (Dict[str, Dict[str, Optional[str]]]): The config.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, '..', '..', 'config.json')

        config = None
        with open(config_path, 'r') as f:
            config = json.load(f)

        return config


    def _write_config(self, config: Dict[str, Dict[str, Optional[str]]]):
        """
        Write the config.

        Args:
            config (Dict[str, Dict[str, Optional[str]]]): The config.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, '..', '..', 'config.json')

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)


    def _read_colours_file(self) -> Dict[str, List[Tuple[int, int, int]]]:
        """
        Read the colours file.

        Returns:
            (Dict[str, List[Tuple[int, int, int]]]): The colours file.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        colours_path = os.path.join(current_dir, '..', '..', 'colours.json')

        colours = None
        with open(colours_path, 'r') as f:
            colours = json.load(f)

        return colours


    def _write_colours_file(self, colours: Dict[str, List[Tuple[int, int, int]]]):
        """
        Write the colours file.

        Args:
            colours (Dict[str, List[Tuple[int, int, int]]]): The colours file.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        colours_path = os.path.join(current_dir, '..', '..', 'colours.json')

        with open(colours_path, 'w') as f:
            json.dump(colours, f, indent=4)


    def _get_template_path(self, template: str) -> str:
        """
        Get the complete path of a template image.

        Args:
            template (str): The template name.

        Returns:
            str: The complete path to the template image.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, '..', '..', 'templates', f'{template}.png')
        return template_path


    def _identify_template(self, template_path: str, screenshot: np.ndarray,
                           threshold: float = .8) -> Optional[Tuple[int, int, int, int]]:
        """
        Identify the template in the screenshot and return coordinates of the first match.

        Args:
            template_path (str): The path of the template image.
            screenshot (np.ndarray): A numpy array of the screenshot.
            threshold (float): Value between 0 - 1, representing the similarity score.

        Returns:
            Optional[Tuple[int, int, int, int]]: None if no match was found, else coordinates for top left and
            bottom right.
        """
        # Read the template image and convert to grayscale
        template = cv2.imread(template_path)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Get the dimensions of the template image
        width, height = template_gray.shape[::-1]

        # Perform template matching
        result = cv2.matchTemplate(screenshot, template_gray, cv2.TM_CCOEFF_NORMED)

        # Get locations with a match above the threshold
        locations = np.where(result >= threshold)

        # If no matches found, return None
        if len(locations[0]) == 0:
            return None

        # Get coordinates of the first match
        point = (locations[1][0], locations[0][0])  # Taking the first match coordinates
        coordinates = (point[0], point[1], point[0] + width, point[1] + height)

        # Convert NumPy int64 to Python int
        coordinates = tuple(int(coord) for coord in coordinates)

        return coordinates


    def _get_screenshot(self, gray: bool = True) -> np.ndarray:
        """
        Take a screenshot and return it.

        Args:
            gray (bool): Should the screenshot be gray?

        Returns:
            np.ndarray: Containing the screenshot.
        """
        # Take a screenshot
        screenshot = np.array(ImageGrab.grab(bbox=(0, 0, self._screen_width, self._screen_height)))

        if gray:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        return screenshot


    def _get_screenshot_box(self, x1: int, y1: int, x2: int, y2: int, gray: bool = True) -> np.ndarray:
        """
        Take a screenshot of the defined region specified by the bounding box coordinates (x1, y1, x2, y2)
        and return it.

        Args:
            x1, y1 (int): Coordinates of the top-left corner.
            x2, y2 (int): Coordinates of the bottom-right corner.
            gray (bool): Should the screenshot be gray?

        Returns:
            np.ndarray: Containing the screenshot of the defined region.
        """
        # Take a screenshot of the defined region
        screenshot = np.array(ImageGrab.grab(bbox=(x1, y1, x2, y2)))

        if gray:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        return screenshot


    def _get_center_coordinate(self, x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
        """
        Calculate the center coordinate given two points: (x1, y1) (top-left corner)
        and (x2, y2) (bottom-right corner).

        Args:
            x1, y1 (int): Coordinates of the top-left corner.
            x2, y2 (int): Coordinates of the bottom-right corner.

        Returns:
            Tuple[int, int]: Center coordinates (center_x, center_y).
        """
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return center_x, center_y


    def _get_coordinate(self, x1: int, y1: int, x2: int, y2: int, x_corr: float, y_corr: float) -> Tuple[int, int]:
        """
        Calculate the adjusted coordinate based on specified correction factors.

        This function calculates a new coordinate pair based on the provided top-left corner (x1, y1) and
        bottom-right corner (x2, y2) coordinates, applying correction factors x_corr and y_corr.

        Args:
            x1, y1 (int): Coordinates of the top-left corner.
            x2, y2 (int): Coordinates of the bottom-right corner.
            x_corr (float): Correction factor for the X-coordinate.
            y_corr (float): Correction factor for the Y-coordinate.

        Returns:
            Tuple[int, int]: Adjusted coordinates (x, y) based on corrections.
        """
        width = x2 - x1
        height = y2 - y1
        x = x1 + int(width * x_corr)
        y = y1 + int(height * y_corr)
        return x, y


    def _calibrate_top_bar_controls(self):
        """
        Calibrate top bar controls.
        """
        config = self._read_config()
        template_coords = config['canvas_controls_template_coordinates']

        x1, y1, x2, y2 = template_coords['clear_canvas_template']
        self._clear_canvas_coord = self._get_center_coordinate(x1, y1, x2, y2)

        x1, y1, x2, y2 = template_coords['save_to_desktop_template']
        self._save_to_desktop_coord = self._get_center_coordinate(x1, y1, x2, y2)

        x1, y1, x2, y2 = template_coords['save_changes_continue_template']
        self._save_changes_continue_coord = self._get_center_coordinate(x1, y1, x2, y2)

        x1, y1, x2, y2 = template_coords['undo_template']
        self._undo_coord = self._get_center_coordinate(x1, y1, x2, y2)

        x1, y1, x2, y2 = template_coords['redo_template']
        self._redo_coord = self._get_center_coordinate(x1, y1, x2, y2)

        x1, y1, x2, y2 = template_coords['reset_camera_position_template']
        self._reset_camera_position_coord = self._get_center_coordinate(x1, y1, x2, y2)

        x1, y1, x2, y2 = template_coords['toggle_light_template']
        self._toggle_light_coord = self._get_center_coordinate(x1, y1, x2, y2)

        x1, y1, x2, y2 = template_coords['toggle_chat_template']
        self._toggle_chat_coord = self._get_center_coordinate(x1, y1, x2, y2)


    def _calibrate_tools_controls(self):
        """
        Calibrate tools controls.
        """
        config = self._read_config()
        x1, y1, x2, y2 = config['canvas_controls_template_coordinates']['tools_menu_template']

        y_corr = 0.70491

        x_corr0 = 0.36467
        x_corr1 = 0.50142
        x_corr2 = 0.63817

        self._tools_coord[Tools.PAINT_BRUSH.value] = self._get_coordinate(x1, y1, x2, y2, x_corr0, y_corr)
        self._tools_coord[Tools.ERASER.value] = self._get_coordinate(x1, y1, x2, y2, x_corr1, y_corr)
        self._tools_coord[Tools.COLOUR_PICKER.value] = self._get_coordinate(x1, y1, x2, y2, x_corr2, y_corr)


    def _calibrate_brush_controls(self):
        """
        Calibrate brush controls.
        """
        config = self._read_config()
        x1, y1, x2, y2 = config['canvas_controls_template_coordinates']['brush_menu_template']

        y_corr = 0.34939

        x_corr0 = 0.10541
        x_corr1 = 0.24216
        x_corr2 = 0.37606
        x_corr3 = 0.51282
        x_corr4 = 0.64957
        x_corr5 = 0.78917
        x_corr6 = 0.92307

        self._brush_types_coord[BrushType.TYPE_1.value] = self._get_coordinate(x1, y1, x2, y2, x_corr0, y_corr)
        self._brush_types_coord[BrushType.TYPE_2.value] = self._get_coordinate(x1, y1, x2, y2, x_corr1, y_corr)
        self._brush_types_coord[BrushType.TYPE_3.value] = self._get_coordinate(x1, y1, x2, y2, x_corr2, y_corr)
        self._brush_types_coord[BrushType.TYPE_4.value] = self._get_coordinate(x1, y1, x2, y2, x_corr3, y_corr)
        self._brush_types_coord[BrushType.TYPE_5.value] = self._get_coordinate(x1, y1, x2, y2, x_corr4, y_corr)
        self._brush_types_coord[BrushType.TYPE_6.value] = self._get_coordinate(x1, y1, x2, y2, x_corr5, y_corr)
        self._brush_types_coord[BrushType.TYPE_7.value] = self._get_coordinate(x1, y1, x2, y2, x_corr6, y_corr)

        x_corr = 0.88034

        y_corr0 = 0.55823
        y_corr1 = 0.72289
        y_corr2 = 0.89156

        self._brush_size_coord = self._get_coordinate(x1, y1, x2, y2, x_corr, y_corr0)
        self._brush_spacing_coord = self._get_coordinate(x1, y1, x2, y2, x_corr, y_corr1)
        self._brush_opacity_coord = self._get_coordinate(x1, y1, x2, y2, x_corr, y_corr2)


    def _calibrate_colour_controls(self):
        """
        Calibrate colour controls.
        """
        config = self._read_config()
        x1, y1, x2, y2 = config['canvas_controls_template_coordinates']['colour_menu_template']

        x_corr = [
            0.14814,
            0.38461,
            0.61823,
            0.85185
        ]

        y_corr = [
            0.14734,
            0.20235,
            0.25540,
            0.30844,
            0.36149,
            0.41453,
            0.46954,
            0.52259,
            0.57563,
            0.62868,
            0.68172,
            0.73673,
            0.78978,
            0.84282,
            0.89587,
            0.94891
        ]

        for i in range(COLOUR_NUMBER_OF_ROWS):
            for j in range(COLOUR_NUMBER_OF_COLUMNS):
                self._colour_coord[i][j] = self._get_coordinate(x1, y1, x2, y2, x_corr[j], y_corr[i])


    def _calibrate_save_changes_cancel_and_colour_display_controls(self):
        """
        Calibrate save changes cancel and colour display controls.
        """
        config = self._read_config()
        x1, y1, x2, y2 = config['canvas_controls_template_coordinates']['save_changes_cancel_template']

        x_corr = 0.50000

        y_corr0 = 0.22413
        y_corr1 = 0.77586

        self._save_changes_exit_coord = self._get_coordinate(x1, y1, x2, y2, x_corr, y_corr0)
        self._cancel_coord = self._get_coordinate(x1, y1, x2, y2, x_corr, y_corr1)


        x1, y1, x2, y2 = config['canvas_controls_template_coordinates']['colour_display_template']
        self._colour_display_coord = self._get_center_coordinate(x1, y1, x2, y2)