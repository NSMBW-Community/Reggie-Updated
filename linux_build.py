# This script hasn't been used since Test Build 9 - it may not work properly!

from cx_Freeze import setup, Executable
import os, os.path, shutil, sys

dir = 'distrib/linux'

print '[[ Freezing Reggie! ]]'
print '>> Destination directory: %s' % dir
sys.argv.append('build')

if os.path.isdir(dir): shutil.rmtree(dir)
os.makedirs(dir)

# check to see if we have qtwebkit
excludes = ['cookielib', 'getpass', 'urllib', 'urllib2', 'ssl', 'termios']
try:
    from PyQt4 import QtWebKit
except ImportError:
    excludes.append('QtWebKit')
    excludes.append('QtNetwork')

# set it up
setup(
    name='Reggie! Level Editor',
    version='1.0',
    description='New Super Mario Bros. Wii Level Editor',
    options={
        'build_exe': {'excludes': excludes}
    },
    executables=[
        Executable("reggie.py", copyDependentFiles=True, targetDir=dir)
    ]
)

print '>> Built frozen executable!'

# now that it's built, configure everything
if os.path.isdir(dir + '/reggiedata'): shutil.rmtree(dir + '/reggiedata')
shutil.copytree('reggiedata', dir + '/reggiedata')
shutil.copy('license.txt', dir)
shutil.copy('readme.txt', dir)

print '>> Reggie has been frozen to %s!' % dir
