#!/usr/bin/env python3

import copy
import json
import os
import requests

from PIL import Image, ImageOps
from io import BytesIO
from typing import Tuple, Optional, Dict

MAX_NUMBER_OF_ALL_COLOURS = 6400
MAX_NUMBER_OF_COLOURS = 256
COLOURS_PER_OPACITY = 64
BRUSH_OPACITY_MIN = .01
BRUSH_OPACITY_MAX = 1
BRUSH_OPACITY_STEP = .01
NUMBER_OF_BRUSH_OPACITIES = 100

class ImageController:

    """
    Controls the colour conversion and resize of images.
    """

    def __init__(self):
        """
        Init of ImageController.
        """
        self.all_colours = None
        self.colours = None

        self.original_image = None
        self.converted_image = None
        self.resized_image = None

        self.load_colours_from_config()


    """
    PUBLIC METHODS
    """

    def load_colours_from_config(self) -> bool:
        """
        Load colours from config.

        Returns:
            bool: True if successful, else False.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        colours_path = os.path.join(current_dir, '..', '..', 'colours.json')

        colours = None
        with open(colours_path, 'r') as f:
            colours = json.load(f)

        if len(colours['colours']) != MAX_NUMBER_OF_ALL_COLOURS:
            return False

        self.all_colours = [tuple(rgb) for rgb in colours['colours']]

        return True


    def get_colour_index(self, colour: Tuple[int, int, int]) -> int:
        """
        Get the index of colour in self.all_colours.

        Args:
            colour (Tuple[int, int, int]): The colour to find,
            represented as a tuple of three integers (r, g, b).

        Returns:
            int: Index of the colour in self.all_colours. Returns -1 if self.all_colours is empty or None,
            and returns -2 if the colour is not found in self.all_colours.
        """
        if self.all_colours is None or len(self.all_colours) == 0:
            return -1

        for i, c in enumerate(self.all_colours):
            if all(a == b for a, b in zip(c, colour)):
                return i

        return -2


    def get_palette_index(self, index: int) -> int:
        """
        Get the palette index based on all_colours index.

        Args:
            index (int): The all_colours index.

        Returns:
            int: The palette index. Returns -1 if index is lower than 0 or higher than MAX_NUMBER_OF_ALL_COLOURS.
        """
        if index < 0 or index >= MAX_NUMBER_OF_ALL_COLOURS:
            return -1

        return index % COLOURS_PER_OPACITY


    def get_opacity_from_colour_index(self, index: int) -> float:
        """
        Get the opacity value based on the provided colour index.

        Args:
            index (int): The colour index.

        Returns:
            float: The opacity value for the given index. Returns -1 if index is lower than 0 or higher than
            MAX_NUMBER_OF_ALL_COLOURS and returns -2 if opacity is lower than BRUSH_OPACITY_MIN.
        """
        if index < 0 or index >= MAX_NUMBER_OF_ALL_COLOURS:
            return -1

        opacity_index = index // COLOURS_PER_OPACITY
        opacity = BRUSH_OPACITY_MAX - (BRUSH_OPACITY_STEP * opacity_index)
        if opacity < BRUSH_OPACITY_MIN:
            return -2

        return opacity


    def get_start_index_from_opacity(self, opacity: float) -> int:
        """
        Get the start index based on the provided opacity value.

        Args:
            opacity (float): The opacity value.

        Returns:
            int: The start index for the given opacity. Returns -1 if opacity is lower than BRUSH_OPACITY_MIN
            or higher than BRUSH_OPACITY_MAX.
        """
        if opacity < BRUSH_OPACITY_MIN or opacity > BRUSH_OPACITY_MAX:
            return -1

        opacity_index = int((BRUSH_OPACITY_MAX - opacity) / BRUSH_OPACITY_STEP)
        return opacity_index * COLOURS_PER_OPACITY


    def load_image(self, path) -> bool:
        """
        Load an image from a local file path or a URL.

        Args:
            path (str): The file path or URL of the image to be loaded.

        Returns:
            bool: True if the image is successfully loaded, False otherwise.
        """
        try:
            if path.startswith(('http://', 'https://')):
                response = requests.get(path)
                if response.status_code == 200:
                    image_data = BytesIO(response.content)
                    self.original_image = Image.open(image_data)
                else:
                    return False
            else:
                self.original_image = Image.open(path)
        except Exception as e:
            return False

        self.converted_image = None
        self.resized_image = None
        return True


    def image_convert_map_colours(self) -> bool:
        """
        Convert the image to a colour-mapped version using a self.colours.

        Returns:
            bool: True if the image is successfully converted, False otherwise.
        """
        if self.original_image is None or self.colours is None or len(self.colours) == 0:
            return False

        image = self.original_image.convert('P', palette=Image.ADAPTIVE, colors=len(self.colours))
        palette = image.getpalette()

        for i in range(0, len(palette), 3):
            # Extract the current pixel's RGB values from the palette
            pixel_rgb = palette[i:i + 3]

            # Find the closest color in the defined colour palette
            closest_distance = float('inf')
            closest_colour = None

            for colour in self.colours:
                distance = sum((pixel_rgb[j] - colour[j]) ** 2 for j in range(3))
                if distance < closest_distance:
                    closest_distance = distance
                    closest_colour = colour

            # Replace the pixel's RGB values in the palette with the closest colour's values
            for j in range(3):
                palette[i + j] = closest_colour[j]

        image.putpalette(palette)
        self.converted_image = image

        return True


    def image_convert_dither_colours(self, dither_posterize_value: int = 8) -> bool:
        """
        Dither the image using self.colours.

        Args:
            dither_posterize_value (int): The number of bits to use for posterizing the image.
            Defaults to 8. Should be value between 1-8

        Returns:
            bool: True if the image is successfully converted, False otherwise.
        """
        if self.original_image is None or self.colours is None or len(self.colours) == 0:
            return False

        if dither_posterize_value < 1 or dither_posterize_value > 8:
            return False

        # Create a PaletteImage from the list of colors
        palette_image = Image.new('P', (1, 1))
        palette_image.putpalette([x for color in self.colours for x in color])

        # Convert the image to indexed mode using the palette
        image = ImageOps.posterize(self.original_image, dither_posterize_value)
        image = image.quantize(palette=palette_image)

        # Apply Floyd-Steinberg dithering to the quantized image
        dithered_image = image.convert('RGB').convert('P', palette=palette_image, colors=len(self.colours),
                                                      dither=Image.FLOYDSTEINBERG)

        self.converted_image = dithered_image

        return True


    def image_resize_converted(self, max_width: int, max_height: int) -> bool:
        """
        Resize the converted image to fit within specified maximum width and height.

        Args:
            max_width (int): The maximum width for the resized image.
            max_height (int): The maximum height for the resized image.

        Returns:
            bool: True if the image is successfully resized, False otherwise.
        """
        if self.original_image is None or self.converted_image is None:
            return False

        # Calculate the ratio to maintain the original aspect ratio
        width, height = self.original_image.size
        aspect_ratio = width / height

        # Calculate the new dimensions based on the maximum width and height
        new_width = min(max_width, int(max_height * aspect_ratio))
        new_height = min(max_height, int(max_width / aspect_ratio))

        # Resize the image using the thumbnail method
        self.resized_image = copy.copy(self.converted_image)
        self.resized_image.thumbnail((new_width, new_height))

        return True


    """
    COLOUR SELECTOR METHODS
    """

    def load_grayscale_colours(self) -> bool:
        """
        Loads grayscale colours.

        Returns:
            bool: True if successful else False.
        """
        if self.all_colours is None or len(self.all_colours) == 0:
            return False

        self.colours = []
        for i in range(0, NUMBER_OF_BRUSH_OPACITIES, 2):
            self.colours.append(self.all_colours[i * COLOURS_PER_OPACITY])
            self.colours.append(self.all_colours[(i * COLOURS_PER_OPACITY) + 1])
            self.colours.append(self.all_colours[(i * COLOURS_PER_OPACITY) + 2])
            self.colours.append(self.all_colours[(i * COLOURS_PER_OPACITY) + 3])

        # Remove duplicates
        unique_rgb_set = set(self.colours)
        self.colours = list(unique_rgb_set)

        return True


    def load_simple_grayscale_colours(self) -> bool:
        """
        Loads simple grayscale colours.

        Returns:
            bool: True if successful else False.
        """
        if self.all_colours is None or len(self.all_colours) == 0:
            return False

        self.colours = []
        for i in range(0, NUMBER_OF_BRUSH_OPACITIES, 20):
            self.colours.append(self.all_colours[i * COLOURS_PER_OPACITY])
            self.colours.append(self.all_colours[(i * COLOURS_PER_OPACITY) + 1])
            self.colours.append(self.all_colours[(i * COLOURS_PER_OPACITY) + 2])
            self.colours.append(self.all_colours[(i * COLOURS_PER_OPACITY) + 3])

        return True


    def load_default_colours(self) -> bool:
        """
        Load default colours.

        Returns:
            bool: True if successful else False.
        """
        if self.all_colours is None or len(self.all_colours) == 0:
            return False

        self.colours = []
        for opacity in [1, .75, .5, .25]:
            start_index = self.get_start_index_from_opacity(opacity)
            for i in range(start_index, start_index + COLOURS_PER_OPACITY):
                self.colours.append(self.all_colours[i])

        # Remove duplicates
        unique_rgb_set = set(self.colours)
        self.colours = list(unique_rgb_set)

        return True


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