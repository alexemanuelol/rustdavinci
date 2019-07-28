# RustDaVinci

Automatic Sign Painter for Rust


## TODO

- Get Facepunch and EAC to recognize this application and what it is capable of doing.

### New features

- Create a howto guide
- Set the window topmost (as an overlay to Rust) then remove topmost when paint is done
- Automatically update the painting when switching colors
- Create a FAQ file


### Optimization

- Optimize area capturing, find another way to capture the tool area and painting area.
- Maybe tweak the image generation, less pixels?
- Optimize the estimate time part


### Test
- Test the line painting speed, is it satisfactory? Does everything get painted? Missing pixels?
- Test the min_pixels_for_line variable, which value is the most optimal? atm 7


## Known errors

- Sometimes a line is painted across other colors... Needs investigation.
