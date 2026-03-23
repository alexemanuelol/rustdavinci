#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

NAME = "RustPicasso"
VERSION = "0.1"
DESCRIPTION = "Automatic Sign Art Painter for the game Rust by Facepunch"
AUTHOR = "Vance Strazzeri"
EMAIL = "init.d.httpd@gmail.com"
URL = "https://github.com/vstrazz/RustPicasso"
REQUIRED = [
    "Pillow==11.3.0",
    "PyAutoGUI==0.9.54",
    "pypiwin32==223; sys_platform == 'win32'",
    "colorama==0.4.6",
    "termcolor==3.1.0",
    "pynput==1.8.1",
    "numpy==2.0.2",
    "opencv-python==4.13.0.92",
    "PyQt5==5.15.11",
]

with open("README.md") as file:
    readme = file.read()

with open("LICENSE") as file:
    license = file.read()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=readme,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    license=license,
    install_requires=REQUIRED,
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
)
