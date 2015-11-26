import sys
import os
import re
import msvcrt
import sqlite3
import time
import datetime
import pyperclip
import configparser
import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets   # TODO: later only take those classes you use and not the whole module, i.e. from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal, Qt, QThread
from PyQt5.QtWidgets import QFileDialog
from window import Ui_MainWindow
from confirm import Ui_Confirm
from preferences import Ui_Preferences

# TODOS: 
### Create custom icons
### Create more HTML statistic files
### am/pm time option
### 
###

class Map():
    TimeAdded = 0
    Name = 1
    Tier = 2
    IQ = 3
    IR = 4
    PackSize = 5
    Rarity = 6
    Mod1 = 7
    Mod2 = 8
    Mod3 = 9
    Mod4 = 10
    Mod5 = 11
    Mod6 = 12
    Mod7 = 13
    Mod8 = 14
    Mod9 = 15
    ModList = 16

class Maps():
    Dropped = 0
    Ran = 1

class MapWatchWindow(QtWidgets.QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # General Settings
        self.appTitle = 'Map Watch (v0.1)'
        self.setWindowTitle(self.appTitle)
        self.setWindowIcon(QtGui.QIcon(r'images\\icon.ico'))
        self.setWindowFlags(Qt.CustomizeWindowHint|Qt.WindowCloseButtonHint|Qt.WindowStaysOnTopHint|Qt.X11BypassWindowManagerHint)
        self.firstClose = 1
        self.settings = readSettings()
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
        icon = QtGui.QIcon('')
        exitAction = QtWidgets.QAction(icon, '&Exit', self)
        exitAction.triggered.connect(self.closeApplication)
        menu.addAction(exitAction)
        self.sysTrayIcon.setContextMenu(menu)
        # This will do the Map Watching in a different thread
        self.thread = MapWatcher()
        self.thread.runLoop()
        self.thread.trigger.connect(self.updateUiMapSelected)  # Triggered when new map found
        # Configure UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui_confirm = ConfirmDialog(self)
        self.ui_prefs = Preferences(self)
        self.setPrefs()
        # Button Actions
        self.ui.ms_add_map.clicked.connect(self.addMap)
        self.ui.ms_remove_map.clicked.connect(self.removeMap)
        self.ui.mr_clear_map.clicked.connect(self.clearMap)
        self.ui.mr_run_map.clicked.connect(self.runMap)
        # Menu Actions
        self.ui.menu_create_new_db.triggered.connect(lambda: self.setDBFile(True))
        self.ui.menu_load_db.triggered.connect(self.setDBFile)
        self.ui.menu_open_stats.triggered.connect(self.openStatFile)
        self.ui.menu_exit_app.triggered.connect(self.closeApplication)
        self.ui.menu_ms_add_map.triggered.connect(self.addMap)
        self.ui.menu_ms_add_unlinked_map.triggered.connect(lambda: self.addMap(True))
        self.ui.menu_ms_remove_map.triggered.connect(self.removeMap)
        self.ui.menu_mr_clear_map.triggered.connect(self.clearMap)
        self.ui.menu_mr_run_map.triggered.connect(self.runMap)
        self.ui.menu_preferences.triggered.connect(self.getPrefs)
        self.ui.menu_about.triggered.connect(self.about)
        # Setup Map Database
        self.map_data = None
        self.mapDB = MapDatabase(self)
        if int(self.settings['LoadLastOpenedDB']):
            if os.path.exists(self.settings['LastOpenedDB']):
                self.mapDB.setDBFile(self.settings['LastOpenedDB'])
            else:
                self.mapDB.setupDB(self.settings['LastOpenedDB'])
            self.updateWindowTitle()

    def restore(self, action):
        if action == self.sysTrayIcon.DoubleClick:
            self.popup()

    def popup(self):
        self.showNormal()
        self.activateWindow()
        self.show()

    def updateUiMapSelected(self, map_data):
        print('UI Updated')
        self.popup()
        self.map_data = map_data
        # Clear those items that may not be updated with new map
        self.ui.ms_iq.setText('0%')
        self.ui.ms_ir.setText('0%')
        self.ui.ms_pack_size.setText('0%')
        self.ui.ms_mods.setText('None')
        # Get each piece of map info and update UI lables, etc
        if Map.TimeAdded in map_data:
            time_added = datetime.datetime.fromtimestamp(map_data[Map.TimeAdded]).strftime('%H:%M:%S')
            self.ui.ms_time_stamp.setText(time_added)
        if Map.Name in map_data:
            self.ui.ms_name.setText(map_data[Map.Name])
        if Map.Tier in map_data:
            level = int(map_data[Map.Tier]) + 67
            self.ui.ms_tier.setText(map_data[Map.Tier] + '  (' + str(level) + ')')
        if Map.IQ in map_data:
            self.ui.ms_iq.setText(map_data[Map.IQ]+'%')
        if Map.IR in map_data:
            self.ui.ms_ir.setText(map_data[Map.IR]+'%')
        if Map.PackSize in map_data:
            self.ui.ms_pack_size.setText(map_data[Map.PackSize]+'%')
        if Map.Rarity in map_data:
            rarity = map_data[Map.Rarity]
            self.ui.ms_rarity.setText(rarity)
            if rarity == 'Rare':
                self.ui.ms_name.setStyleSheet("color: rgb(170, 170, 0);")
            elif rarity == 'Magic':
                self.ui.ms_name.setStyleSheet("color: rgb(0, 85, 255);")
            elif rarity == 'Unique':
                self.ui.ms_name.setStyleSheet("color: rgb(170, 85, 0);")
            else:
                self.ui.ms_name.setStyleSheet("color: rgb(0, 0, 0);")
        if Map.Mod1 in map_data:
            all_mods = map_data[Map.Mod1] + '\r\n'
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod2 in map_data:
            all_mods = all_mods + map_data[Map.Mod2] + '\r\n'
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod3 in map_data:
            all_mods = all_mods + map_data[Map.Mod3] + '\r\n'
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod4 in map_data:
            all_mods = all_mods + map_data[Map.Mod4] + '\r\n'
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod5 in map_data:
            all_mods = all_mods + map_data[Map.Mod5] + '\r\n'
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod6 in map_data:
            all_mods = all_mods + map_data[Map.Mod6] + '\r\n'
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod7 in map_data:
            all_mods = all_mods + map_data[Map.Mod7] + '\r\n'
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod8 in map_data:
            all_mods = all_mods + map_data[Map.Mod8] + '\r\n'
            self.ui.ms_mods.setText(all_mods)
        if Map.Mod9 in map_data:
            all_mods = all_mods + map_data[Map.Mod9]
            self.ui.ms_mods.setText(all_mods)
        # if Map.ModList in map_data:
        #     all_mods = ''
        #     #print(map_data[Map.ModList])
        #     for mod in map_data[Map.ModList]:
        #         all_mods = all_mods + mod + '\r\n'
        #         self.ui.ms_mods.setText(all_mods)
        #     print(self.ui.ms_mods.toPlainText())

    def updateUiMapRunning(self, clear = False):
        print('UI Updated')
        if clear:
            self.ui.mr_name.setText('None')
            self.ui.mr_tier.setText('0')
            self.ui.mr_iq.setText('0%')
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
            rarity = self.ui.ms_rarity.text()
            if rarity == 'Rare':
                self.ui.mr_name.setStyleSheet("color: rgb(170, 170, 0);")
            elif rarity == 'Magic':
                self.ui.mr_name.setStyleSheet("color: rgb(0, 85, 255);")
            elif rarity == 'Unique':
                self.ui.mr_name.setStyleSheet("color: rgb(170, 85, 0);")
            else:
                self.ui.mr_name.setStyleSheet("color: rgb(0, 0, 0);")

    def removeMap(self):
        print('Removing Last Map')
        self.ui_confirm.boxType('confirm')
        del_map = None
        if self.ui_confirm.exec_('Remove Map?', 'Are you sure you want to delete the last map saved to database?'):
            del_map = self.mapDB.deleteLastMap(Maps.Dropped)
            self.updateWindowTitle()
        if del_map:
            self.sysTrayIcon.showMessage(
                'Last Map Removed',
                del_map+' was removed from the database.',
                1, 1000)

    def addMap(self, unlinked = False):
        print('Adding to Map Drops')
        self.minimizeToSysTray()
        self.ui_confirm.boxType('confirm')
        add_map = self.mapDB.addMap(self.map_data, unlinked)
        if add_map:
            self.updateWindowTitle()
            self.sysTrayIcon.showMessage(
                'Map Added',
                add_map+' was added to the database.',
                1, 1000)

    def clearMap(self):
        self.ui_confirm.boxType('confirm')
        if self.ui_confirm.exec_('Map Cleared?', 'Is the map cleared?  No more map drops will be linked to this map.'):
            self.mapDB.clearMap()
            self.updateUiMapRunning(True)

    def runMap(self):
        print('Running Selected Map')
        if self.mapDB.runMap(self.map_data):
            self.updateUiMapRunning()

    def setDBFile(self, new = False):
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
            self.updateWindowTitle()
            self.settings['LastOpenedDB'] = file_name[0]
            writeSettings(self.settings)

    def openStatFile(self):
        stat_file = self.settings['SelectedStatisticsFile']
        webbrowser.open('file://' + stat_file)

    def getPrefs(self):
        if self.ui_prefs.exec_():
            self.setPrefs()

    def setPrefs(self):
        self.settings = readSettings()
        self.thread.setMapCheckInterval(int(self.settings['MapCheckInterval']))
        print("Preferences Updated")

    def about(self):
        version = '0.1'
        self.ui_confirm.boxType('about')
        self.ui_confirm.exec_('About', 'Map Watch\nVersion '+version+'\n\nCreated by\nJonathan.D.Hatten@gmail.com\nIGN: Grahf_Azura')

    def updateWindowTitle(self):
        map_count = self.mapDB.countMapsAdded()
        self.setWindowTitle(self.appTitle + ' ---> ' + str(map_count) +' map drops in database (' + os.path.basename(self.mapDB.db_file) + ')')

    def error(self, err_msg, errors):
        err_msg += '\n'
        for err in errors:
            err_msg += '\n'+str(err)
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
                'Map Watch will still continue to run in the background.  Right click and select exit to shut down application.',
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
            self.ui.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Yes)
        if type is 'confirmXL':
            self.setFixedSize(270, 119)
            self.ui.buttonBox.setGeometry(QtCore.QRect(10, 90, 251, 23))
            self.ui.message.setGeometry(QtCore.QRect(10, 0, 251, 91))
            self.ui.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Yes)
        elif type is 'error':
            self.setFixedSize(270, 199)
            self.ui.buttonBox.setGeometry(QtCore.QRect(10, 170, 251, 23))
            self.ui.message.setGeometry(QtCore.QRect(10, 0, 251, 161))
            self.ui.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        elif type is 'about':
            self.setFixedSize(270, 189)
            self.ui.buttonBox.setGeometry(QtCore.QRect(10, 160, 251, 23))
            self.ui.message.setGeometry(QtCore.QRect(10, 0, 251, 141))
            self.ui.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)


