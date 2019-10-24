# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'colorsui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ColorsUI(object):
    def setupUi(self, ColorsUI):
        ColorsUI.setObjectName("ColorsUI")
        ColorsUI.resize(200, 350)
        ColorsUI.setMinimumSize(QtCore.QSize(200, 350))
        ColorsUI.setMaximumSize(QtCore.QSize(200, 350))
        self.colors_ListWidget = QtWidgets.QListWidget(ColorsUI)
        self.colors_ListWidget.setGeometry(QtCore.QRect(10, 40, 181, 301))
        self.colors_ListWidget.setObjectName("colors_ListWidget")
        self.label = QtWidgets.QLabel(ColorsUI)
        self.label.setGeometry(QtCore.QRect(16, 12, 141, 21))
        self.label.setObjectName("label")

        self.retranslateUi(ColorsUI)
        QtCore.QMetaObject.connectSlotsByName(ColorsUI)

    def retranslateUi(self, ColorsUI):
        _translate = QtCore.QCoreApplication.translate
        ColorsUI.setWindowTitle(_translate("ColorsUI", "Dialog"))
        self.label.setText(_translate("ColorsUI", "Available colors:"))
