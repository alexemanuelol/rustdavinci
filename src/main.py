#!/usr/bin/env python3

from modules.canvasController.canvasController import CanvasController

def main():
    canvasController = CanvasController()
    result = canvasController.update_controls_coordinates()
    print(result)

if __name__ == '__main__':
    main()