class Preferences(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.setFixedSize(400, 225)
        self.loadData()
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Discard).clicked.connect(self.reject)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.RestoreDefaults).clicked.connect(self.restoreDefaults)
        print("Preferences Window loaded")

    def loadData(self):
        abs_path = os.path.abspath(os.path.dirname('__file__'))
        statistics_dir = abs_path+'\\statistics\\'
        file_names = os.listdir(statistics_dir)
        self.statistics_files = []
        for file_name in file_names:
            match = re.search(r'\w+\.html', file_name)
            if match:
                self.statistics_files.append(statistics_dir+file_name)

    def insertPrefs(self):
        self.ui.pref_interval.setProperty('value', int(self.parent.settings['MapCheckInterval']))
        self.ui.pref_startup.setChecked(int(self.parent.settings['LoadLastOpenedDB']))
        self.ui.pref_db_path.setText((self.parent.settings['LastOpenedDB']))
        self.ui.pref_statistics.clear()
        i = 0
        for stat_file in self.statistics_files:
            self.ui.pref_statistics.addItem(os.path.basename(stat_file))
            if stat_file == self.parent.settings['SelectedStatisticsFile']:
                self.ui.pref_statistics.setCurrentIndex(i)
            i += 1

    def restoreDefaults(self):
        self.parent.ui_confirm.boxType('confirm')
        if self.parent.ui_confirm.exec_('Restore Defaults?', 'Are you sure you want to restore the default settings?'):
            writeSettings({})
            self.parent.settings = readSettings()
            self.insertPrefs(parent.settings)

    def accept(self):
        self.parent.settings['MapCheckInterval'] = str(self.ui.pref_interval.property('value'))
        self.parent.settings['LoadLastOpenedDB'] = str(self.ui.pref_startup.checkState())
        self.parent.settings['SelectedStatisticsFile'] = self.statistics_files[self.ui.pref_statistics.currentIndex()]
        writeSettings(self.parent.settings)
        super().accept()

    def exec_(self):
        self.insertPrefs()
        return super().exec_()


