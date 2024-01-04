#!/usr/bin/env python3

from modules.canvasController.canvasController import Tools, BrushType, CanvasController

def main():
    canvasController = CanvasController()
    updated, failed = canvasController.update_controls_coordinates()
    if len(failed) == 0:
        if canvasController.calibrate_controls():
            print('SUCCESS')


if __name__ == '__main__':
    main()