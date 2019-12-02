import subprocess
import os
import shutil
import glob

# Requires pyinstaller


def remove_content(folder_path):
    """ Remove content of a fiven folder """
    for f in os.listdir(folder_path):
        file_path = os.path.join(folder_path, f)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def copy_content(src, dst, symlinks=False, ignore=None):
    """ Copy content of a given folder to a destination folder """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def move_content(srcDir, dstDir):
    """ Move content from a given folder to a destination folder """
    for filePath in glob.glob(srcDir + '\*'):
        shutil.move(filePath, dstDir);


def main():
    # Build with pyinstaller
    subprocess.run('pyinstaller --name="RustDaVinci" --icon=./../images/RustDaVinci-icon.ico app.pyw')

    # Create executable folder if not exist, else remove content of executable folder
    folder_name = "executable"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    else:
        remove_content(folder_name)

    # move build from dist to executable folder
    move_content("dist/", folder_name)

    # move opencv_template folder to executable folder
    os.mkdir("executable/RustDaVinci/opencv_template")
    copy_content("opencv_template/", "executable/RustDaVinci/opencv_template/")

    # Remove build directories
    remove_content("build/")
    os.rmdir("build")
    os.rmdir("dist")
    os.remove("RustDaVinci.spec")



if __name__ == "__main__":
    main()
