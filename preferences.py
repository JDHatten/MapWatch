# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferences.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName("Preferences")
        Preferences.resize(400, 342)
        self.label_4 = QtWidgets.QLabel(Preferences)
        self.label_4.setGeometry(QtCore.QRect(6, 110, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.pref_lang = QtWidgets.QComboBox(Preferences)
        self.pref_lang.setGeometry(QtCore.QRect(170, 110, 131, 21))
        self.pref_lang.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pref_lang.setObjectName("pref_lang")
        self.pref_lang.addItem("")
        self.label_2 = QtWidgets.QLabel(Preferences)
        self.label_2.setGeometry(QtCore.QRect(220, 50, 47, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.pref_db_path = QtWidgets.QLineEdit(Preferences)
        self.pref_db_path.setGeometry(QtCore.QRect(196, 80, 191, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pref_db_path.setFont(font)
        self.pref_db_path.setText("")
        self.pref_db_path.setReadOnly(True)
        self.pref_db_path.setObjectName("pref_db_path")
        self.label = QtWidgets.QLabel(Preferences)
        self.label.setGeometry(QtCore.QRect(6, 50, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.pref_title = QtWidgets.QLabel(Preferences)
        self.pref_title.setGeometry(QtCore.QRect(6, 10, 241, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pref_title.setFont(font)
        self.pref_title.setObjectName("pref_title")
        self.label_5 = QtWidgets.QLabel(Preferences)
        self.label_5.setGeometry(QtCore.QRect(6, 140, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.line = QtWidgets.QFrame(Preferences)
        self.line.setGeometry(QtCore.QRect(5, 30, 388, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.pref_startup = QtWidgets.QCheckBox(Preferences)
        self.pref_startup.setGeometry(QtCore.QRect(-4, 80, 187, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pref_startup.setFont(font)
        self.pref_startup.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pref_startup.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.pref_startup.setChecked(False)
        self.pref_startup.setObjectName("pref_startup")
        self.pref_statistics = QtWidgets.QComboBox(Preferences)
        self.pref_statistics.setGeometry(QtCore.QRect(170, 140, 131, 21))
        self.pref_statistics.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pref_statistics.setCurrentText("")
        self.pref_statistics.setObjectName("pref_statistics")
        self.pref_buttons = QtWidgets.QDialogButtonBox(Preferences)
        self.pref_buttons.setGeometry(QtCore.QRect(10, 310, 381, 23))
        self.pref_buttons.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pref_buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Discard|QtWidgets.QDialogButtonBox.RestoreDefaults|QtWidgets.QDialogButtonBox.Save)
        self.pref_buttons.setObjectName("pref_buttons")
        self.line_2 = QtWidgets.QFrame(Preferences)
        self.line_2.setGeometry(QtCore.QRect(5, 290, 388, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.label_6 = QtWidgets.QLabel(Preferences)
        self.label_6.setGeometry(QtCore.QRect(16, 200, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.pref_zana_level = QtWidgets.QSpinBox(Preferences)
        self.pref_zana_level.setGeometry(QtCore.QRect(170, 200, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pref_zana_level.setFont(font)
        self.pref_zana_level.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pref_zana_level.setMinimum(1)
        self.pref_zana_level.setMaximum(8)
        self.pref_zana_level.setProperty("value", 8)
        self.pref_zana_level.setObjectName("pref_zana_level")
        self.label_7 = QtWidgets.QLabel(Preferences)
        self.label_7.setGeometry(QtCore.QRect(16, 230, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.pref_defualt_zana_mod = QtWidgets.QComboBox(Preferences)
        self.pref_defualt_zana_mod.setGeometry(QtCore.QRect(170, 230, 201, 23))
        self.pref_defualt_zana_mod.setCurrentText("")
        self.pref_defualt_zana_mod.setMaxVisibleItems(10)
        self.pref_defualt_zana_mod.setObjectName("pref_defualt_zana_mod")
        self.pref_hour = QtWidgets.QCheckBox(Preferences)
        self.pref_hour.setGeometry(QtCore.QRect(170, 170, 101, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pref_hour.setFont(font)
        self.pref_hour.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pref_hour.setObjectName("pref_hour")
        self.pref_millisec = QtWidgets.QCheckBox(Preferences)
        self.pref_millisec.setGeometry(QtCore.QRect(270, 170, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pref_millisec.setFont(font)
        self.pref_millisec.setObjectName("pref_millisec")
        self.label_8 = QtWidgets.QLabel(Preferences)
        self.label_8.setGeometry(QtCore.QRect(6, 170, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_8.setFont(font)
        self.label_8.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.pref_on_top = QtWidgets.QCheckBox(Preferences)
        self.pref_on_top.setGeometry(QtCore.QRect(10, 260, 231, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pref_on_top.setFont(font)
        self.pref_on_top.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pref_on_top.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.pref_on_top.setChecked(False)
        self.pref_on_top.setObjectName("pref_on_top")
        self.label_9 = QtWidgets.QLabel(Preferences)
        self.label_9.setGeometry(QtCore.QRect(260, 260, 101, 20))
        self.label_9.setObjectName("label_9")
        self.pref_map_check = QtWidgets.QDoubleSpinBox(Preferences)
        self.pref_map_check.setGeometry(QtCore.QRect(170, 50, 44, 21))
        self.pref_map_check.setDecimals(1)
        self.pref_map_check.setMinimum(0.5)
        self.pref_map_check.setMaximum(3.0)
        self.pref_map_check.setSingleStep(0.5)
        self.pref_map_check.setProperty("value", 2.0)
        self.pref_map_check.setObjectName("pref_map_check")

        self.retranslateUi(Preferences)
        self.pref_statistics.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        _translate = QtCore.QCoreApplication.translate
        Preferences.setWindowTitle(_translate("Preferences", "Preferences"))
        self.label_4.setText(_translate("Preferences", "Selected Language:"))
        self.pref_lang.setCurrentText(_translate("Preferences", "English"))
        self.pref_lang.setItemText(0, _translate("Preferences", "English"))
        self.label_2.setToolTip(_translate("Preferences", "<html><head/><body><p><span style=\" font-size:8pt;\">The amount of second\'s in-between clipboard checks this application preforms. </span></p></body></html>"))
        self.label_2.setText(_translate("Preferences", "seconds"))
        self.label.setToolTip(_translate("Preferences", "<html><head/><body><p><span style=\" font-size:8pt;\">The amount of second\'s in-between clipboard checks this application preforms. </span></p></body></html>"))
        self.label.setText(_translate("Preferences", "Check for maps every:"))
        self.pref_title.setText(_translate("Preferences", "Map Watch Preferences"))
        self.label_5.setText(_translate("Preferences", "Selected Statistics File:"))
        self.pref_startup.setText(_translate("Preferences", "Load Database on Startup:  "))
        self.label_6.setToolTip(_translate("Preferences", "<html><head/><body><p><span style=\" font-size:8pt;\">The level of your Master Zana will affect which mods you can use and how much bonus IQ you get from the first mod. </span></p></body></html>"))
        self.label_6.setText(_translate("Preferences", "Zana\'s Level:"))
        self.pref_zana_level.setToolTip(_translate("Preferences", "<html><head/><body><p><span style=\" font-size:8pt;\">The level of your Master Zana will affect which mods you can use and how much bonus IQ you get from the first mod. </span></p></body></html>"))
        self.label_7.setText(_translate("Preferences", "Zana\'s Defualt Mod:"))
        self.pref_hour.setToolTip(_translate("Preferences", "<html><head/><body><p><span style=\" font-size:8pt;\">Time formatting options are used for this application and any statistics files. </span></p></body></html>"))
        self.pref_hour.setText(_translate("Preferences", "12 Hour Time"))
        self.pref_millisec.setToolTip(_translate("Preferences", "<html><head/><body><p><span style=\" font-size:8pt;\">Time formatting options are used for this application and any statistics files. </span></p></body></html>"))
        self.pref_millisec.setText(_translate("Preferences", "Show Milliseconds"))
        self.label_8.setToolTip(_translate("Preferences", "<html><head/><body><p><span style=\" font-size:8pt;\">Time formatting options are used for this application and any statistics files. </span></p></body></html>"))
        self.label_8.setText(_translate("Preferences", "Time Formating Options:"))
        self.pref_on_top.setText(_translate("Preferences", "* Always Keep Map Watch On Top:  "))
        self.label_9.setText(_translate("Preferences", "* Requires Restart"))
        self.pref_map_check.setToolTip(_translate("Preferences", "<html><head/><body><p>The amount of second\'s in-between clipboard checks this application preforms.</p></body></html>"))

