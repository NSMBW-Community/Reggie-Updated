"""
Usage:
    cd to it's directory
    python mac_setup.py py2app
"""


from setuptools import setup
import os, sys, shutil


NAME = 'Reggie!'
VERSION = '1.0'

plist = dict(
    CFBundleIconFile=NAME,
    CFBundleName=NAME,
    CFBundleShortVersionString=VERSION,
    CFBundleGetInfoString=' '.join([NAME, VERSION]),
    CFBundleExecutable=NAME,
    CFBundleIdentifier='ca.chronometry.reggie',
)



APP = ['reggie.py']
DATA_FILES = ['reggiedata', 'archive.py', 'common.py', 'license.txt', 'lz77.py', 'nsmblib-0.4.zip', 'readme.txt', 'sprites.py']
OPTIONS = {
 'argv_emulation': True,
# 'graph': True,
 'iconfile': 'reggiedata/reggie.icns',
 'plist': plist,
# 'xref': True,
 'includes': ['sip', 'encodings', 'encodings.hex_codec', 'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
 'excludes': ['PyQt5.QtWebKit', 'PyQt5.QtDesigner', 'PyQt5.QtNetwork', 'PyQt5.QtOpenGL',
            'PyQt5.QtScript', 'PyQt5.QtSql', 'PyQt5.QtTest', 'PyQt5.QtXml', 'PyQt5.phonon', 'nsmblibmodule'],
 'compressed': 0,
 'optimize': 0
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
