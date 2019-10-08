# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainUI(object):
    def setupUi(self, MainUI):
        MainUI.setObjectName("MainUI")
        MainUI.resize(240, 400)
        MainUI.setMinimumSize(QtCore.QSize(240, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/RustDaVinci-icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainUI.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainUI)
        self.centralwidget.setObjectName("centralwidget")
        self.loadImagePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.loadImagePushButton.setGeometry(QtCore.QRect(10, 10, 220, 45))
        self.loadImagePushButton.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.loadImagePushButton.setAcceptDrops(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/load_image_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadImagePushButton.setIcon(icon1)
        self.loadImagePushButton.setIconSize(QtCore.QSize(220, 45))
        self.loadImagePushButton.setCheckable(False)
        self.loadImagePushButton.setAutoDefault(False)
        self.loadImagePushButton.setDefault(False)
        self.loadImagePushButton.setFlat(True)
        self.loadImagePushButton.setObjectName("loadImagePushButton")
        self.identifyAreasPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.identifyAreasPushButton.setGeometry(QtCore.QRect(10, 60, 220, 45))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/select_area_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.identifyAreasPushButton.setIcon(icon2)
        self.identifyAreasPushButton.setIconSize(QtCore.QSize(220, 45))
        self.identifyAreasPushButton.setFlat(True)
        self.identifyAreasPushButton.setObjectName("identifyAreasPushButton")
        self.paintImagePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.paintImagePushButton.setEnabled(False)
        self.paintImagePushButton.setGeometry(QtCore.QRect(10, 110, 220, 45))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/paint_image_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.paintImagePushButton.setIcon(icon3)
        self.paintImagePushButton.setIconSize(QtCore.QSize(220, 45))
        self.paintImagePushButton.setFlat(True)
        self.paintImagePushButton.setObjectName("paintImagePushButton")
        self.settingsPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.settingsPushButton.setGeometry(QtCore.QRect(10, 160, 220, 45))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/settings_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settingsPushButton.setIcon(icon4)
        self.settingsPushButton.setIconSize(QtCore.QSize(220, 45))
        self.settingsPushButton.setFlat(True)
        self.settingsPushButton.setObjectName("settingsPushButton")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(17, 220, 201, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        MainUI.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainUI)
        self.statusbar.setObjectName("statusbar")
        MainUI.setStatusBar(self.statusbar)

        self.retranslateUi(MainUI)
        QtCore.QMetaObject.connectSlotsByName(MainUI)

    def retranslateUi(self, MainUI):
        _translate = QtCore.QCoreApplication.translate
        MainUI.setWindowTitle(_translate("MainUI", "RustDaVinci"))
        self.loadImagePushButton.setText(_translate("MainUI", "Load Image..."))
        self.identifyAreasPushButton.setText(_translate("MainUI", "Capture Control Area..."))
        self.paintImagePushButton.setText(_translate("MainUI", "Paint Image"))
        self.settingsPushButton.setText(_translate("MainUI", "Settings"))
import ui.resources.icons_rc
