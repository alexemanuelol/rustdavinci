#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QMovie, QPainter, QFont
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton


class CaptureAreaDialog(QDialog):

    def __init__(self, parent=None, dialog=0):
        """ init CaptureAreaDialog module """
        super(CaptureAreaDialog, self).__init__(parent)
        self.setModal(True)
        self.resize(QSize(600, 430))
        self.setFixedSize(QSize(600, 430))

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("Times", 10, QFont.Bold))
        self.label.setGeometry(20, 357, 390, 53)

        if dialog == 0:
            self.label.setText( "Manually capture the area by drag & drop the top left " +
                                "corner of the canvas to the bottom right corner.")
            self.movie = QMovie(":/gifs/capture_canvas.gif")
        else:
            self.label.setText( "Manually capture the area by drag & drop the top left " +
                                "corner of the painting controls area to the bottom right corner.")
            self.movie = QMovie(":/gifs/capture_ctrl_area.gif")

        self.movie.frameChanged.connect(self.repaint)
        self.movie.start()

        self.ok_button = QPushButton(self)
        self.ok_button.setText("OK")
        self.ok_button.setGeometry(430, 357, 150, 53)
        self.ok_button.clicked.connect(self.ok_clicked)


    def paintEvent(self, event):
        """ Update the gif """
        currentFrame = self.movie.currentPixmap()
        frameRect = currentFrame.rect()
        if frameRect.intersects(event.rect()):
            painter = QPainter(self)
            painter.drawPixmap(frameRect.left(), frameRect.top(), currentFrame)


    def ok_clicked(self):
        """ Ok has been clicked, return 1 """
        self.done(1)
