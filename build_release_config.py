import os.path

# Everything highly specific to Reggie is in this section, to make it
# simpler to copypaste this script across all of the NSMBW-related
# projects that use the same technologies (Reggie, Puzzle, BRFNTify,
# etc)

PROJECT_NAME = 'Reggie!'
FULL_PROJECT_NAME = 'Reggie! Level Editor'
PROJECT_VERSION = '1.0'

WIN_ICON = os.path.join('reggiedata', 'win_icon.ico')
MAC_ICON = os.path.join('reggiedata', 'reggie.icns')
MAC_BUNDLE_IDENTIFIER = 'ca.chronometry.reggie'

SCRIPT_FILE = 'reggie.py'
DATA_FOLDERS = ['reggiedata', 'reggieextras']
DATA_FILES = ['readme.md', 'license.txt']
EXTRA_IMPORT_PATHS = []

USE_PYQT = True
USE_NSMBLIB = True

EXCLUDE_SELECT = True
EXCLUDE_HASHLIB = True
EXCLUDE_LOCALE = True

# macOS only
AUTO_APP_BUNDLE_NAME = SCRIPT_FILE.split('.')[0] + '.app'
FINAL_APP_BUNDLE_NAME = FULL_PROJECT_NAME + '.app'
