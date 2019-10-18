# TODO

## Coding
- Make it possible to abort capturing by clicking the close button when prompted to capture
- Fix the progress bar. Perhaps check the amount of painted pixels and from that decide what to show on the progress bar?
- Create build script to make it easy to create windows executable.
- Fix the settings about tab, add more information to it.
- Add help tags to all the modules in the gui?
- Add picture help when capturing areas?
- Setup CI travis yml


## Testing
- Test different settings for paintings (click_delay, line_delay etc...). See what settings is the most optimal.
- Investigate how the application work together with the rust application. Will Rust minimize when switched to rustdavinci? Make it possible to set rustdavinci on top while painting? etc...
- Check accuracy for the estimation of time.


## Other
- Get Facepunch and EAC to recognize this application and what it is capable of doing. Contact them.
- Create a howto/ tutorial guide.
- Add more to FAQ
- Investigate what is the best way to create a windows executable.
- Check what more settings would be appropriate.
- Investigate what is the most important things to show in the textedit window.


# Potentially big todos
- Try to lower the calculation time for statistics. At the moment it is very long...
- Investigate how to handle setting the pause, skip and exit button. As of now, the values are hardcoded (F10, F11, ESC)
- Change the way to append colors to skip. Perhaps show the actual colors from the palette?


# Known errors
