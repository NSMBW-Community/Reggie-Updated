#!/usr/bin/python
# -*- coding: latin-1 -*-

# Reggie! - New Super Mario Bros. Wii Level Editor
# Copyright (C) 2009-2010 Treeki, Tempus


# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import os, os.path
import shutil
import sys

import PyInstaller.__main__


########################################################################
################## Secret NSMBLib-installation feature #################
########################################################################

# This command-line option automatically installs the latest release of
# nsmblib. It's intended only for use with CI, though it would probably
# work for end users as well.
# (This part of the code is not necessarily compatible with Py 2.x.)

API_URL = 'https://api.github.com/repos/RoadrunnerWMC/NSMBLib-Updated/releases/latest'

if len(sys.argv) >= 2 and sys.argv[1] == '--install-nsmblib':
    print('[[ Downloading and installing NSMBLib... ]]')

    import json
    import os
    import subprocess
    import urllib.request

    # Retrieve info about the latest release
    print('>> Retrieving release information...')
    with urllib.request.urlopen(API_URL) as response:
        j = json.loads(response.read())

    # Simplify it down to a {filename: url} mapping
    name2URL = {}
    for a in j['assets']:
        name2URL[a['name']] = a['browser_download_url']

    # Generate a couple of strings that ought to be in the correct wheel
    # filename
    pyver = 'cp' + str(sys.version_info[0]) + str(sys.version_info[1])
    platform = {'darwin': 'macosx', 'posix': 'manylinux1', 'nt': 'win'}[os.name]

    # Iterate over all available wheel filenames
    for wheel_name, url in name2URL.items():
        if pyver not in wheel_name: continue
        if platform not in wheel_name: continue
        print('>> Selected ' + wheel_name)

        # Download the wheel as a local file
        print('>> Downloading...')
        with urllib.request.urlopen(url) as response:
            with open(wheel_name, 'wb') as f:
                f.write(response.read())

        # Install the file with pip
        # https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program
        print('>> Installing...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', wheel_name])

        # Clean up
        # (not necessary for CI, but, can't hurt)
        os.remove(wheel_name)

        break

    else:
        print(f'>> ERROR: No suitable wheel for pyver={pyver} platform={platform} found!')
        sys.exit(1)

    print('>> Done!')
    sys.exit(0)


########################################################################
################################# Intro ################################
########################################################################

DIR = 'distrib'
WORKPATH = 'build_temp'

def print_emphasis(s):
    print('>>')
    print('>> ' + '=' * (len(s) - 3))
    print(s)
    print('>> ' + '=' * (len(s) - 3))
    print('>>')

print('[[ Building Reggie! ]]')
print('>> Please note: extra command-line arguments passed to this script will be passed through to PyInstaller.')
print('>> Destination directory: ' + DIR)

if os.path.isdir(DIR): shutil.rmtree(DIR)
if os.path.isdir(WORKPATH): shutil.rmtree(WORKPATH)

########################################################################
######################### Environment detection ########################
########################################################################
print('>>')
print('>> Detecting environment...')
print('>>')

# Python optimization level
if sys.flags.optimize == 2:
    print('>>   [X] Python optimization level is -OO')
else:
    print('>>   [ ] Python optimization level is -OO')

# NSMBLib being installed
try:
    import nsmblib
    print('>>   [X] NSMBLib is installed')
except ImportError:
    nsmblib = None
    print('>>   [ ] NSMBLib is installed')

# UPX being installed

# There seems to be no reliable way to determine in this script if
# PyInstaller will detect UPX or not. PyInstaller itself provides no
# public API for this, and doing horrible things with its private API
# didn't ultimately work well enough to be useful.
# So all we can do is show this generic message, unfortunately.
print('>>   [?] UPX is installed')


# Now show big warning messages if any of those failed
if sys.flags.optimize < 2:
    msg = 'without' if sys.flags.optimize == 0 else 'with only one level of'
    print_emphasis('>> WARNING: Python is being run ' + msg + ' optimizations enabled! Please consider building with -OO.')

if nsmblib is None:
    print_emphasis('>> WARNING: NSMBLib does not seem to be installed! Please consider installing it prior to building.')

print_emphasis('>> NOTE: If the PyInstaller output below says "INFO: UPX is not available.", you should install UPX!')

########################################################################
############################### Excludes ###############################
########################################################################
print('>>')
print('>> Populating excludes...')
print('>>')

# Static excludes
excludes = ['calendar', 'difflib', 'doctest', 'hashlib', 'inspect',
    'locale', 'multiprocessing', 'optpath', 'os2emxpath', 'pdb',
    'select', 'socket', 'ssl', 'threading', 'unittest']

if sys.platform == 'nt':
    excludes.append('posixpath')

# Add excludes for other Qt modules

unneededQtModules = ['Designer', 'Network', 'OpenGL', 'Qml', 'Script', 'Sql', 'Test', 'WebKit', 'Xml']
neededQtModules = ['Core', 'Gui', 'Widgets']

targetQt = 'PyQt' + str(4 if sys.version_info.major < 3 else 5)
print('>> Targeting ' + targetQt)

for qt in ['PySide2', 'PyQt4', 'PyQt5']:
    # Exclude all the stuff we don't use
    for m in unneededQtModules:
        excludes.append(qt + '.Qt' + m)

    if qt != targetQt:
        # Since we're not using this copy of Qt, exclude it
        excludes.append(qt)

        # As well as its QtCore/QtGui/etc
        for m in neededQtModules:
            excludes.append(qt + '.Qt' + m)

print('>> Will use the following excludes list: ' + ', '.join(excludes))


########################################################################
########################## Running PyInstaller #########################
########################################################################

args = [
    '--windowed',
    '--onefile',
    '--distpath=' + DIR,
    '--workpath=' + WORKPATH,
    '--specpath=' + WORKPATH,
    '--icon=' + os.path.abspath(os.path.join('reggiedata', 'win_icon.ico')),
]

for e in excludes:
    args.append('--exclude-module=' + e)
args.extend(sys.argv[1:])
args.append('reggie.py')

print('>>')
printMessage = ['>> Running PyInstaller with the following arguments:']
for a in args:
    if ' ' in a:
        printMessage.append('"' + a + '"')
    else:
        printMessage.append(a)
print(' '.join(printMessage))
print('>>')

PyInstaller.__main__.run(args)

########################################################################
######################## Copying required files ########################
########################################################################
print('>> Copying required files...')

if os.path.isdir(DIR + '/reggiedata'): shutil.rmtree(DIR + '/reggiedata')
if os.path.isdir(DIR + '/reggieextras'): shutil.rmtree(DIR + '/reggieextras')
shutil.copytree('reggiedata', DIR + '/reggiedata')
shutil.copytree('reggieextras', DIR + '/reggieextras')

shutil.copy('license.txt', DIR)
shutil.copy('readme.md', DIR)

shutil.rmtree(WORKPATH)

########################################################################
################################## End #################################
########################################################################
print('>> Reggie has been built to the %s folder!' % DIR)