class MapWatcher(QThread):

    trigger = pyqtSignal(object)

    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.check_interval = 3

    def __del__(self):
        self.exiting = True
        self.wait()

    def runLoop(self):
        self.start()

    def setMapCheckInterval(self, seconds):
        self.check_interval = seconds;

    def parseMapData(self, copied_str):
        # Windows specific RE used here (\r)
        map_rarity =    re.search(r'Rarity:\s(\w*)\r\s', copied_str) 
        map_name1 =     re.search(r'Rarity:\s\w*\r\s(.*)\r\s', copied_str)
        map_name2 =     re.search(r'Rarity:\s\w*\r\s.*\r\s(.*[^\-])\r\s', copied_str)
        map_tier =      re.search(r'Map\sTier:\s(\d*)\r\s', copied_str)
        map_iq =        re.search(r'Item\sQuantity:\s\+(\d*)\%.*\r\s', copied_str)
        map_ir =        re.search(r'Item\sRarity:\s\+(\d*)\%.*\r\s', copied_str)
        map_pack_size = re.search(r'Monster\sPack\sSize:\s\+(\d*)\%.*\r\s', copied_str)
        map_mod1 =      re.search(r'Item\sLevel:\s\d*\r\s.*\r\s(.*)', copied_str)
        map_mod2 =      re.search(r'Item\sLevel:\s\d*\r\s.*\r\s.*\r\s(.*)', copied_str)
        map_mod3 =      re.search(r'Item\sLevel:\s\d*\r\s.*\r\s.*\r\s.*\r\s(.*)', copied_str)
        map_mod4 =      re.search(r'Item\sLevel:\s\d*\r\s.*\r\s.*\r\s.*\r\s.*\r\s(.*)', copied_str)
        map_mod5 =      re.search(r'Item\sLevel:\s\d*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s(.*)', copied_str)
        map_mod6 =      re.search(r'Item\sLevel:\s\d*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s(.*)', copied_str)
        map_mod7 =      re.search(r'Item\sLevel:\s\d*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s(.*)', copied_str)
        map_mod8 =      re.search(r'Item\sLevel:\s\d*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s(.*)', copied_str)
        map_mod9 =      re.search(r'Item\sLevel:\s\d*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s.*\r\s(.*)', copied_str)
        map_data = {}
        #map_mods = []
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
        if map_mod1:
            print('Map Mods: \r\n' + map_mod1.group(1))
            # Unidentified maps add 30% bonus IQ
            mod1 = map_mod1.group(1).replace('\r', '')
            if mod1 == 'Unidentified':
                map_data[Map.IQ] = '30'
                #map_data[Map.IR] = '?'
                #map_data[Map.PackSize] = '?'
            #map_mods.append(mod1)
            map_data[Map.Mod1] = mod1
        if map_mod2:
            print(map_mod2.group(1))
            #map_mods.append(map_mod2.group(1).replace('\r', ''))
            map_data[Map.Mod2] = map_mod2.group(1).replace('\r', '')
        if map_mod3:
            print(map_mod3.group(1))
            #map_mods.append(map_mod3.group(1).replace('\r', ''))
            map_data[Map.Mod3] = map_mod3.group(1).replace('\r', '')
        if map_mod4:
            print(map_mod4.group(1))
            #map_mods.append(map_mod4.group(1).replace('\r', ''))
            map_data[Map.Mod4] = map_mod4.group(1).replace('\r', '')
        if map_mod5:
            print(map_mod5.group(1))
            #map_mods.append(map_mod5.group(1).replace('\r', ''))
            map_data[Map.Mod5] = map_mod5.group(1).replace('\r', '')
        if map_mod6:
            print(map_mod6.group(1))
            #map_mods.append(map_mod6.group(1).replace('\r', ''))
            map_data[Map.Mod6] = map_mod6.group(1).replace('\r', '')
        if map_mod7:
            print(map_mod7.group(1))
            #map_mods.append(map_mod7.group(1).replace('\r', ''))
            map_data[Map.Mod7] = map_mod7.group(1).replace('\r', '')
        if map_mod8:
            print(map_mod8.group(1))
            #map_mods.append(map_mod8.group(1).replace('\r', ''))
            map_data[Map.Mod8] = map_mod8.group(1).replace('\r', '')
        if map_mod9:
            print(map_mod9.group(1))
            #map_mods.append(map_mod9.group(1).replace('\r', ''))
            map_data[Map.Mod9] = map_mod9.group(1).replace('\r', '')
        # if map_mods:
        #     map_data[Map.ModList] = map_mods
        # Send signal to Update UI
        self.trigger.emit(map_data)

    # Note: This is never called directly. It is called by Qt once the thread environment has been set up.
    def run(self):
        map_check_str = r'\r\s--------\r\sTravel to this Map by using it in the Eternal Laboratory or a personal Map Device\. Maps can only be used once\.'
        while not self.exiting:
            copied_data = pyperclip.paste()
            if copied_data: #TODO: This doesn't work when no data has been copied since boot.  Need fix
                if re.search(map_check_str, copied_data) and not re.search(r'Map Watch Time Stamp:', copied_data): # Ignore maps already checked with Time Stamp
                    print('====Found a Map====')
                    # Add time stamp to every map found
                    time_stamp = '========\r\nMap Watch Time Stamp: ' + str(time.time()) + '\r\n========\r\n'
                    pyperclip.copy(time_stamp + copied_data)
                    # Remove quote on a unique map (if there) and all other info below
                    pattern = re.compile(r'.*--------.*--------.*--------.*(\r\n--------.*--------.*)', re.DOTALL)
                    extra_text = re.search(pattern, copied_data)
                    if (extra_text):
                        copied_data = copied_data.replace(extra_text.group(1), '')
                    else:
                        copied_data = re.sub(map_check_str, '', copied_data)
                    # Trim all new lines at end, just in case
                    while copied_data[-2:] == '\r\n':
                        print('Trimming \\r\\n')
                        copied_data = copied_data[:-2]
                    self.parseMapData(copied_data)
            time.sleep(self.check_interval)


