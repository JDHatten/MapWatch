# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'confirm.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Confirm(object):
    def setupUi(self, Confirm):
        Confirm.setObjectName("Confirm")
        Confirm.resize(270, 89)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Confirm.sizePolicy().hasHeightForWidth())
        Confirm.setSizePolicy(sizePolicy)
        self.buttonBox = QtWidgets.QDialogButtonBox(Confirm)
        self.buttonBox.setGeometry(QtCore.QRect(10, 60, 251, 23))
        self.buttonBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Yes)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.message = QtWidgets.QLabel(Confirm)
        self.message.setGeometry(QtCore.QRect(10, 0, 251, 61))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.message.setFont(font)
        self.message.setText("")
        self.message.setWordWrap(True)
        self.message.setObjectName("message")

        self.retranslateUi(Confirm)
        self.buttonBox.accepted.connect(Confirm.accept)
        self.buttonBox.rejected.connect(Confirm.reject)
        QtCore.QMetaObject.connectSlotsByName(Confirm)

    def retranslateUi(self, Confirm):
        _translate = QtCore.QCoreApplication.translate
        Confirm.setWindowTitle(_translate("Confirm", "Warning"))

