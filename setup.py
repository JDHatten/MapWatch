from distutils.core import setup
import py2exe
#setup(console=['mapwatch.py'])
setup(
    data_files=[
        ('imageformats', [
            r'C:\\Python34\\Lib\\site-packages\\PyQt5\\plugins\\imageformats\\qico.dll'
        ]),
        ('platforms', [
            r'C:\\Python34\\Lib\\site-packages\\PyQt5\\plugins\\platforms\\qwindows.dll'
        ])
    ],
    windows=[{
        "script": "mapwatch.py",
        "icon_resources": [(0, r"images\\icon.ico")]
    }]
)