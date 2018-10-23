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
 'includes': ['sip', 'encodings', 'encodings.hex_codec', 'PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui'],
 'excludes': ['PyQt4.QtWebKit', 'PyQt4.QtDesigner', 'PyQt4.QtNetwork', 'PyQt4.QtOpenGL',
            'PyQt4.QtScript', 'PyQt4.QtSql', 'PyQt4.QtTest', 'PyQt4.QtXml', 'PyQt4.phonon', 'nsmblibmodule'],
 'compressed': 0,
 'optimize': 0
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
