Reggie! Level Editor ("Reggie-Updated" fork)
============================================

Advanced level editor for New Super Mario Bros. Wii, created by Treeki and
Tempus using Python, PyQt and Wii.py.

The "Reggie-Updated" fork aims to keep Reggie! compatible with the latest versions of its
dependencies, and to fix bugs and make minor improvements. Pull requests that make large
changes to how the editor works or add major features will be declined — please make your
own fork for that.

Homepage: http://www.rvlution.net/reggie/

Source code package for Release 3: http://www.rvlution.net/reggie/downloads/Reggie_r3_source.zip


Changelog
=========

"Reggie-Updated" fork
---------------------
- Reggie! is now compatible with Python 3, PyQt5, and Qt for Python (PySide2).
    Python 2 and PyQt4 are also still supported.
- nsmblib has been removed from this repository -- you can find it at
    https://github.com/RoadrunnerWMC/NSMBLib-Updated
- Made loading times much faster on environments where NSMBLib is not available.
- Made tileset texture rendering perfectly accurate instead of just
    "close enough."
- Made certain terminology consistent across the editor.
- All changes that were merged into the main repository
    (https://github.com/Treeki/Reggie) between Release 3 and October 22, 2018
    are included:
    - Added "Minimum Zoom" and "Maximum Zoom" actions, and increased the
        number of available zoom levels
    - Made certain fonts bold.
    - Made the raw sprite data textbox turn red when containing invalid data.
    - Sprites 151, 175, 176, 180, 185, 187, 193, 195, 196, 197, 198, 199,
        200, 224, 227, 233, 262, 271, 318, 333, 376, 395, 416 and 425 now
        render using images.
- Other various bug fixes.


Release 3: (April 2nd, 2011)
----------------------------
- Unicode is now supported in sprite names within spritedata.xml
    (thanks to 'NSMBWHack' on rvlution.net for the bug report)
- Unicode is now supported in sprite categories.
- Sprites 274, 354 and 356 now render using images.
- Other various bug fixes.


Release 2: (April 2nd, 2010)
----------------------------
- Bug with Python 2.5 compatibility fixed.
- Unicode filenames and Stage folder paths should now work.
- Changed key shortcut for "Shift Objects" to fix a conflict.
- Fixed pasting so that whitespace/newlines won't mess up Reggie clips.
- Fixed a crash with the Delete Zone button in levels with no zones.
- Added an error message if an error occurs while loading a tileset.
- Fixed W9 toad houses showing up as unused in the level list.
- Removed integrated help viewer (should kill the QtWebKit dependency)
- Fixed a small error when saving levels with empty blocks
- Fixed tileset changing
- Palette is no longer unclosable
- Ctrl+0 now sets the zoom level to 100%
- Path editing support added (thanks, Angel-SL)


Release 1: (March 19th, 2010)
-----------------------------
- Reggie! is finally released after 4 months of work and 18 test builds!
- First release, may have bugs or incomplete sprites. Report any errors to us
    at the forums (link above).


Requirements
============

If you are using the source release:

- Python 2.7 (or newer) (3.5 or newer recommended) - https://www.python.org
- Qt for Python or PyQt; your options depend on the version of Python you're using:
  - If using Python 2.x: PyQt 4.8 (or newer, but less than 5) — https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4
  - If using Python 3.x, either of the following:
    - PyQt 5.11 (or newer) **(RECOMMENDED)** — `pip install PyQt5`
    - Qt for Python 5.12 (or newer) (NOT RECOMMENDED) — `pip install PySide2`
- NSMBLib 0.4.1 - https://github.com/RoadrunnerWMC/NSMBLib-Updated (optional)

If you have a prebuilt/frozen release (for Windows or Mac OS)
you don't need to install anything - all the required libraries are included.

For more information on running Reggie! from source and getting the required
libraries, check the Getting Started page inside the help file
(located at reggiedata/help/start.html within the archive)


Reggie! Team
============

Developers
----------
- Treeki — Creator, Programmer, Data, RE
- Tempus — Programmer, Graphics, Data
- AerialX — CheerIOS, Riivolution
- megazig — Code, Optimisation, Data, RE
- Omega — int(), Python, Testing
- Pop006 — Sprite Images
- Tobias Amaranth — Sprite Info (a lot of it), Event Example Stage
- RoadrunnerWMC — "Reggie-Updated" Fork

Other Testers and Contributors
------------------------------
- BulletBillTime, Dirbaio, EdgarAllen, FirePhoenix, GrandMasterJimmy,
  Mooseknuckle2000, MotherBrainsBrain, RainbowIE, Skawo, Sonicandtails,
  Tanks, Vibestar
- Tobias Amaranth and Valeth — Text Tileset Addon


Libraries/Resources
===================

- Qt — The Qt Company (https://www.qt.io)
- Qt for Python — The Qt Company (https://www.qt.io)
- PyQt — Riverbank Computing (https://riverbankcomputing.com/software/pyqt/intro)
- Wii.py — megazig, Xuzz, The Lemon Man, Matt_P, SquidMan, Omega (https://github.com/grp/Wii.py)
- Interface Icons — Yusuke Kamiyamane (http://p.yusukekamiyamane.com/)


Licensing
=========

Reggie! is released under the GNU General Public License v2.
See the license file in the distribution for information.
