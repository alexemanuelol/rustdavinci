#!/usr/bin/env python3

from modules.canvasController.canvasController import Tools, BrushType, CanvasController
from modules.imageController.imageController import ImageController

def main():
    canvasController = CanvasController()
    if canvasController.select_canvas_painting_area():
        x, y, w, h = canvasController.get_canvas_painting_area()
        canvasController.display_area(x, y, w, h)


    #updated, failed = canvasController.update_controls_coordinates()
    #if len(failed) == 0:
    #    if canvasController.calibrate_controls():
    #        canvasController.update_calibrate_colours()
    #        print('SUCCESS')
    #imageController = ImageController()
    ##path = 'https://www.looper.com/img/gallery/gollums-entire-backstory-explained/intro-1584137078.jpg'
    #path = 'https://ew.com/thmb/qqofw2-fYfIwaXB2eGSA3xbB7h4=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/image-tout-5741441aeb5f4a46856513f92e182914.jpg'
    ##result = imageController.load_grayscale_colours()
    ##result = imageController.load_simple_grayscale_colours()
    ##result = imageController.load_black_and_white_colours()
    #result = imageController.load_default_colours()
    ##result = imageController.load_third_column_colours()
    #if result:
    #    result = imageController.load_image(path)
    #    #imageController.find_optimal_colours()
    #    if result:
    #        #result = imageController.image_convert_colours()
    #        result = imageController.image_convert_dither_colours(8)
    #        if result:
    #            imageController.image_resize_converted(100, 100)
    #            imageController.original_image.show()
    #            imageController.converted_image.show()
    #            imageController.resized_image.show()


if __name__ == '__main__':
    main()