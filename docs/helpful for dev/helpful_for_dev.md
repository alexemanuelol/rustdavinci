# Helpful things for the project:

## Generate quantized images

### alt_quantize_image.py
Perhaps a middle quality quantize.. cons - it is very slow in generating the image


## The hidden palette

- Useful site: https://imgur.com/a/L7P0f

### identifyColors.py
Script that print out every single pixel from the palette onto a picture frame in-game.
NOTE: The coordinates needs to be modified to the correct placement of the control area.

![Demonstration of the what the script accomplishes](rust_palette_hidden.png)


## Identify control area automatically with opencv

### identify_tool_area.py
Script uses opencv to take a screenshot and look for the template to match somewhere (rust_palette_template.png).

![The template for the control area](rust_palette_template.png)




## Useful articles and links:

### Dithering image/ quantize
https://stackoverflow.com/questions/53477624/python-pil-image-convert-not-replacing-color-with-the-closest-palette
https://stackoverflow.com/questions/29433243/convert-image-to-specific-palette-using-pil-without-dithering
https://stackoverflow.com/questions/236692/how-do-i-convert-any-image-to-a-4-color-paletted-image-using-the-python-imaging-l

### Function for getting "primary" color for an image with defined palette
https://www.codementor.io/isaib.cicourel/image-manipulation-in-python-du1089j1u
