import sys
import os
import re
import configparser
import copy
import datetime
import json
import pyperclip
import pywinauto
import requests
import sqlite3
import time
import webbrowser
import win32con
import win32gui

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt, QThread
from PyQt5.QtWidgets import QFileDialog
from window import Ui_MainWindow
from confirm import Ui_Confirm
from preferences import Ui_Preferences
from about import Ui_About
from addmore import Ui_AddMore
from counter import Ui_Counter

# TODOS:
### Create custom icons
### Create more HTML statistic files
### Sacrifice Fragments ...eh
### 

class Map():
    TimeAdded = 0
    DroppedInID = 1
    ClearTime = 1
    Name = 2
    Tier = 3
    IQ = 4
    BonusIQ = 5
    IR = 6
    PackSize = 7
    Rarity = 8
    Mod1 = 9
    Mod2 = 10
    Mod3 = 11
    Mod4 = 12
    Mod5 = 13
    Mod6 = 14
    Mod7 = 15
    Mod8 = 16
    Mod9 = 17
    Mod10 = 18
    Mod11 = 19
    Mod12 = 20
    Mod13 = 21
    Mod14 = 22
    Mod15 = 23
    Mod16 = 24
    Mod17 = 25
    Mod18 = 26
    Corrupted = 27
    ZanaMod = 28
    League = 29
    Fragments = 30
    CartoFound = 31
    ZanaFound = 32
    Notes = 33

class Maps():
    Dropped = 0
    Ran = 1

class MapType():
    Standard = 0
    Corrupted = 1
    Fragment = 2
    RareFragment = 3

class ZanaMod():
    Name = 0
    Cost = 1
    Level = 2
    IQ = 3
    Desc = 4

class Button():
    Add = 0
    Delete = 1
    Run = 2
    Clear = 3

class MapWatchWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        # General Settings
        self.version = '0.4'
        self.appTitle = 'Map Watch (v'+self.version+')'
        self.setWindowIcon(QtGui.QIcon(r'images\\icon.ico'))
        self.firstClose = 1
        #Windows hwnd
        self._handle = None
        self.window = None
        # System Tray Icon
        self.sysTrayIcon = QtWidgets.QSystemTrayIcon()
        self.sysTrayIcon.setIcon(QtGui.QIcon(r'images\\icon.ico'))
        self.sysTrayIcon.show()
        self.sysTrayIcon.activated.connect(self.restore)
        # System Tray Context Menu
        menu = QtWidgets.QMenu(parent)
        icon = QtGui.QIcon(r'images\\icon.ico')
        restoreAction = QtWidgets.QAction(icon, '&Show Map Watch', self)
        restoreAction.triggered.connect(self.popup)
        menu.addAction(restoreAction)

        # icon = QtGui.QIcon('')
        # self.pauseAction = QtWidgets.QAction(icon, '&Pause', self)
        # self.pauseAction.triggered.connect(lambda: self.pauseMapWatch(True))
        # menu.addAction(self.pauseAction)

        menu.addSeparator()
        icon = QtGui.QIcon('')
        exitAction = QtWidgets.QAction(icon, '&Exit', self)
        exitAction.triggered.connect(self.closeApplication)
        menu.addAction(exitAction)
        self.sysTrayIcon.setContextMenu(menu)
        # This will do the Map Watching in a different thread
        self.thread = MapWatcher()
        self.thread.runLoop(True)
        self.thread.trigger.connect(self.newMapFound)  # Triggered when new map found
        # Setup Map Database
        self.map_data = None
        self.mapDB = MapDatabase(self)
        # Configure UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(471, 382)
        self.setWindowTitle(self.appTitle)
        self.ui_confirm = ConfirmDialog(self)

        self.ui_prefs = Preferences(self)
        self.ui_addmore = AddMore(self)
        self.ui_about = About(self)
        self.setPrefs()

        if not int(self.settings['AlwaysOnTop']):
            self.setWindowFlags(Qt.CustomizeWindowHint|Qt.WindowCloseButtonHint|Qt.X11BypassWindowManagerHint)
        else:
            #self.setStyleSheet('background: rgba(0,0,255,20%)')
            #self.setAttribute(Qt.WA_NoSystemBackground)
            #self.setAttribute(Qt.WA_TranslucentBackground)
            #self.setAttribute(Qt.WA_OpaquePaintEvent)
            #self.setAttribute(Qt.WA_PaintOnScreen)

            self.setWindowFlags(Qt.CustomizeWindowHint|Qt.WindowCloseButtonHint|Qt.WindowStaysOnTopHint|Qt.X11BypassWindowManagerHint)
            #self.setWindowFlags(Qt.CustomizeWindowHint|Qt.WindowCloseButtonHint|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.X11BypassWindowManagerHint)
            #setWindowFlags(Qt::Widget |Qt.FramelessWindowHint);t.
            #setParent(0); // Create TopLevel-Widget

            # from ctypes import windll, c_int, byref
            # windll.dwmapi.DwmExtendFrameIntoClientArea(c_int(self.winId()), byref(c_int(-1)))

            # self.setAttribute(Qt.WA_OpaquePaintEvent)
            # self.setAttribute(Qt.WA_PaintOnScreen)


        # Button Actions
        self.ui.ms_add_map.clicked.connect(self.addMap)
        self.ui.ms_delete_map.clicked.connect(self.deleteMap)
        self.ui.mr_clear_map.clicked.connect(self.clearMap)
        self.ui.mr_add_more.clicked.connect(self.addMore)
        self.ui.mr_run_map.clicked.connect(self.runMap)
        # self.ui.mr_add_zana_mod.currentIndexChanged.connect(self.changeZanaMod)
        # self.ui.mr_add_bonus_iq.valueChanged.connect(self.changeBonusIQ)
        # Menu Actions
        self.ui.menu_create_new_db.triggered.connect(lambda: self.setDBFile(True))
        self.ui.menu_load_db.triggered.connect(self.setDBFile)
        self.ui.menu_open_stats.triggered.connect(self.openStatFile)
        self.ui.menu_exit_app.triggered.connect(self.closeApplication)
        self.ui.menu_ms_add_map.triggered.connect(self.addMap)
        self.ui.menu_ms_add_unlinked_map.triggered.connect(lambda: self.addMap(True))
        self.ui.menu_ms_delete_map.triggered.connect(self.deleteMap)
        self.ui.menu_mr_clear_map.triggered.connect(self.clearMap)
        self.ui.menu_mr_run_map.triggered.connect(self.runMap)
        self.ui.menu_preferences.triggered.connect(self.getPrefs)
        self.ui.menu_pause.triggered.connect(lambda: self.pauseMapWatch(True))
        self.ui.menu_about.triggered.connect(self.about)
        # Keyboard Shortcuts
        self.hotkey_add = QtWidgets.QShortcut(QtGui.QKeySequence("A"), self, self.addMap)
        self.hotkey_addu = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+U"), self, lambda: self.addMap(True))
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+D"), self, self.deleteMap)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+X"), self, self.clearMap)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+R"), self, self.runMap)
        # QtWidgets.QShortcut(QtGui.QKeySequence("Z"), self, lambda: self.giveFocus('ZanaMod'))
        # QtWidgets.QShortcut(QtGui.QKeySequence("Q"), self, lambda: self.giveFocus('BonusIQ'))
        QtWidgets.QShortcut(QtGui.QKeySequence("M"), self, self.minimizeToSysTray)
        QtWidgets.QShortcut(QtGui.QKeySequence("Esc"), self, self.minimizeToSysTray)
        QtWidgets.QShortcut(QtGui.QKeySequence("F1"), self, lambda: self.setDBFile(True))
        QtWidgets.QShortcut(QtGui.QKeySequence("F2"), self, self.setDBFile)
        QtWidgets.QShortcut(QtGui.QKeySequence("F3"), self, self.openStatFile)
        QtWidgets.QShortcut(QtGui.QKeySequence("F4"), self, self.getPrefs)
        QtWidgets.QShortcut(QtGui.QKeySequence("F5"), self, self.about)
        QtWidgets.QShortcut(QtGui.QKeySequence("F12"), self, self.closeApplication)
        self.button_access = [False, False, False, False]
        if int(self.settings['LoadLastOpenedDB']):
            if os.path.exists(self.settings['LastOpenedDB']):
                self.mapDB.setDBFile(self.settings['LastOpenedDB'])
                self.mapDB.setupDB('Checking DB Structure', True)
            else:
                self.mapDB.setupDB(self.settings['LastOpenedDB'])
        else:
            self.buttonAccess(self.button_access)
        self.updateWindowTitle()

    def _window_enum_callback(self, hwnd, wildcard):
        '''Pass to win32gui.EnumWindows() to check all the opened windows'''
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd
            print('hwnd: '+str(self._handle))
        #print(str(win32gui.GetWindowText(hwnd)))

    def restore(self, action):
        if action == self.sysTrayIcon.DoubleClick:
            self.popup()

    def popup(self):
        self.button_access = [True, True, True, True]
        if self.thread.map_type is MapType.Fragment:
            self.button_access[Button.Add] = False
        if self.mapDB.db_file:
            self.buttonAccess(self.button_access)
        self.showNormal()
        #self.show()
        self.activateWindow()
        if self._handle:
            #win32gui.ShowWindow(self._handle, win32con.SW_RESTORE)
            win32gui.BringWindowToTop(self._handle)
            if int(self.settings['AlwaysOnTop']):
                win32gui.SetWindowPos(self._handle, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
            else:
                win32gui.SetWindowPos(self._handle, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
                win32gui.SetWindowPos(self._handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
            self.window.SetFocus() #STEALFOCUS

    def pauseMapWatch(self, pause):
        print('Pause: '+str(pause))
        self.thread.pause(pause)
        if pause:
            self.ui.menu_pause.setText("&Start Map Watching")
            self.ui.menu_pause.triggered.connect(lambda: self.pauseMapWatch(False))
        else:
            self.ui.menu_pause.setText("&Stop Map Watching")
            self.ui.menu_pause.triggered.connect(lambda: self.pauseMapWatch(True))

    # def giveFocus(self, widget):
    #     if widget is 'ZanaMod':
    #         self.ui.mr_add_zana_mod.setFocus(Qt.ShortcutFocusReason)
    #     elif widget is 'BonusIQ':
    #         self.ui.mr_add_bonus_iq.setFocus(Qt.ShortcutFocusReason)

    def newMapFound(self, map_data):
        self.popup()
        self.map_data = map_data
        self.updateUiMapSelected()

    def updateUiMapSelected(self):
        print('UI Updated')
        # Clear those items that may not be updated with new map
        self.ui.ms_iq.setText('0%')
        self.ui.ms_ir.setText('0%')
        self.ui.ms_pack_size.setText('0%')
        self.ui.ms_mods.setText('None')
        # Get each piece of map info and update UI lables, etc
        if Map.TimeAdded in self.map_data:
            h = '%H'
            ms = ''
            p = ''
            if int(self.settings['ClockHour12']):
                h = '%I'
                p = ' %p'
            if int(self.settings['ShowMilliseconds']):
                ms = '.%f'
            time_added = datetime.datetime.fromtimestamp(self.map_data[Map.TimeAdded]).strftime(h+':%M:%S'+ms+p)
            self.ui.ms_time_stamp.setText(time_added)
        if Map.Name in self.map_data:
            self.ui.ms_name.setText(self.map_data[Map.Name])
        if Map.Tier in self.map_data:
            level = int(self.map_data[Map.Tier]) + 67
            self.ui.ms_tier.setText(self.map_data[Map.Tier] + '  (' + str(level) + ')')
        if Map.IQ in self.map_data:
            self.ui.ms_iq.setText(self.map_data[Map.IQ]+'%')
        if Map.IR in self.map_data:
            self.ui.ms_ir.setText(self.map_data[Map.IR]+'%')
        if Map.PackSize in self.map_data:
            self.ui.ms_pack_size.setText(self.map_data[Map.PackSize]+'%')
        if Map.Rarity in self.map_data:
            rarity = self.map_data[Map.Rarity]
            self.ui.ms_rarity.setText(rarity)
            if rarity == 'Rare':
                self.ui.ms_name.setStyleSheet("color: rgb(170, 170, 0);")
            elif rarity == 'Magic':
                self.ui.ms_name.setStyleSheet("color: rgb(0, 85, 255);")
            elif rarity == 'Unique':
                self.ui.ms_name.setStyleSheet("color: rgb(170, 85, 0);")
            else:
                self.ui.ms_name.setStyleSheet("color: rgb(0, 0, 0);")
        if Map.Mod1 in self.map_data:
            all_mods = self.map_data[Map.Mod1]
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod2 in self.map_data:
            all_mods = all_mods + '\r\n' + self.map_data[Map.Mod2]
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod3 in self.map_data:
            all_mods = all_mods + '\r\n' + self.map_data[Map.Mod3]
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod4 in self.map_data:
            all_mods = all_mods + '\r\n' + self.map_data[Map.Mod4]
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod5 in self.map_data:
            all_mods = all_mods + '\r\n' + self.map_data[Map.Mod5]
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod6 in self.map_data:
            all_mods = all_mods + '\r\n' + self.map_data[Map.Mod6]
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod7 in self.map_data:
            all_mods = all_mods + '\r\n' + self.map_data[Map.Mod7]
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod8 in self.map_data:
            all_mods = all_mods + '\r\n' + self.map_data[Map.Mod8]
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod9 in self.map_data:
            all_mods = all_mods + '\r\n' + self.map_data[Map.Mod9]
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod10 in self.map_data:
            all_mods = all_mods + '\r\n' + self.map_data[Map.Mod10]
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod11 in self.map_data:
            all_mods = all_mods + '\r\n' + self.map_data[Map.Mod11]
            self.ui.ms_mods.setText(all_mods)
        # if Map.ZanaMod in self.map_data:
        #     all_mods = all_mods + '\r\n' + self.map_data[Map.ZanaMod]
        #     self.ui.ms_mods.setText(all_mods)
        if Map.Corrupted in self.map_data and int(self.map_data[Map.Corrupted]):
            all_mods = self.ui.ms_mods.toHtml() + '\r\n<br><span  style="color:#CC0000">Corrupted</span>'
            self.ui.ms_mods.setText(all_mods)

    def updateUiMapRunning(self, clear=False):
        print('UI Updated')
        if clear:
            self.ui.mr_name.setText('None')
            self.ui.mr_tier.setText('0')
            self.ui.mr_iq.setText('0%')
            self.ui.mr_bonus_iq.setText('')
            self.ui.mr_ir.setText('0%')
            self.ui.mr_pack_size.setText('0%')
            self.ui.mr_rarity.setText('')
            self.ui.mr_mods.setText('')
            self.ui.mr_name.setStyleSheet("color: rgb(0, 0, 0);")
        else:
            self.ui.mr_name.setText(self.ui.ms_name.text())
            self.ui.mr_tier.setText(self.ui.ms_tier.text())
            self.ui.mr_iq.setText(self.ui.ms_iq.text())
            self.ui.mr_ir.setText(self.ui.ms_ir.text())
            self.ui.mr_pack_size.setText(self.ui.ms_pack_size.text())
            self.ui.mr_rarity.setText(self.ui.ms_rarity.text())
            self.ui.mr_mods.setText(self.ui.ms_mods.toPlainText())
            self.map_mod_text = self.ui.ms_mods.toHtml() # orginal copy for adding/removing Zana Mod
            rarity = self.ui.ms_rarity.text()
            if rarity == 'Rare':
                self.ui.mr_name.setStyleSheet("color: rgb(170, 170, 0);")
            elif rarity == 'Magic':
                self.ui.mr_name.setStyleSheet("color: rgb(0, 85, 255);")
            elif rarity == 'Unique':
                self.ui.mr_name.setStyleSheet("color: rgb(170, 85, 0);")
            else:
                self.ui.mr_name.setStyleSheet("color: rgb(0, 0, 0);")

    def updateUiMapRunningBonuses(self):
        print('UI Updated')
        #print(self.mapDB.map_running[Map.BonusIQ])
        if Map.BonusIQ in self.mapDB.map_running and self.mapDB.map_running[Map.BonusIQ] != 0:
            self.ui.mr_bonus_iq.setText('+'+str(self.mapDB.map_running[Map.BonusIQ])+'%')
        else:
            self.ui.mr_bonus_iq.setText('')
        if Map.ZanaMod in self.mapDB.map_running:
            if self.mapDB.map_running[Map.ZanaMod] and self.map_mod_text:
                all_mods = self.map_mod_text + '\r\n<br><b>' + self.mapDB.map_running[Map.ZanaMod] + '</b>'
                self.ui.mr_mods.setText(all_mods)
            else:
                self.ui.mr_mods.setText(self.map_mod_text)

    def deleteMap(self):
        print('Removing Last Map')
        self.ui_confirm.boxType('confirm')
        del_map = None
        if self.ui_confirm.exec_('Delete Map?', 'Are you sure you want to delete the last map saved to database?'):
            del_map = self.mapDB.deleteLastMap(Maps.Dropped)
            self.updateWindowTitle()
        if del_map:
            self.sysTrayIcon.showMessage(
                'Last Map Deleted',
                del_map+' was deleted from the database.',
                1, 1000)

    def addMap(self, unlinked=False):
        print('Adding to Map Drops')
        add_map = self.mapDB.addMap(self.map_data, unlinked)
        if add_map:
            self.minimizeToSysTray()
            self.updateWindowTitle()
            self.sysTrayIcon.showMessage(
                'Map Added',
                add_map+' was added to the database.',
                1, 1000)

    def clearMap(self):
        if self.mapDB.map_running:
            self.ui_confirm.boxType('confirm')
            if self.ui_confirm.exec_('Map Cleared?', 'Is the current running map cleared?  No more map drops will be linked to this map.'):
                self.mapDB.clearMap()
                self.updateUiMapRunning(True)
                return True
            else:
                return False
        else:
            return True

    def addMore(self):
        if self.ui_addmore.exec_() and self.mapDB.map_running:
            self.updateUiMapRunningBonuses()

    def runMap(self):
        print('Running Selected Map')
        if self.mapDB.runMap(self.map_data):
            self.ui_addmore.reset(True)
            self.updateUiMapRunning()
            #self.mapDB.map_type_running = self.thread.map_type
            self.updateUiMapRunningBonuses()

    def setDBFile(self, new=False):
        if self.clearMap():
            abs_path = os.path.abspath(os.path.dirname('__file__'))
            if new:
                file_name = QFileDialog.getSaveFileName(self, 'Create New Database File', abs_path+'/data', 'SQLite Files (*.sqlite)')
                if file_name[0]:
                    self.mapDB.setupDB(file_name[0])
            else:
                file_name = QFileDialog.getOpenFileName(self, 'Load Database File', abs_path+'/data', 'SQLite Files (*.sqlite)')
            # Update settings
            if file_name[0]:
                self.mapDB.setDBFile(file_name[0])
                if not new:
                    self.mapDB.setupDB('Checking DB Structure', True)
                self.updateWindowTitle()
                self.popup()
                self.settings['LastOpenedDB'] = file_name[0]
                writeSettings(self.settings)

    # def addZanaMods(self):
    #     print('Adding Zana Mods to Combo Box')
    #     self.ui.mr_add_zana_mod.clear()
    #     for i, zana_mod in enumerate(self.zana_mods):
    #         self.ui.mr_add_zana_mod.addItem(zana_mod[ZanaMod.Name] + ' (' + zana_mod[ZanaMod.Cost] + ')')
    #         if int(self.settings['ZanaDefaultModIndex']) == i:
    #             self.ui.mr_add_zana_mod.setCurrentIndex(i)
    #         if int(self.settings['ZanaLevel']) < zana_mod[ZanaMod.Level]:
    #             break # Stop adding mod options if Zana level is to low to run them

    # def changeZanaLevel(self):
    #     self.zana_mods[1][ZanaMod.IQ] = int(self.settings['ZanaLevel'])
    #     self.addZanaMods()

    # def changeZanaMod(self):
    #     print('New Zana Mod Selected')
    #     if self.mapDB.map_running:
    #         self.mapDB.map_running[Map.BonusIQ] = self.calcBonusIQ()
    #         zana_mod_str = self.zana_mods[self.ui.mr_add_zana_mod.currentIndex()][ZanaMod.Desc]
    #         self.mapDB.map_running[Map.Mod9] = zana_mod_str
    #         self.updateUiMapRunningBonuses()
    #         self.ui.mr_mods.moveCursor(QtGui.QTextCursor.End)

    # def changeBonusIQ(self):
    #     print('Bonus IQ Changed')
    #     if self.mapDB.map_running:
    #         self.mapDB.map_running[Map.BonusIQ] = self.calcBonusIQ()
    #         self.updateUiMapRunningBonuses()

    # def calcBonusIQ(self):
    #     zana_iq = self.zana_mods[self.ui.mr_add_zana_mod.currentIndex()][ZanaMod.IQ]
    #     bonus_iq = self.ui.mr_add_bonus_iq.property('value') + zana_iq
    #     return bonus_iq

    # def resetBonuses(self):
    #     self.ui.mr_add_zana_mod.setCurrentIndex(-1) # force change event
    #     self.ui.mr_add_zana_mod.setCurrentIndex(int(self.settings['ZanaDefaultModIndex']))
    #     self.ui.mr_add_bonus_iq.setProperty('value', 0)

    def openStatFile(self):
        stat_file = self.settings['SelectedStatisticsFile']
        webbrowser.open('file://' + stat_file)

    def getPrefs(self):
        if self.ui_prefs.exec_():
            self.setPrefs()

    def setPrefs(self):
        self.settings = readSettings()
        self.popup()
        self.thread.setMapCheckInterval(float(self.settings['MapCheckInterval']))
        self.ui_addmore.loadLeagues()
        self.ui_addmore.updateZanaLevel()
        hour12 = self.settings['ClockHour12']
        milliseconds = self.settings['ShowMilliseconds']
        hour12 = False if hour12 == '0' else True
        milliseconds = False if milliseconds == '0' else True
        settings = {'hour12': hour12, 'milliseconds': milliseconds}
        writeSettingsJS(settings)
        print("Preferences Updated")

    def about(self):
        self.ui_about.exec_()
        # self.ui_confirm.boxType('about')
        # self.ui_confirm.exec_('About', 'Map Watch\nVersion '+self.version+'\n\nCreated by\nJonathan.D.Hatten@gmail.com\nIGN: Grahf_Azura')

    def updateWindowTitle(self):
        if self.mapDB.db_file:
            map_count = self.mapDB.countMapsAdded()
            self.setWindowTitle(self.appTitle + ' ---> ' + str(map_count) + ' map drops in database (' + os.path.basename(self.mapDB.db_file) + ')')
        else:
            self.setWindowTitle(self.appTitle + ' ---> Map Database Not Loaded')

    def buttonAccess(self, button):
        self.ui.ms_add_map.setEnabled(button[Button.Add])
        self.ui.ms_delete_map.setEnabled(button[Button.Delete])
        self.ui.mr_clear_map.setEnabled(button[Button.Clear])
        self.ui.mr_run_map.setEnabled(button[Button.Run])
        self.ui.menu_ms_add_map.setEnabled(button[Button.Add])
        self.ui.menu_ms_add_unlinked_map.setEnabled(button[Button.Add])
        self.ui.menu_ms_delete_map.setEnabled(button[Button.Delete])
        self.ui.menu_mr_clear_map.setEnabled(button[Button.Clear])
        self.ui.menu_mr_run_map.setEnabled(button[Button.Run])
        self.hotkey_add.setEnabled(button[Button.Add])
        self.hotkey_addu.setEnabled(button[Button.Add])

    def error(self, err_msg, errors=None):
        err_msg += '\n'
        if errors is not None:
            for err in errors:
                err_msg += '\n'+str(err)
                #print(err)
        self.ui_confirm.boxType('error')
        self.ui_confirm.exec_('Error', err_msg)

    def closeApplication(self):
        print('Map Watch Closing')
        self.mapDB.clearMap() # In-case user forgot to clear thier map before closing app
        self.sysTrayIcon.hide()
        sys.exit()

    def closeEvent(self, event):
        # Changes the close button (X) behavior to minimize instead
        event.ignore()
        if self.firstClose:
            self.sysTrayIcon.showMessage(
                'Minimized To System Tray',
                'Map Watch will still continue to run in the background. Right click and select exit to shut down application.',
                1, 1000)
            self.firstClose = 0
        self.minimizeToSysTray()
        #self.closeApplication()

    def minimizeToSysTray(self):
        self.showMinimized()
        self.hide()


class ConfirmDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Confirm()
        self.ui.setupUi(self)
        self.setFixedSize(270, 89)
        print("ConfirmBox loaded")

    def exec_(self, title=None, message=None):
        if title:
            self.setWindowTitle(title)
        if message:
            self.ui.message.setText(message)
        return super().exec_()

    def setTitle(self, text):
        self.setWindowTitle(text)

    def setTextMsg(self, text):
        self.ui.message.setText(text)

    def boxType(self, type):
        if type is 'confirm':
            self.setFixedSize(270, 89)
            self.ui.buttonBox.setGeometry(QtCore.QRect(10, 60, 251, 23))
            self.ui.message.setGeometry(QtCore.QRect(10, 0, 251, 61))
            self.ui.message.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.ui.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Yes)
            self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.No).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        if type is 'confirmXL':
            self.setFixedSize(270, 149)
            self.ui.buttonBox.setGeometry(QtCore.QRect(10, 120, 251, 23))
            self.ui.message.setGeometry(QtCore.QRect(10, 0, 251, 121))
            self.ui.message.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.ui.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Yes)
            self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.No).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        elif type is 'error':
            self.setFixedSize(270, 199)
            self.ui.buttonBox.setGeometry(QtCore.QRect(10, 170, 251, 23))
            self.ui.message.setGeometry(QtCore.QRect(10, 0, 251, 161))
            self.ui.message.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.ui.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
            self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        elif type is 'about':
            self.setFixedSize(270, 189)
            self.ui.buttonBox.setGeometry(QtCore.QRect(10, 160, 251, 23))
            self.ui.message.setGeometry(QtCore.QRect(10, 0, 251, 141))
            self.ui.message.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            self.ui.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
            self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))


