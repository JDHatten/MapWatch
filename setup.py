from distutils.core import setup
import py2exe
setup(
    data_files=[
        ('imageformats', [
            r'C:\\Python34\\Lib\\site-packages\\PyQt5\\plugins\\imageformats\\qico.dll'
        ]),
        ('platforms', [
            r'C:\\Python34\\Lib\\site-packages\\PyQt5\\plugins\\platforms\\qwindows.dll'
        ]),
        ('', [
            r'C:\\Python34\\Lib\\site-packages\\requests\\cacert.pem'
        ])
    ],
    options={'py2exe': {
            'compressed': True,
            'dist_dir': 'MapWatch',
            'optimize': 1,
            'excludes': ['pydoc', 'doctest', 'pdb', 'inspect', 'pyreadline', 'optparse']
        }
    },
    windows=[{
        'script': 'mapwatch.py',
        'icon_resources': [(0, r'images\\icon.ico')]
    }]
)