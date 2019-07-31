![RustDaVinci logo](images/RustDaVinci-logo-2.png)

An automatic sign painter for Rust Facepunch


## TODO

- Get Facepunch and EAC to recognize this application and what it is capable of doing.

### New features

- Create a howto guide
- Set the window topmost (as an overlay to Rust) then remove topmost when paint is done
- Automatically update the painting when switching colors
- Create a FAQ file
- Play around with the hidden colors (Needs to be SUPER accurate for it to work)
- Create a config file


### Optimization

- Optimize area capturing, find another way to capture the tool area and painting area.
- Maybe tweak the image generation, less pixels?
- Optimize the estimate time part
- Right now we're showing which is fastest, with lines or without, depending on that choose differently, if pixels only is faster, use that.


### Test
- Test the line painting speed, is it satisfactory? Does everything get painted? Missing pixels?
- Test the min_pixels_for_line variable, which value is the most optimal? atm 7


## Known errors

- Sometimes a line is painted across other colors... Needs investigation.


## Variables for the future config file
- pag_delay, pag_line_delay?
- min_pixels_for_line
- which rust palette that should be used
- quality of the image (needs to be investigated for PIL Image)
- window as overlay always on top?
- location for tool area, perhaps (None, None), (None, None) if it's not defined and add the values when define for the first time.
- Show preview of image or not?
- Set the default background, default white
- Remember the tool area coordinates when it's been defined in the application
- Save the image when it's done
- Update the canvas while it's painting
- draw lines?
- double-click?
- 
