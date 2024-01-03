#!/usr/bin/env python3

import cv2
import json
import numpy as np
import os
import pyautogui

from PIL import ImageGrab
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


class CanvasController:

    """
    Controls the canvas tools.
    """

    def __init__(self):
        """
        """
        self._screen_width = 0
        self._screen_height = 0


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
        height, width = template_gray.shape[::-1]

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