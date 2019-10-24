import subprocess

subprocess.run("pyuic5 settingsui.ui -o settingsui.py")

s = open("settingsui.py").read()
s = s.replace("import icons_rc", "import ui.resources.icons_rc")
f = open("settingsui.py", "w")
f.write(s)
f.close()
