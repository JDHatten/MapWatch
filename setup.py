from distutils.core import setup
import py2exe
setup(
    data_files=[
        ('imageformats', [
            r'C:\\Python34\\Lib\\site-packages\\PyQt5\\plugins\\imageformats\\qico.dll'
        ]),
        ('platforms', [
            r'C:\\Python34\\Lib\\site-packages\\PyQt5\\plugins\\platforms\\qwindows.dll'
        ])
    ],
    options={'py2exe': {
            'compressed': True,
            'dist_dir': 'dist',
            'optimize': 1,
            'excludes': ['pydoc', 'doctest', 'pdb', 'inspect', 'pyreadline', 'locale', 'optparse', 'pickle', 'calendar']
        }
    },
    windows=[{
        "script": "mapwatch.py",
        "icon_resources": [(0, r"images\\icon.ico")]
    }]
)