class MapDatabase(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.table_names = ['Maps_Dropped','Maps_Ran']
        self.unique_col_name = 'Time_Stamp_ID'
        self.column_names = [['Name','Tier','IQ','IR','Pack_Size','Rarity','Mod1','Mod2','Mod3','Mod4','Mod5','Mod6','Mod7','Mod8','Mod9','Dropped_In_ID'],
                             ['Name','Tier','IQ','IR','Pack_Size','Rarity','Mod1','Mod2','Mod3','Mod4','Mod5','Mod6','Mod7','Mod8','Mod9','Time_Cleared']]
        self.map_running = None
        print('MapDatabase loaded')

    def setDBFile(self, file):
        self.db_file = file
        # TODO: get current map running? has to be saved into db
        # TODO: check for tables and see if this DB file has beed setup. If not show error

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
        self.conn = sqlite3.connect(self.db_file)
        self.c = self.conn.cursor()

    def closeDB(self):
        self.conn.close()

    def addMap(self, map, unlinked = False):
        if map is None:
            return None
        self.openDB()
        map_name = None
        try:
            for field, value in map.items():
                if int(field) == Map.TimeAdded:
                    # Note: Will throw error when adding a map that already exist (Time_Stamp) with no "INSERT OR IGNORE".  Do I want this behavior?
                    self.c.execute("INSERT INTO {tn} ({kcn}) VALUES ({val})".format(tn=self.table_names[0], kcn=self.unique_col_name, val=value))
                    map_name = map[Map.Name]
                else:
                    self.c.execute("UPDATE {tn} SET {cn}=({val}) WHERE {kcn}=({key})".format(
                            tn=self.table_names[Maps.Dropped], 
                            cn=self.column_names[Maps.Dropped][int(field)-1],
                            kcn=self.unique_col_name,
                            val='\"'+value+'\"',
                            key=map[Map.TimeAdded]
                        ))
            # Map found in
            if self.map_running and not unlinked:
                self.c.execute("UPDATE {tn} SET {cn}=({val}) WHERE {kcn}=({key})".format(
                        tn=self.table_names[Maps.Dropped],
                        cn=self.column_names[Maps.Dropped][15], # Dropped_In_ID
                        kcn=self.unique_col_name,
                        val=self.map_running[Map.TimeAdded],
                        key=map[Map.TimeAdded]
                    ))
            self.conn.commit()
            print('Adding Map')
        except:
            self.parent.error('Error: Database record could not be created.', sys.exc_info())
        self.closeDB()
        return map_name

    def runMap(self, map):
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
                    self.c.execute("UPDATE {tn} SET {cn}=({val}) WHERE {kcn}=({key})".format(
                            tn=self.table_names[Maps.Ran],
                            cn=self.column_names[Maps.Ran][int(field)-1],
                            kcn=self.unique_col_name,
                            val='\"'+value+'\"',
                            key=map[Map.TimeAdded]
                        ))
            self.conn.commit()
            success = True
            self.map_running = map
        except:
            self.parent.error('Error: Database record could not be created.', sys.exc_info())
            success = False
            #self.map_running = None
        self.closeDB()
        return success

    def clearMap(self):
        if self.map_running:
            print('Map Cleared')
            self.openDB()
            clear_time = time.time()
            try:
                # Add time map cleared
                self.c.execute("UPDATE {tn} SET {cn}=({val}) WHERE {kcn}=({key})".format(
                        tn=self.table_names[Maps.Ran],
                        cn=self.column_names[Maps.Ran][15], # Time_Cleared
                        kcn=self.unique_col_name,
                        val=clear_time,
                        key=self.map_running[Map.TimeAdded]
                    ))
                self.conn.commit()
                # Any map drops in this map?
                self.c.execute("SELECT * FROM {tn} WHERE {kcn} = (SELECT MAX({mr_kcn}) FROM {mr_tn})".format(
                        tn=self.table_names[Maps.Dropped],
                        kcn=self.column_names[Maps.Dropped][15], # Dropped_In_ID
                        mr_kcn=self.unique_col_name,
                        mr_tn=self.table_names[Maps.Ran]
                    ))
                self.map_running = None
            except:
                self.parent.error('Error: Database record could not be updated.', sys.exc_info())
            if not self.c.fetchone():
                self.parent.ui_confirm.boxType('confirmXL')
                if self.parent.ui_confirm.exec_('Delete Map?', 
                                                'No Map Drops were found in this map.  '+
                                                'Is this correct or did you run this map by mistake and want to delete it from the database?'):
                    map_name = self.deleteLastMap(Maps.Ran)
                    if map_name:
                        self.parent.sysTrayIcon.showMessage(
                            'Last Map Ran Removed',
                            map_name+' was removed from the database.',
                            1, 1000)
                else:
                    print('No mistake here, keep the map.')
            else:
                print('Map drops found don\'t ask to delete.')
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
        self.closeDB()
        return map_name

    def setupDB(self, file):
        print('Setting up new map database.')
        if os.path.exists(file):
            os.unlink(file) # Overwrite old file
        self.setDBFile(file)
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
            # Create columns if they don't already exist
            for col in self.column_names[i]:
                if col not in existing_columns:
                    if col in ['Tier','IQ','IR','Pack_Size']:
                        col_type = 'INTEGER'
                    elif col == self.column_names[i][15]: # Dropped_In_ID / Time_Cleared
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


def writeSettings(settings):
    config = configparser.ConfigParser()
    abs_path = os.path.abspath(os.path.dirname('__file__'))
    default_settings = {
                        'MapCheckInterval': '3',
                        'Language': 'English',
                        'LastOpenedDB': abs_path+'\\data\\mw_db001.sqlite',
                        'LoadLastOpenedDB': '2',
                        'SelectedStatisticsFile': abs_path+'\\statistics\\stat_file_01.html'
                        }
    config['DEFAULT'] = default_settings
    if not settings:
        config['CURRENT'] = default_settings
    else:
        config['CURRENT'] = settings
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)
        configfile.close()


def readSettings():
    config = configparser.ConfigParser()
    if config.read('settings.ini'):
        return config['CURRENT']
    else:
        print('No settings file found, making new settings file with defaults.')
        writeSettings({})
        return readSettings()


def main():
    app = QtWidgets.QApplication(sys.argv)
    mw_ui = MapWatchWindow()
    mw_ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
