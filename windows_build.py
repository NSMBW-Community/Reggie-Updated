import os, os.path, shutil, sys
from cx_Freeze import setup, Executable

upxFlag = False
if '-upx' in sys.argv:
    sys.argv.remove('-upx')
    upxFlag = True

dir = 'distrib/windows'

print('[[ Freezing Reggie! ]]')
print('>> Destination directory: %s' % dir)
sys.argv.append('build')

if os.path.isdir(dir): shutil.rmtree(dir)
os.makedirs(dir)

# exclude QtWebKit to save space, plus Python stuff we don't use
excludes = ['doctest', 'pdb', 'unittest', 'difflib', 'inspect',
    'os2emxpath', 'posixpath', 'optpath', 'locale', 'calendar',
    'threading', 'select', 'socket', 'hashlib', 'multiprocessing', 'ssl',
    'PyQt4.QtWebKit', 'PyQt4.QtNetwork', 'PyQt5.QtWebKit', 'PyQt5.QtNetwork']

# exclude PyQt4 if we're on Python 3, or PyQt5 if we're on Python 2
excludePyQtVer = 5 if sys.version_info.major < 3 else 4
pyqtModules = ['Core', 'Gui', 'Widgets', 'Designer', 'OpenGL', 'Script', 'Sql', 'Test', 'Xml']
excludes.append('PyQt%d' % excludePyQtVer)
for m in pyqtModules:
    excludes.append('PyQt%d.Qt%s' % (excludePyQtVer, m))

# set it up
setup(
    name='Reggie! Level Editor',
    version='1.0',
    description='Reggie! Level Editor',
    options={
        'build_exe': {
            'build_exe': dir,
            'excludes': excludes,
            'include_msvcr': True,
            'packages': ['sip', 'encodings', 'encodings.hex_codec', 'encodings.utf_8'],
            'zip_include_packages': '*', # https://stackoverflow.com/a/44429619
            'zip_exclude_packages': '',
            },
        },
    executables = [
        Executable(
            'reggie.py',
            base=('Win32GUI' if sys.platform == 'win32' else None),
            icon='reggiedata/win_icon.ico',
            ),
        ],
)

print('>> Built frozen executable!')

# now that it's built, configure everything
try: os.unlink(dir_ + '/w9xpopen.exe') # not needed
except: pass

if upxFlag:
    if os.path.isfile('upx.exe'):
        print('>> Found UPX, using it to compress the executables!')
        files = os.listdir(dir)
        upx = []
        for f in files:
            if f.endswith('.exe') or f.endswith('.dll') or f.endswith('.pyd'):
                upx.append('"%s/%s"' % (dir,f))
        os.system('upx -9 ' + ' '.join(upx))
        print('>> Compression complete.')
    else:
        print(">> UPX not found, binaries can't be compressed.")
        print('>> In order to build Reggie! with UPX, place the upx.exe file into '
              'this folder.')

if os.path.isdir(dir + '/reggiedata'): shutil.rmtree(dir + '/reggiedata')
if os.path.isdir(dir + '/reggieextras'): shutil.rmtree(dir + '/reggieextras')
shutil.copytree('reggiedata', dir + '/reggiedata')
shutil.copytree('reggieextras', dir + '/reggieextras')
shutil.copy('license.txt', dir)
shutil.copy('readme.txt', dir)
if not os.path.isfile(dir + '/libEGL.dll'):
    if os.path.isfile('libEGL.dll'):
        shutil.copy('libEGL.dll', dir)
    else:
        print('>> WARNING: libEGL.dll not found!')

print('>> Reggie has been frozen to %s!' % dir)
