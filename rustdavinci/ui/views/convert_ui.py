import subprocess

subprocess.run("pyuic5 mainui.ui -o mainui.py")

s = open("mainui.py").read()
s = s.replace("import icons_rc", "import ui.resources.icons_rc")
f = open("mainui.py", "w")
f.write(s)
f.close()
