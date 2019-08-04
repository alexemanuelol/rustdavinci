# Helpful things for the project:

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