class Preferences(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.setFixedSize(400, 368)
        self.statistics_files = []
        self.leagues = []
        self.loadData()
        self.ui.pref_buttons.accepted.connect(self.accept)
        self.ui.pref_buttons.button(QtWidgets.QDialogButtonBox.Save).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ui.pref_buttons.button(QtWidgets.QDialogButtonBox.Discard).clicked.connect(self.reject)
        self.ui.pref_buttons.button(QtWidgets.QDialogButtonBox.Discard).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ui.pref_buttons.button(QtWidgets.QDialogButtonBox.RestoreDefaults).clicked.connect(self.restoreDefaults)
        self.ui.pref_buttons.button(QtWidgets.QDialogButtonBox.RestoreDefaults).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        print("Preferences Window loaded")

        #self.setStyleSheet('background: rgba(0,0,255,20%)')
        #self.setAttribute(Qt.WA_NoSystemBackground)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setAttribute(Qt.WA_OpaquePaintEvent)
        #self.setAttribute(Qt.WA_PaintOnScreen)
        #self.setWindowFlags(Qt.CustomizeWindowHint|Qt.WindowCloseButtonHint|Qt.WindowStaysOnTopHint|Qt.X11BypassWindowManagerHint)

        # Transparent Window
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setWindowFlags(Qt.Dialog|Qt.CustomizeWindowHint|Qt.WindowCloseButtonHint|Qt.FramelessWindowHint)


    def loadData(self):
        abs_path = os.path.abspath(os.path.dirname('__file__'))
        statistics_dir = abs_path+'\\statistics\\'
        file_names = os.listdir(statistics_dir)
        for file_name in file_names:
            match = re.search(r'\w+\.html', file_name)
            if match:
                self.statistics_files.append(statistics_dir+file_name)
        leagues = readData('Leagues')
        for league in leagues:
            self.leagues.append(leagues[str(league)])

    def insertPrefs(self):
        self.ui.pref_map_check.setProperty('value', float(self.parent.settings['MapCheckInterval']))
        self.ui.pref_startup.setChecked(int(self.parent.settings['LoadLastOpenedDB']))
        self.ui.pref_db_path.setText((self.parent.settings['LastOpenedDB']))
        self.ui.pref_statistics.clear()
        for i, stat_file in enumerate(self.statistics_files):
            self.ui.pref_statistics.addItem(os.path.basename(stat_file))
            if stat_file == self.parent.settings['SelectedStatisticsFile']:
                self.ui.pref_statistics.setCurrentIndex(i)
        self.ui.pref_hour.setChecked(int(self.parent.settings['ClockHour12']))
        self.ui.pref_millisec.setChecked(int(self.parent.settings['ShowMilliseconds']))
        self.ui.pref_defualt_league.clear()
        for i, league in enumerate(self.leagues):
            self.ui.pref_defualt_league.addItem(league)
            if self.parent.settings['DefualtLeague'] == league:
                self.ui.pref_defualt_league.setCurrentIndex(i)
        self.ui.pref_zana_level.setProperty('value', int(self.parent.settings['ZanaLevel']))
        self.ui.pref_defualt_zana_mod.clear()
        for i, zana_mod in enumerate(self.parent.ui_addmore.zana_mods):
            self.ui.pref_defualt_zana_mod.addItem(zana_mod[ZanaMod.Name] + ' (' + zana_mod[ZanaMod.Cost] + ')')
            if int(self.parent.settings['ZanaDefaultModIndex']) == i:
                self.ui.pref_defualt_zana_mod.setCurrentIndex(i)
            # if self.ui.pref_zana_level.property('value') < zana_mod[ZanaMod.Level]:
            #     break
        self.ui.pref_on_top.setChecked(int(self.parent.settings['AlwaysOnTop']))

    def restoreDefaults(self):
        self.parent.ui_confirm.boxType('confirm')
        if self.parent.ui_confirm.exec_('Restore Defaults?', 'Are you sure you want to restore the default settings?'):
            get_defaults = True
            self.parent.settings = readSettings(get_defaults)
            self.insertPrefs()

    def accept(self):
        self.parent.settings['MapCheckInterval'] = str(self.ui.pref_map_check.property('value'))
        self.parent.settings['LoadLastOpenedDB'] = str(self.ui.pref_startup.checkState())
        self.parent.settings['SelectedStatisticsFile'] = self.statistics_files[self.ui.pref_statistics.currentIndex()]
        self.parent.settings['ClockHour12'] = str(self.ui.pref_hour.checkState())
        self.parent.settings['ShowMilliseconds'] = str(self.ui.pref_millisec.checkState())
        self.parent.settings['DefualtLeague'] = self.ui.pref_defualt_league.currentText()
        self.parent.settings['ZanaLevel'] = str(self.ui.pref_zana_level.property('value'))
        self.parent.settings['ZanaDefaultModIndex'] = str(self.ui.pref_defualt_zana_mod.currentIndex())
        self.parent.settings['AlwaysOnTop'] = str(self.ui.pref_on_top.checkState())
        writeSettings(self.parent.settings)
        super().accept()

    def exec_(self):
        self.insertPrefs()
        return super().exec_()


class About(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ui = Ui_About()
        self.ui.setupUi(self)
        self.setFixedSize(334, 290)
        self.ui.version.setText('Version '+self.parent.version)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ui.email.mouseReleaseEvent = self.email
        self.ui.update.mouseReleaseEvent = self.checkForUpdates
        print("About Window loaded")

    def exec_(self):
        return super().exec_()

    def accept(self):
        super().accept()

    def email(self, event):
        print('Email Clicked')
        webbrowser.open('mailto:%s?subject=%s&body=' % ('Jonathan.D.Hatten@gmail.com', 'Map%20Watch%20Inquiry'))

    def checkForUpdates(self, event):
        print('Checking for updates...')
        self.ui.update.setText('<html><head/><body><p><span style="color:#0055ff;">Checking...</span></p></body></html>')
        self.repaint()
        latest_tag = None
        try:
            r = requests.get('https://api.github.com/repos/JDHatten/MapWatch/releases', verify='cacert.pem')
            latest_tag = r.json()[0]['tag_name']
        except:
            self.parent.error('Error: Checking for an update failed.', sys.exc_info())
        if latest_tag:
            latest_tag = float(latest_tag[1:])
            if float(self.parent.version) >= latest_tag:
                self.ui.update.setText('<html><head/><body><p><span style="color:#0055ff;">No Update Available</span></p></body></html>')
            else:
                self.ui.update.setText('<html><head/><body><p><span style="color:#0055ff;">An Update is Available</span></p></body></html>')
                self.ui.update.mouseReleaseEvent = self.getUpdate
        else:
            self.ui.update.setText('<html><head/><body><p><span style="color:#0055ff;">Update Available?</span></p></body></html>')
            self.ui.update.mouseReleaseEvent = self.getUpdate

    def getUpdate(self, event):
        webbrowser.open('https://github.com/JDHatten/MapWatch/releases')


class AddMore(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ui = Ui_AddMore()
        self.ui.setupUi(self)
        self.setFixedSize(341, 320)
        # self.zana_mods = [ # TODO: maybe load from outside source? settings.ini?
        #     ['None', 'Free', 0, 0, ''],
        #     ['Item Quantity', 'Free', 1, 0, '+1% Quantity Per Master Level'],
        #     ['Rampage', '4x Chaos Orbs', 2, 0, 'Slaying enemies quickly grants Rampage bonuses'],
        #     ['Bloodlines', '4x Chaos Orbs', 2, 15, 'Magic Monster Packs each have a Bloodline Mod'],
        #     ['Anarchy', '8x Chaos Orbs', 3, 16, 'Area is inhabited by 4 additional Rogue Exiles'],
        #     ['Invasion', '8x Chaos Orbs', 3, 16, 'Area is inhabited by 3 additional Invasion Bosses'],
        #     ['Domination', '10x Chaos Orbs', 4, 0, 'Area Contains 5 Extra Shrines'],
        #     ['Onslaught', '8x Chaos Orbs', 4, 30, '40% Increased Monster Cast & Attack Speed'],
        #     ['Torment', '8x Chaos Orbs', 5, 12, 'Area spawns 3 extra Tormented Spirits (Stacks with any that naturally spawned)'],
        #     ['Beyond', '12x Chaos Orbs', 5, 8, 'Slaying enemies close together can attract monsters from Beyond this realm'],
        #     ['Tempest', '6x Choas Orbs', 6, 16, 'Powerful Tempests can affect both Monsters and You'],
        #     ['Ambush', '12x Chaos Orbs', 6, 0, 'Area contains 4 extra Strongboxes'],
        #     ['Warbands', '12x Chaos Orbs', 7, 16, 'Area is inhabited by 2 additional Warbands'],
        #     ['Nemesis', '1x Exalted Orb', 7, 0, 'One Rare Per Pack, Rare Monsters Each Have A Nemesis Mod']
        # ]
        self.zana_mods = []
        self.curLeague = 0
        self.leagues = []
        self.loadExternalData()
        # self.curIQ = 0
        # self.curIR = 0
        # self.curPS = 0
        self.curFrags = 1
        self.curZanaMod = 0
        self.curCartoFound = 0
        self.curZanaFound = 0
        self.curNotes = ''
        self.ui.add_zana_mod.currentIndexChanged.connect(self.changeZanaMod)
        self.ui.add_fragments.valueChanged.connect(self.changeBonusIQ)
        self.ui.add_iq.valueChanged.connect(self.changeIQ)
        self.ui.add_ir.valueChanged.connect(self.changeIR)
        self.ui.add_pack_size.valueChanged.connect(self.changePackSize)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Save).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        print('Preferences Window loaded')

    def loadExternalData(self):
        zanamods = readData('Zanamods')
        for mod in zanamods:
            self.zana_mods.append([x.strip() for x in zanamods[str(mod)].split(',')])
        #print(self.zana_mods)
        leagues = readData('Leagues')
        for league in leagues:
            self.leagues.append(leagues[str(league)])
        #print(self.leagues)

    def loadLeagues(self):
        print('Adding Leagues to Combo Box')
        self.ui.add_league.clear()
        for i, league in enumerate(self.leagues):
            self.ui.add_league.addItem(league)
            if self.parent.settings['DefualtLeague'] == league:
                self.ui.add_league.setCurrentIndex(i)

    def updateZanaLevel(self):
        self.zana_mods[1][ZanaMod.IQ] = int(self.parent.settings['ZanaLevel'])
        self.loadZanaMods()

    def loadZanaMods(self):
        print('Adding Zana Mods to Combo Box')
        self.ui.add_zana_mod.clear()
        for i, zana_mod in enumerate(self.zana_mods):
            self.ui.add_zana_mod.addItem(zana_mod[ZanaMod.Name] + ' (' + zana_mod[ZanaMod.Cost] + ')')
            if int(self.parent.settings['ZanaDefaultModIndex']) == i:
                self.ui.add_zana_mod.setCurrentIndex(i)
            if int(self.parent.settings['ZanaLevel']) < int(zana_mod[ZanaMod.Level]):
                break # Stop adding mod options if Zana level is to low to run them

    def changeZanaMod(self):
        pass
        #self.parent.ui.mr_mods.moveCursor(QtGui.QTextCursor.End)

    def changeBonusIQ(self):
        pass

    def calcBonusIQ(self):
        zana_iq = int(self.zana_mods[self.ui.add_zana_mod.currentIndex()][ZanaMod.IQ])
        bonus_iq = self.ui.add_fragments.property('value') * 5 + zana_iq
        return bonus_iq

    def changeIQ(self):
        pass

    def changeIR(self):
        pass

    def changePackSize(self):
        pass

    def reset(self, defualts=False):
        iq = 0
        ir = 0
        ps = 0
        frags = 0
        if defualts:
            self.curLeague = self.ui.add_league.findText(self.parent.settings['DefualtLeague'])
            self.parent.mapDB.map_running[Map.League] = self.parent.settings['DefualtLeague']
            self.ui.add_zana_mod.setCurrentIndex(-1) # force change event
            self.curZanaMod = int(self.parent.settings['ZanaDefaultModIndex'])
            self.ui.add_zana_mod.setCurrentIndex(self.curZanaMod)
            self.ui.add_fragments.setProperty('value', frags)
            if Map.Mod1 in self.parent.mapDB.map_running and self.parent.mapDB.map_running[Map.Mod1] == 'Unidentified':
                self.ui.add_iq.setMinimum(30)
                self.curIQ = 30
                self.ui.add_iq.setProperty('value', 30)
                self.ui.add_iq.setEnabled(True)
                self.ui.add_ir.setProperty('value', 0)
                self.ui.add_ir.setEnabled(True)
                self.ui.add_pack_size.setProperty('value', 0)
                self.ui.add_pack_size.setEnabled(True)
            else:
                if Map.IQ in self.parent.mapDB.map_running:
                    iq = self.parent.mapDB.map_running[Map.IQ]
                self.ui.add_iq.setMinimum(0)
                self.ui.add_iq.setProperty('value', iq)
                self.ui.add_iq.setEnabled(False)
                if Map.IR in self.parent.mapDB.map_running:
                    ir = self.parent.mapDB.map_running[Map.IR]
                self.ui.add_ir.setProperty('value', ir)
                self.ui.add_ir.setEnabled(False)
                if Map.PackSize in self.parent.mapDB.map_running:
                    ps = self.parent.mapDB.map_running[Map.PackSize]
                self.ui.add_pack_size.setProperty('value', ps)
                self.ui.add_pack_size.setEnabled(False)
            if self.parent.mapDB.map_type_running == MapType.Fragment or self.parent.mapDB.map_type_running == MapType.RareFragment:
                self.ui.add_fragments.setEnabled(False)
            else:
                self.ui.add_fragments.setEnabled(True)
            self.accept()
        else:
            if Map.IQ in self.parent.mapDB.map_running:
                iq = self.parent.mapDB.map_running[Map.IQ]
            self.ui.add_iq.setProperty('value', iq)
            if Map.IR in self.parent.mapDB.map_running:
                ir = self.parent.mapDB.map_running[Map.IR]
            self.ui.add_ir.setProperty('value', ir)
            if Map.PackSize in self.parent.mapDB.map_running:
                ps = self.parent.mapDB.map_running[Map.PackSize]
            self.ui.add_pack_size.setProperty('value', ps)
            if Map.Fragments in self.parent.mapDB.map_running:
                frags = self.parent.mapDB.map_running[Map.Fragments]
            self.ui.add_fragments.setProperty('value', frags)
            self.ui.add_league.setCurrentIndex(self.curLeague)
            self.ui.add_zana_mod.setCurrentIndex(self.curZanaMod)
            self.ui.carto_box.setChecked(self.curCartoFound)
            self.ui.zana_box.setChecked(self.curZanaFound)
            self.ui.map_notes.setPlainText(self.curNotes)

    def accept(self):
        if self.parent.mapDB.map_running:
            self.parent.mapDB.map_running[Map.IQ] = self.ui.add_iq.property('value')
            self.parent.mapDB.map_running[Map.IR] = self.ui.add_ir.property('value')
            self.parent.mapDB.map_running[Map.PackSize] = self.ui.add_pack_size.property('value')
            self.parent.mapDB.map_running[Map.Fragments] = self.ui.add_fragments.property('value')
            self.parent.mapDB.map_running[Map.BonusIQ] = self.calcBonusIQ()
            self.curLeague = self.ui.add_league.currentIndex()
            self.parent.mapDB.map_running[Map.League] = self.leagues[self.curLeague]
            self.curZanaMod = self.ui.add_zana_mod.currentIndex()
            self.curCartoFound = self.ui.carto_box.checkState()
            self.curZanaFound = self.ui.zana_box.checkState()
            self.curNotes = self.ui.map_notes.toPlainText()
            self.parent.mapDB.map_running[Map.ZanaMod] = self.zana_mods[self.curZanaMod][ZanaMod.Desc]
            self.parent.mapDB.map_running[Map.CartoFound] = self.curCartoFound
            self.parent.mapDB.map_running[Map.ZanaFound] = self.curZanaFound
            self.parent.mapDB.map_running[Map.Notes] = self.curNotes
        super().accept()

    def exec_(self):
        if self.parent.mapDB.map_running:
            self.reset()
        return super().exec_()


class MapWatcher(QThread):

    trigger = pyqtSignal(object)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.check_interval = 2.0
        self.map_type = MapType.Standard
        self.map_check_str = r'\r?\n--------\r?\nTravel to this Map by using it in the Eternal Laboratory or a personal Map Device\. Maps can only be used once\.'
        self.fragment_check_str = r'\r?\n--------\r?\nCan be used in the Eternal Laboratory or a personal Map Device\.'
        self.corrupted_map_check_str = r'\r?\n--------\r?\nCorrupted'
        # I don't know how to include some of these within the current map tier system, 0,-1,-2 ?
        # How would they compare in statistics? Not sure about this anymore.
        # self.fragments = [
        #     {Map.TimeAdded: 0, Map.Name: 'Sacrifice at Dusk', Map.Tier: 66, Map.Rarity: 'Unique'},
        #     ['Sacrifice at Dawn', 67],
        #     ['Sacrifice at Noon', 68],
        #     ['Sacrifice at Midnight', 69],
        #     ['Mortal Grief', 70],
        #     ['Mortal Rage', 71],
        #     ['Mortal Ignorance', 72],
        #     ['Mortal Hope', 73]
        # ]
        self.atziri_maps = [
            {
                Map.TimeAdded: 0,
                Map.Name: 'The Apex of Sacrifice',
                Map.Tier: '3',
                Map.Rarity: 'Unique'
            },
            {
                Map.TimeAdded: 0,
                Map.Name: 'The Alluring Abyss',
                Map.Tier: '13',
                Map.IQ: '200',
                Map.Rarity: 'Unique',
                Map.Mod1: '100% Monsters Damage',
                Map.Mod2: '100% Monsters Life'
            }
        ]

    def __del__(self):
        self.exiting = True
        self.wait()
        super().__del__(self)

    def runLoop(self, running):
        self.start()

    def pause(self, pause):
        self.exiting = pause
        if not pause:
            self.start()

    def setMapCheckInterval(self, seconds):
        self.check_interval = seconds

    def parseMapData(self, copied_str, fragment=False, corrupted=False):
        map_data = {}
        map_data[Map.Corrupted] = "0"
        map_rarity = re.search(r'Rarity:\s(\w*)\n', copied_str)
        map_name1 = re.search(r'Rarity:\s\w*\n(.*)\n', copied_str)
        if fragment:
            if re.match(r'Sacrifice\sat', map_name1.group(1)):
                map_data = self.atziri_maps[0]
            else:
                map_data = self.atziri_maps[1]
            if re.match(r'Sacrifice\sat\sMidnight', map_name1.group(1)) or re.match(r'Mortal\sHope', map_name1.group(1)):
                self.map_type = MapType.RareFragment
            else:
                self.map_type = MapType.Fragment
            map_data[Map.TimeAdded] = time.time()
        else:
            if corrupted:
                self.map_type = MapType.Corrupted
                map_data[Map.Corrupted] = "1"
            else:
                self.map_type = MapType.Standard
            map_name2 = re.search(r'Rarity:\s\w*\n.*\n([^-].*)\n', copied_str)
            map_tier = re.search(r'Map\sTier:\s(\d*)\s', copied_str)
            map_iq = re.search(r'Item\sQuantity:\s\+(\d*)\%.*\n', copied_str)
            map_ir = re.search(r'Item\sRarity:\s\+(\d*)\%.*\n', copied_str)
            map_pack_size = re.search(r'Monster\sPack\sSize:\s\+(\d*)\%.*\n', copied_str)
            map_mods = []
            pattern = re.compile(r'Item\sLevel:\s\d*\n--------\n(.*)', re.DOTALL)
            remaining_data = re.search(pattern, copied_str)
            if remaining_data:
                map_mods = remaining_data.group(1).split('\n')
            map_data[Map.TimeAdded] = time.time()
            if map_rarity:
                print('Rarity: ' + map_rarity.group(1))
                map_data[Map.Rarity] = map_rarity.group(1)
            if map_name1 and map_name2:
                print('Map Name: ' + map_name1.group(1) + ' ' + map_name2.group(1))
                map_data[Map.Name] = map_name1.group(1) + ' ' + map_name2.group(1)
            elif map_name1:
                print('Map Name: ' + map_name1.group(1))
                map_data[Map.Name] = map_name1.group(1)
            if map_tier:
                print('Map Tier: ' + map_tier.group(1))
                map_data[Map.Tier] = map_tier.group(1)
            if map_iq:
                print('Map Item Quantity: ' + map_iq.group(1))
                map_data[Map.IQ] = map_iq.group(1)
            if map_ir:
                print('Map Item Rarity: ' + map_ir.group(1))
                map_data[Map.IR] = map_ir.group(1)
            if map_pack_size:
                print('Monster Pack Size: ' + map_pack_size.group(1))
                map_data[Map.PackSize] = map_pack_size.group(1)
            for i, mod in enumerate(map_mods):
                print('Map Mod ' + str(i+1) +': ' + mod)
                map_data[Map.Mod1 + i] = mod
                # Unidentified maps add 30% bonus IQ
                if mod == 'Unidentified':
                    map_data[Map.IQ] = '30'
        # Send signal to Update UI
        self.trigger.emit(map_data)

    # Note: This is never called directly. It is called by Qt once the thread environment has been set up.
    def run(self):
        while not self.exiting:
            copied_data = pyperclip.paste()
            if copied_data:
                if re.search(self.map_check_str, copied_data) and not re.search(r'Map Watch Time Stamp:', copied_data): # Ignore maps already checked with Time Stamp
                    print('====Found a Map====')
                    # Add time stamp to every map found
                    time_stamp = '========\r\nMap Watch Time Stamp: ' + str(time.time()) + '\r\n========\r\n'
                    pyperclip.copy(time_stamp + copied_data)
                    # Remove all Windows specific carriage returns (\r)
                    copied_data = copied_data.replace('\r', '')
                    # Check for a corrupted map
                    corrupted_map = re.search(self.corrupted_map_check_str, copied_data)
                    #print(corrupted_map)
                    # Remove quote on a unique map (if there) and all other unneeded data below
                    pattern = re.compile(r'.*--------.*--------.*--------.*(\n--------.*--------.*)', re.DOTALL)
                    extra_text = re.search(pattern, copied_data)
                    if (extra_text):
                        copied_data = copied_data.replace(extra_text.group(1), '')
                    else:
                        copied_data = re.sub(self.map_check_str, '', copied_data)
                    # Trim all new lines at end, just in case
                    while copied_data[-1:] == '\n':
                        print('Trimming \\n')
                        copied_data = copied_data[:-1]
                    print(copied_data)
                    self.parseMapData(copied_data, False, corrupted_map)
                elif re.search(self.fragment_check_str, copied_data) and not re.search(r'Map Watch Time Stamp:', copied_data):
                    print('====Found a Fragment====')
                    # Add time stamp to every fragment found
                    time_stamp = '========\r\nMap Watch Time Stamp: ' + str(time.time()) + '\r\n========\r\n'
                    pyperclip.copy(time_stamp + copied_data)
                    # Remove all Windows specific carriage returns (\r)
                    copied_data = copied_data.replace('\r', '')
                    self.parseMapData(copied_data, True)
            time.sleep(self.check_interval)


class MapDatabase(object):

    def __init__(self, parent=None):
        self.parent = parent
        self.table_names = ['Maps_Dropped','Maps_Ran']
        self.unique_col_name = 'Time_Stamp_ID'
        self.column_names = [['Dropped_In_ID','Name','Tier','IQ','IR','Pack_Size','Rarity',
                                'Mod1','Mod2','Mod3','Mod4','Mod5','Mod6','Mod7','Mod8','Mod9','Mod10',
                                'Mod11','Mod12','Mod13','Mod14','Mod15','Mod16','Mod17','Mod18','Corrupted'],
                            ['Time_Cleared','Name','Tier','IQ','Bonus_IQ','IR','Pack_Size','Rarity',
                                'Mod1','Mod2','Mod3','Mod4','Mod5','Mod6','Mod7','Mod8','Mod9','Mod10',
                                'Mod11','Mod12','Mod13','Mod14','Mod15','Mod16','Mod17','Mod18','Corrupted',
                                'Zana_Mod','League','Fragments','Carto_Found','Zana_Found','Notes']]
        self.map_running = None
        self.map_type_running = MapType.Standard
        self.db_file = None
        print('MapDatabase loaded')

    def setDBFile(self, file):
        self.db_file = file
        # TODO: get current map running? has to be saved into db with no time_cleared

    def countMapsAdded(self):
        self.openDB()
        map_count = 0
        try:
            self.c.execute("SELECT * FROM {tn}".format(tn=self.table_names[Maps.Dropped]))
            map_count = len(self.c.fetchall())
        except:
            self.parent.error('Error: A database table could not be found. Atziri corrupted your database file!', sys.exc_info())
        self.closeDB()
        return map_count

    def openDB(self):
        if self.db_file:
            self.conn = sqlite3.connect(self.db_file)
            self.c = self.conn.cursor()
        else:
            self.parent.error('Error: No database file found.', {'Please select a database file before adding any maps.'})

    def closeDB(self):
        if self.db_file:
            self.conn.close()

    def addMap(self, map, unlinked=False):
        if map is None:
            self.parent.error('Error: Database record could not be created.',
                {"No map has been selected. Copy (Ctrl+C) a map from Path of Exile first."})
            return None
        if self.map_running and map[Map.TimeAdded] == self.map_running[Map.TimeAdded]:
            self.parent.error('Error: Database record could not be created.',
                {
                "You can't add the map running to it's own map drops.",
                "This isn't Back to the Future where you go back in time and bang your own mother to create yourself."
                })
            return None
        self.openDB()
        map_name = None
        try:
            for field, value in map.items():
                if int(field) == Map.TimeAdded:
                    self.c.execute("INSERT INTO {tn} ({kcn}) VALUES ({val})".format(
                            tn=self.table_names[Maps.Dropped],
                            kcn=self.unique_col_name,
                            val=value
                        ))
                else:
                    self.c.execute("UPDATE {tn} SET {cn}=({val}) WHERE {kcn}=({key})".format(
                            tn=self.table_names[Maps.Dropped],
                            cn=self.column_names[Maps.Dropped][int(field)],
                            kcn=self.unique_col_name,
                            val='\"'+value+'\"',
                            key=map[Map.TimeAdded]
                        ))
            # Map found in
            if self.map_running and not unlinked:
                self.c.execute("UPDATE {tn} SET {cn}=({val}) WHERE {kcn}=({key})".format(
                        tn=self.table_names[Maps.Dropped],
                        cn=self.column_names[Maps.Dropped][0], # Dropped_In_ID
                        kcn=self.unique_col_name,
                        val=self.map_running[Map.TimeAdded],
                        key=map[Map.TimeAdded]
                    ))
            map_name = map[Map.Name]
            self.conn.commit()
            print('Map added to database')
        except sqlite3.IntegrityError:
            self.parent.error('Error: Database record already exists.',
                {"This map has already been added to the database. If you want you may delete it and re-add it though."})
        except:
            self.parent.error('Error: Database record could not be created.', sys.exc_info())
        self.closeDB()
        return map_name

    def runMap(self, map):
        if map is None:
            self.parent.error('Error: Database record could not be created.',
                {"No map has been selected. Copy (Ctrl+C) a map from Path of Exile first."})
            return False
        if self.map_running and map[Map.TimeAdded] == self.map_running[Map.TimeAdded]:
            self.parent.error('Error: Database record could not be created.',
                {"This map is already running. If you would like to clear it click the 'Map Clear' button."})
            return False
        self.parent.clearMap()
        self.map_type_running = self.parent.thread.map_type
        self.openDB()
        try:
            for field, value in map.items():
                if int(field) == Map.TimeAdded:
                    self.c.execute("INSERT INTO {tn} ({kcn}) VALUES ({val})".format(
                            tn=self.table_names[Maps.Ran],
                            kcn=self.unique_col_name,
                            val=value
                        ))
                else:
                    print(value)
                    self.c.execute("UPDATE {tn} SET {cn}=({val}) WHERE {kcn}=({key})".format(
                            tn=self.table_names[Maps.Ran],
                            cn=self.column_names[Maps.Ran][int(field)-1],
                            kcn=self.unique_col_name,
                            val='\"'+value+'\"',
                            key=map[Map.TimeAdded]
                        ))
            self.conn.commit()
            success = True
            self.map_running = copy.deepcopy(map)
        except:
            self.parent.error('Error: Database record could not be created.', sys.exc_info())
            success = False
        self.closeDB()
        return success

    def updateMapRunning(self):
        if self.map_running:
            print('updateMapRunning')
            self.openDB()
            try:
                print('here1')
                if Map.Mod1 in self.map_running and self.map_running[Map.Mod1] == 'Unidentified':
                    update_cols = {
                        'IQ': Map.IQ,
                        'IR': Map.IR,
                        'Pack_Size': Map.PackSize,
                        'Bonus_IQ': Map.BonusIQ,
                        'League': Map.League,
                        'Zana_Mod': Map.ZanaMod,
                        'Fragments': Map.Fragments,
                        'Carto_Found': Map.CartoFound,
                        'Zana_Found': Map.ZanaFound,
                        'Notes': Map.Notes
                    }.items()
                else:
                    print('here2')
                    update_cols = {
                        'Bonus_IQ': Map.BonusIQ,
                        'League': Map.League,
                        'Zana_Mod': Map.ZanaMod,
                        'Fragments': Map.Fragments,
                        'Carto_Found': Map.CartoFound,
                        'Zana_Found': Map.ZanaFound,
                        'Notes': Map.Notes
                    }.items()

                for col, i in update_cols:
                    self.c.execute("UPDATE {tn} SET {cn}=({val}) WHERE {kcn}=({key})".format(
                            tn=self.table_names[Maps.Ran],
                            cn=str(col),
                            kcn=self.unique_col_name,
                            val='\"'+str(self.map_running[i])+'\"',
                            key=self.map_running[Map.TimeAdded]
                        ))
                    print(col)
                self.conn.commit()
            except:
                self.parent.error('Error: Database record could not be updated.', sys.exc_info())
            self.closeDB()

    def clearMap(self):
        if self.map_running:
            self.updateMapRunning()
            print('Map Cleared')
            self.openDB()
            clear_time = time.time()
            try:
                # Add time map cleared
                self.c.execute("UPDATE {tn} SET {cn}=({val}) WHERE {kcn}=({key})".format(
                        tn=self.table_names[Maps.Ran],
                        cn=self.column_names[Maps.Ran][0], # Time_Cleared
                        kcn=self.unique_col_name,
                        val=clear_time,
                        key=self.map_running[Map.TimeAdded]
                    ))
                self.conn.commit()
                # Any map drops in this map?
                self.c.execute("SELECT * FROM {tn} WHERE {kcn} = (SELECT MAX({mr_kcn}) FROM {mr_tn})".format(
                        tn=self.table_names[Maps.Dropped],
                        kcn=self.column_names[Maps.Dropped][0], # Dropped_In_ID
                        mr_kcn=self.unique_col_name,
                        mr_tn=self.table_names[Maps.Ran]
                    ))
                self.map_running = None
            except:
                self.parent.error('Error: Database record could not be updated.', sys.exc_info())
            if not self.c.fetchone():
                self.parent.ui_confirm.boxType('confirmXL')
                if self.parent.ui_confirm.exec_('Delete Current Map Running?',
                                                'No Map Drops were found in this map.  '+
                                                'Is this correct or did you run this map by mistake and want to delete it from the database?  '+
                                                '\nSelect "No" if you want to record this map with no map drops.'):
                    map_name = self.deleteLastMap(Maps.Ran)
                    if map_name:
                        self.parent.sysTrayIcon.showMessage(
                            'Last Map Ran Deleted',
                            map_name+' was deleted from the database.',
                            1, 1000)
            self.closeDB()
        else:
            print('No Map to Clear')

    def deleteLastMap(self, from_table):
        self.openDB()
        map_name = None
        try:
            self.c.execute("SELECT * FROM {tn} WHERE {kcn} = (SELECT MAX({kcn}) FROM {tn})".format(
                    tn=self.table_names[from_table],
                    kcn=self.unique_col_name
                ))
            map_name = self.c.fetchone()[Map.Name]
            self.c.execute("DELETE FROM {tn} WHERE {kcn} = (SELECT MAX({kcn}) FROM {tn})".format(
                    tn=self.table_names[from_table],
                    kcn=self.unique_col_name
                ))
            self.conn.commit()
            print('Map Deleted')
        except:
            self.parent.error('Error: Database record could not be deleted.', sys.exc_info())
            map_name = 'Error'
        self.closeDB()
        return map_name

    def setupDB(self, file, db_struct_check=False):
        if not db_struct_check:
            print('Setting up new map database.')
            if os.path.exists(file):
                try:
                    # Overwrite old file
                    os.unlink(file)
                except:
                    self.parent.error('Error: Database could not be created.', sys.exc_info())
                    return False
            self.setDBFile(file)
        else:
            print('Checking database structure.')
        diff_struct = False
        self.openDB()
        for i, tname in enumerate(self.table_names):
            # Create a map table with unique Time_Stamp column
            self.c.execute('CREATE TABLE IF NOT EXISTS {tn} ({cn} REAL PRIMARY KEY)'.format(
                    tn=tname,
                    cn=self.unique_col_name
                ))
            # Get existing columns
            self.c.execute('PRAGMA table_info({tn})'.format(tn=tname))
            existing_columns = []
            for excol in self.c.fetchall():
                existing_columns.append(excol[1])
            # Check if database structure is different
            if existing_columns[1:] != self.column_names[i]:
                diff_struct = True
            # Create columns if they don't already exist
            for col in self.column_names[i]:
                if col not in existing_columns:
                    if col in ['Tier','IQ','Bonus_IQ','IR','Pack_Size','Corrupted','Fragments','Carto_Found','Zana_Found']:
                        col_type = 'INTEGER'
                    elif col in ['Dropped_In_ID','Time_Cleared']:
                        col_type = 'REAL'
                    else:
                        col_type = 'TEXT'
                    self.c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(
                            tn=tname,
                            cn=col,
                            ct=col_type
                        ))
        self.conn.commit()
        self.closeDB()
        if diff_struct and db_struct_check:
            self.parent.ui_confirm.boxType('error')
            self.parent.ui_confirm.exec_('Older DB File Detected',
                                        'An older database file from a previous version of Map Watch detected, and is no longer compatible.  '+
                                        'It is recommended you start a new database file.')
        return True


def writeSettings(settings, defaults=None):
    config = configparser.ConfigParser()
    default_settings = settingDefaults()
    if not settings:
        config['DEFAULT'] = default_settings
        config['CURRENT'] = default_settings
    else:
        if config.read('settings.ini'):
            if defaults: #update
                config['DEFAULT'] = defaults
            config['CURRENT'] = settings
        else:
            print('No settings file found.  Please restart application to create a default settings file.')
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)
        configfile.close()


