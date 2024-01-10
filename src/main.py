#!/usr/bin/env python3

from modules.canvasController.canvasController import Tools, BrushType, CanvasController
from modules.imageController.imageController import ImageController

def main():
    #canvasController = CanvasController()
    #updated, failed = canvasController.update_controls_coordinates()
    #if len(failed) == 0:
    #    if canvasController.calibrate_controls():
    #        canvasController.update_calibrate_colours()
    #        print('SUCCESS')
    imageController = ImageController()
    path = 'https://www.looper.com/img/gallery/gollums-entire-backstory-explained/intro-1584137078.jpg'
    result = imageController.load_image(path)
    if result:
        res = imageController.image_convert_colours()
        if res:
            imageController.original_image.show()
            imageController.converted_image.show()


if __name__ == '__main__':
    main()