# This script hasn't been used since Test Build 9 - it may not work properly!

from cx_Freeze import setup, Executable
import os, os.path, shutil, sys

distribDir = 'distrib'
dir = 'distrib/linux'

print('[[ Freezing Reggie! ]]')
print('>> Destination directory: %s' % dir)
sys.argv.append('build')

if os.path.isdir(dir): shutil.rmtree(dir)
if not os.path.isdir(distribDir): os.makedirs(distribDir)

# check to see if we have qtwebkit
excludes = ['cookielib', 'getpass', 'urllib', 'urllib2', 'ssl', 'termios']
try:
    if sys.version_info.major < 3:
        from PyQt4 import QtWebKit
    else:
        from PyQt5 import QtWebKit
except ImportError:
    excludes.append('QtWebKit')
    excludes.append('QtNetwork')

# exclude PyQt4 if we're on Python 3, or PyQt5 if we're on Python 2
excludePyQtVer = 5 if sys.version_info.major < 3 else 4
pyqtModules = ['Core', 'Gui', 'Widgets', 'WebKit', 'Network']
excludes.append('PyQt%d' % excludePyQtVer)
for m in pyqtModules:
    excludes.append('PyQt%d.Qt%s' % (excludePyQtVer, m))

# set it up
setup(
    name='Reggie! Level Editor',
    version='1.0',
    description='New Super Mario Bros. Wii Level Editor',
    options={
        'build_exe': {'excludes': excludes},
    },
    executables=[
        Executable("reggie.py")
    ]
)

print('>> Built frozen executable!')

# now move the output to the actual correct directory
# thanks for getting rid of the targetDir option and not adding an
# alternative, cx_Freeze devs
# (or if there is one, I could't find it after an hour of Googling and
# trial-and-error)
assert len(os.listdir('build')) == 1
tempSubDir = os.path.join('build', os.listdir('build')[0])
shutil.move(tempSubDir, dir)
shutil.rmtree('build')

# now that it's built, configure everything
if os.path.isdir(dir + '/reggiedata'): shutil.rmtree(dir + '/reggiedata')
shutil.copytree('reggiedata', dir + '/reggiedata')
shutil.copy('license.txt', dir)
shutil.copy('readme.txt', dir)

print('>> Reggie has been frozen to %s!' % dir)
