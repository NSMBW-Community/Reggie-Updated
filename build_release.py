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

import json
import os, os.path
import shutil
import sys

import PyInstaller.__main__


########################################################################
############################### Constants ##############################
########################################################################

# Everything highly specific to Reggie is in this section, to make it
# simpler to copypaste this script across all of the NSMBW-related
# projects that use the same technologies (Reggie, Puzzle, BRFNTify,
# etc)

PROJECT_NAME = 'Reggie!'
PROJECT_VERSION = '1.0'

WIN_ICON = os.path.join('reggiedata', 'win_icon.ico')
MAC_ICON = os.path.join('reggiedata', 'reggie.icns')
MAC_BUNDLE_IDENTIFIER = 'ca.chronometry.reggie'

SCRIPT_FILE = 'reggie.py'
DATA_FOLDERS = ['reggiedata', 'reggieextras']
DATA_FILES = ['readme.md', 'license.txt']


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

    import subprocess
    import urllib.request, urllib.error

    # Retrieve info about the latest release
    print('>> Retrieving release information...')
    try:
        with urllib.request.urlopen(API_URL) as response:
            j = json.loads(response.read())
    except urllib.error.HTTPError as e:
        print('HTTPError:')
        print(e)
        print(e.code)
        print(e.reason)
        print(e.headers)
        print(e.read())

    # Simplify it down to a {filename: url} mapping
    name2URL = {}
    for a in j['assets']:
        name2URL[a['name']] = a['browser_download_url']

    # Generate a couple of strings that ought to be in the correct wheel
    # filename
    pyver = 'cp' + str(sys.version_info[0]) + str(sys.version_info[1])
    platform = {'win32': 'win', 'darwin': 'macosx', 'linux': 'manylinux1'}[sys.platform]

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
WORKPATH = 'build_temp_1'
SPECPATH = 'build_temp_2'

def print_emphasis(s):
    print('>>')
    print('>> ' + '=' * (len(s) - 3))
    print(s)
    print('>> ' + '=' * (len(s) - 3))
    print('>>')

print('[[ Building ' + PROJECT_NAME + ' ]]')
print('>> Please note: extra command-line arguments passed to this script will be passed through to PyInstaller.')
print('>> Destination directory: ' + DIR)

if os.path.isdir(DIR): shutil.rmtree(DIR)
if os.path.isdir(WORKPATH): shutil.rmtree(WORKPATH)
if os.path.isdir(SPECPATH): shutil.rmtree(SPECPATH)

def run_pyinstaller(args):
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
################### Running PyInstaller (first time) ###################
########################################################################

# Our only goal here is to create a specfile we can edit. Unfortunately,
# there's no good way to do that without doing a full PyInstaller
# build...

args = [
    '--windowed',
    '--onefile',
    '--distpath=' + DIR,
    '--workpath=' + WORKPATH,
    '--specpath=' + SPECPATH,
]

if sys.platform == 'win32':
    args.append('--icon=' + os.path.abspath(WIN_ICON))
elif sys.platform == 'darwin':
    args.append('--icon=' + os.path.abspath(MAC_ICON))
    args.append('--osx-bundle-identifier=' + MAC_BUNDLE_IDENTIFIER)

for e in excludes:
    args.append('--exclude-module=' + e)
args.extend(sys.argv[1:])
args.append(SCRIPT_FILE)

run_pyinstaller(args)

shutil.rmtree(DIR)
shutil.rmtree(WORKPATH)
# (Leave SPECPATH alone -- we need to adjust the specfile next)


########################################################################
########################## Adjusting specfile ##########################
########################################################################
print('>> Adjusting specfile...')

specfile = os.path.join(SPECPATH, SCRIPT_FILE[:-3] + '.spec')

# New plist file data (if on Mac)
info_plist = {
    'CFBundleName': PROJECT_NAME,
    'CFBundleShortVersionString': PROJECT_VERSION,
    'CFBundleGetInfoString': PROJECT_NAME + ' ' + PROJECT_VERSION,
    'CFBundleExecutable': PROJECT_NAME,
}

# Open original specfile
with open(specfile, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

# Iterate over its lines, and potentially add new ones
new_lines = []
for line in lines:
    new_lines.append(line)

    if sys.platform == 'darwin' and 'BUNDLE(' in line:
        new_lines.append('info_plist=' + json.dumps(info_plist) + ',')

# Save new specfile
with open(specfile, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))


########################################################################
################### Running PyInstaller (second time) ##################
########################################################################

# Most of the arguments are now contained in the specfile. Thus, we can
# run with minimal arguments this time.

args = [
    '--distpath=' + DIR,
    '--workpath=' + WORKPATH,
    specfile,
]

run_pyinstaller(args)

shutil.rmtree(WORKPATH)
shutil.rmtree(SPECPATH)


########################################################################
######################## Copying required files ########################
########################################################################
print('>> Copying required files...')

for f in DATA_FOLDERS:
    if os.path.isdir(os.path.join(DIR, f)):
        shutil.rmtree(os.path.join(DIR, f))
    shutil.copytree(f, os.path.join(DIR, f))

for f in DATA_FILES:
    shutil.copy(f, DIR)


########################################################################
################################## End #################################
########################################################################
print('>> %s has been built to the %s folder!' % (PROJECT_NAME, DIR))
