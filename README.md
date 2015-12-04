# MapWatch
#### A Path of Exile application that collects and reports map drop data and statistics.


![MapWatch]( http://i.imgur.com/10BCzec.png "Map Watch - Main Window")


### Description:
*Map Watch* is an application that records map drops in the game Path of Exile.  Once enough data is collected it can show different statistics on the map drops recorded via a local webpage.  


### Use:
You can run the Python script in version 3.4 or download the full release that includes a Windows exe that any Windows PC should be able to run.  While in game the application will run in the background and it will popup once a player finds and copies a map's data to the clipboard.  To do this, simply highlight a map in your inventory and press Ctrl+C.  
	
Once a map is selected you can choose to add it to your map drops or run it.  If you choose to run the map, all future map drops that you add will be linked to this map until you select map cleared.  Maps can also be added unlinked to any map currently running and removed (in order added) from the database.

Once a suitable about of map data has been collected you can open a statistics file.  These files will show many charts, tables, and otherwise useful information regarding your mapping progress in the game Path of Exile.  


### Important Note:
It is highly recommended you play Path of Exile in a **Windowed Mode** while using this application.  Playing in Full Screen will cause problems that may lead to your death in game (i.e. the game might minimize).  Don't say I didn't warn you.

For version 0.2+ it is recommended you start a new database file (or overwrite existing).  Some statistics might be incorrect because of a change in the database structure.  


### Keyboard Shortcuts:
| Action | Shortcut |
| :----- | :------: |
| Add Map | A |
| Add Unlinked Map | Ctrl + U |
| Remove Map | Ctrl + D |
| Clear Map | Ctrl + X |
| Run Map | Ctrl + R |
| Focus Zana Mods | Z |
| Focus Bonus IQ | Q |
| New DB File | F1 |
| Load DB File | F2 |
| Open Stat File | F3 |
| Preferences | F4 |
| About | F5 |
| Exit | F12 |


### Sample Map Data:
This can be used to test the Map Watch application without having to run Path of Exile.  Simply highlight and copy the complete block of text below while the application is running.
```
Rarity: Rare
Destiny Spires
Volcano Map
--------
Map Tier: 10
Item Quantity: +69% (augmented)
Item Rarity: +40% (augmented)
Monster Pack Size: +15% (augmented)
--------
Item Level: 78
--------
Area has increased monster variety
Area has patches of desecrated ground
Area is inhabited by 2 additional Rogue Exiles
Players Recover Life, Mana and Energy Shield 40% slower
+60% Monster Lightning Resistance
--------
Travel to this Map by using it in the Eternal Laboratory or a personal Map Device. Maps can only be used once.
```

### Versions:
*0.2*
* *New:* Added Zana mods and Bonus IQ that can be added to running maps
* Added two more general statistics to stat_file_01.html
* Added many keyboard shortcuts for different actions
* Added some time formatting options
* Added new regex that is more portable for non-Windows users
* Added some clearer database error messages
* *Fixes:* Maps now auto clear and record time cleared when a new map is selected to be ran.
* Some statistics math has been corrected in stat_file_01.html
* Default settings in settings.ini file can now be changed and restored
* The Map Watch window now properly gains/steals focus when a map is selected

*0.1*
* Initial Release


### Licensing:
Map Watch is licensed under the GNU GENERAL PUBLIC LICENSE Version 2.  Please see the file called LICENSE for more info.

sql.js uses the MIT LICENSE.


### Contacts:
Email:  Jonathan.D.Hatten(at)gmail(dot)com

Path of Exile IGN:  Grahf_Azura
