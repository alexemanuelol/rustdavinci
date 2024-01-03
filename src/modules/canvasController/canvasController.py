#!/usr/bin/env python3

import cv2
import json
import numpy as np
import os
import pyautogui
import time

from PIL import ImageGrab
from enum import Enum
from typing import Optional, Tuple, List, Dict

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
COLOUR_MENU_TEMPLATE = ('colour_menu_template', .8)
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


class CanvasController:

    """
    Controls the canvas tools.
    """

    def __init__(self):
        """
        Init of CanvasController.
        """
        self._screen_width = 0
        self._screen_height = 0

        self._is_calibrated = False

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

        self._save_changes_coord = None
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


    """
    PRIVATE METHODS
    """

    def _read_config(self) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Get the config.

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
        Set the config.

        Args:
            config (Dict[str, Dict[str, Optional[str]]]): The config.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, '..', '..', 'config.json')

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)


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
        # Get screen width/height
        self._screen_width, self._screen_height = pyautogui.size()

        # Take a screenshot
        screenshot = np.array(ImageGrab.grab(bbox=(0, 0, self._screen_width, self._screen_height)))

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

        self._save_changes_coord = self._get_coordinate(x1, y1, x2, y2, x_corr, y_corr0)
        self._cancel_coord = self._get_coordinate(x1, y1, x2, y2, x_corr, y_corr1)


        x1, y1, x2, y2 = config['canvas_controls_template_coordinates']['colour_display_template']
        self._colour_display_coord = self._get_center_coordinate(x1, y1, x2, y2)