# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'click_colorui.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Click_ColorUI(object):
    def setupUi(self, Click_ColorUI):
        Click_ColorUI.setObjectName("Click_ColorUI")
        Click_ColorUI.resize(200, 200)
        Click_ColorUI.setMinimumSize(QtCore.QSize(200, 200))
        Click_ColorUI.setMaximumSize(QtCore.QSize(200, 200))
        self.colors_ListWidget = QtWidgets.QListWidget(Click_ColorUI)
        self.colors_ListWidget.setGeometry(QtCore.QRect(10, 40, 181, 110))
        self.colors_ListWidget.setObjectName("colors_ListWidget")
        self.label = QtWidgets.QLabel(Click_ColorUI)
        self.label.setGeometry(QtCore.QRect(16, 12, 141, 21))
        self.label.setObjectName("label")
        self.click_color_PushButton = QtWidgets.QPushButton(Click_ColorUI)
        self.click_color_PushButton.setGeometry(QtCore.QRect(10, 160, 181, 31))
        self.click_color_PushButton.setObjectName("click_color_PushButton")

        self.retranslateUi(Click_ColorUI)
        QtCore.QMetaObject.connectSlotsByName(Click_ColorUI)

    def retranslateUi(self, Click_ColorUI):
        _translate = QtCore.QCoreApplication.translate
        Click_ColorUI.setWindowTitle(_translate("Click_ColorUI", "Dialog"))
        self.colors_ListWidget.setToolTip(_translate("Click_ColorUI", "A list of all the available colors"))
        self.label.setText(_translate("Click_ColorUI", "Available colors:"))
        self.click_color_PushButton.setToolTip(_translate("Click_ColorUI", "This will make the application click on the selected color in the in-game palette"))
        self.click_color_PushButton.setText(_translate("Click_ColorUI", "Click Color"))
