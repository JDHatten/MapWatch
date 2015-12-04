:: All the directories
if not exist "%~dp0\MapWatch\css" mkdir %~dp0\MapWatch\css
if not exist "%~dp0\MapWatch\data" mkdir %~dp0\MapWatch\data
if not exist "%~dp0\MapWatch\images" mkdir %~dp0\MapWatch\images
if not exist "%~dp0\MapWatch\js" mkdir %~dp0\MapWatch\js
if not exist "%~dp0\MapWatch\statistics" mkdir %~dp0\MapWatch\statistics

:: CSS Files

:: Data Files

:: Image Files
xcopy /s/y %~dp0\images\header.png %~dp0\MapWatch\images\
xcopy /s/y %~dp0\images\button.png %~dp0\MapWatch\images\
xcopy /s/y %~dp0\images\details_close.png %~dp0\MapWatch\images\
xcopy /s/y %~dp0\images\details_open.png %~dp0\MapWatch\images\
xcopy /s/y %~dp0\images\background-fm.jpg %~dp0\MapWatch\images\
xcopy /s/y %~dp0\images\icon.ico %~dp0\MapWatch\images\

:: Javascript Files
xcopy /s/y %~dp0\js\sql.js %~dp0\MapWatch\js\
xcopy /s/y %~dp0\js\map_names.js %~dp0\MapWatch\js\

:: Readme and License
copy %~dp0\README.md %~dp0\MapWatch\readme.txt
copy %~dp0\LICENSE %~dp0\MapWatch\license.txt

:: Statistics Files
xcopy /s/y %~dp0\statistics\stat_file_01.html %~dp0\MapWatch\statistics\

:: Compile scripts to a Windows exe
python34 setup.py py2exe --includes sip
