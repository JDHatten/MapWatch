:: All the directories
if not exist "%~dp0\dist\css" mkdir %~dp0\dist\css
if not exist "%~dp0\dist\data" mkdir %~dp0\dist\data
if not exist "%~dp0\dist\images" mkdir %~dp0\dist\images
if not exist "%~dp0\dist\js" mkdir %~dp0\dist\js
if not exist "%~dp0\dist\statistics" mkdir %~dp0\dist\statistics

:: CSS Files

:: Data Files

:: Image Files
xcopy /s/y %~dp0\images\header.png %~dp0\dist\images\
xcopy /s/y %~dp0\images\button.png %~dp0\dist\images\
xcopy /s/y %~dp0\images\details_close.png %~dp0\dist\images\
xcopy /s/y %~dp0\images\details_open.png %~dp0\dist\images\
xcopy /s/y %~dp0\images\background-fm.jpg %~dp0\dist\images\
xcopy /s/y %~dp0\images\icon.ico %~dp0\dist\images\

:: Javascript Files
xcopy /s/y %~dp0\js\sql.js %~dp0\dist\js\

:: Template Files
xcopy /s/y %~dp0\statistics\stat_file_01.html %~dp0\dist\statistics\

:: Compile scripts to a Windows exe
python34 setup.py py2exe --includes sip