#!/usr/bin/env python3

import json
import os
import requests

from PIL import Image
from io import BytesIO

NUMBER_OF_COLOURS = 256

class ImageController:

    """
    """

    def __init__(self):
        """
        """
        self.colours = None

        self.original_image = None
        self.converted_image = None

        self.load_colours_from_config(1,1,1,1)


    """
    PUBLIC METHODS
    """

    def load_colours_from_config(self, opacity_1, opacity_2, opacity_3, opacity_4):
        """
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        colours_path = os.path.join(current_dir, '..', '..', 'colours.json')

        colours = None
        with open(colours_path, 'r') as f:
            colours = json.load(f)

        if len(colours['colours']) == 0:
            return False

        self.colours = colours['colours']

        return True


    def load_image(self, path):
        """
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

        return True


    def image_convert_colours(self):
        """
        """
        if self.original_image == None or self.colours == None or len(self.colours) == 0:
            return False

        image = self.original_image.convert('P', palette=Image.ADAPTIVE, colors=NUMBER_OF_COLOURS)
        palette = image.getpalette()

        for i in range(0, len(palette), 3):
            # Extract the current pixel's RGB values from the palette
            pixel_rgb = palette[i:i + 3]

            # Find the closest color in the defined colour palette
            closest_distance = float('inf')
            closest_colour = None

            for colour in self.colours[:NUMBER_OF_COLOURS]:
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


    def image_resize(self):
        """
        """
        None



    """
    PRIVATE METHODS
    """