"""
Usage:
    cd to its directory
    python3 mac_setup.py py2app
"""


from setuptools import setup
import os, sys, shutil


NAME = 'Reggie!'
VERSION = '1.0'

plist = {
    'CFBundleIconFile': NAME,
    'CFBundleName': NAME,
    'CFBundleShortVersionString': VERSION,
    'CFBundleGetInfoString': NAME + ' ' + VERSION,
    'CFBundleExecutable': NAME,
    'CFBundleIdentifier': 'ca.chronometry.reggie',
}


excludes = ['doctest', 'pdb', 'unittest', 'difflib', 'inspect',
    'os2emxpath', 'optpath', 'locale', 'calendar', 'threading',
    'select', 'socket', 'hashlib', 'multiprocessing', 'ssl',
    'PyQt4.QtWebKit', 'PyQt4.QtNetwork', 'PyQt5.QtWebKit', 'PyQt5.QtNetwork']

# exclude PyQt4 if we're on Python 3, or PyQt5 if we're on Python 2
excludePyQtVer = 5 if sys.version_info.major < 3 else 4
pyqtModules = ['Core', 'Gui', 'Widgets', 'Designer', 'OpenGL', 'Script', 'Sql', 'Test', 'Xml']
excludes.append('PyQt%d' % excludePyQtVer)
excludes.append('PyQt%d.phonon' % excludePyQtVer)
for m in pyqtModules:
    excludes.append('PyQt%d.Qt%s' % (excludePyQtVer, m))

includes = ['sip', 'encodings', 'encodings.hex_codec', 'posixpath']
includePyQtVer = 4 if sys.version_info.major < 3 else 5
includes.append('PyQt%d' % includePyQtVer)
for m in pyqtModules:
    includes.append('PyQt%d.Qt%s' % (includePyQtVer, m))


APP = ['reggie.py']
DATA_FILES = ['reggiedata', 'archive.py', 'common.py', 'license.txt', 'lz77.py', 'readme.md', 'sprites.py']
OPTIONS = {
 'argv_emulation': True,
# 'graph': True,
 'iconfile': 'reggiedata/reggie.icns',
 'plist': plist,
# 'xref': True,
 'includes': includes,
 'excludes': excludes,
 'compressed': 0,
 'optimize': 0
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