def readSettings(defaults=False):
    config = configparser.ConfigParser()
    if config.read('settings.ini'):
        if defaults:
            return config['DEFAULT']
        else:
            verifySettings(config, 'CURRENT')
            return config['CURRENT']
    else:
        print('No settings file found, making new settings file with defaults.')
        writeSettings({})
        return readSettings()


def verifySettings(config, section):
    missing_option = False
    default_settings = settingDefaults()
    for option, value in default_settings.items():
        if not config.has_option(section, option):
            config.set(section, option, value)
            config.set('DEFAULT', option, value)
            missing_option = True
    if missing_option:
        writeSettings(config[section], config['DEFAULT'])


def settingDefaults():
    abs_path = os.path.abspath(os.path.dirname('__file__'))
    return {
            'MapCheckInterval': '2.0',
            'AlwaysOnTop': '2',
            'Language': 'English',
            'LastOpenedDB': abs_path+'\\data\\mw_db001.sqlite',
            'LoadLastOpenedDB': '2',
            'SelectedStatisticsFile': abs_path+'\\statistics\\stat_file_01.html',
            'ShowMilliseconds': '0',
            'ClockHour12': '2',
            'DefualtLeague': 'Standard',
            'ZanaLevel': '8',
            'ZanaDefaultModIndex': '1'
            }


def writeSettingsJS(settings):
    if not settings:
        settings = {'hour12': True, 'milliseconds': False}
    settings = json.JSONEncoder().encode(settings)
    settings = 'var settings = '+settings
    with open('js\settings.js', 'w') as outfile:
        outfile.write(settings)


def readData(data='all'):
    config = configparser.ConfigParser()
    if config.read('data.ini'):
        if data == 'all':
            return config
        if data == 'Zanamods':
            return config['ZANAMODS']
        elif data == 'Leagues':
            return config['LEAGUES']
    else:
        print('No data file found.')
        return None


def main():
    app = QtWidgets.QApplication(sys.argv)
    mw_ui = MapWatchWindow()
    mw_ui.show()

    # All this just to steal focus, damn it Microsoft
    win32gui.EnumWindows(mw_ui._window_enum_callback, r'Map Watch \(')
    pywinapp = pywinauto.application.Application()
    if mw_ui._handle:
        mw_ui.window = pywinapp.window_(handle=mw_ui._handle)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
