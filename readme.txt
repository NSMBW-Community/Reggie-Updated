=== Reggie! Level Editor (Release 3) ===

Advanced level editor for New Super Mario Bros. Wii, created by Treeki and
Tempus using Python, PyQt and Wii.py.

Homepage: http://www.rvlution.net/reggie/
Support:  http://www.rvlution.net/forums/

Source code package for this release:
- http://www.rvlution.net/reggie/downloads/Reggie_r3_source.zip


=== Changelog: ===

Release 3: (April 2nd, 2011)
- Unicode is now supported in sprite names within spritedata.xml
    (thanks to 'NSMBWHack' on rvlution.net for the bug report)
- Unicode is now supported in sprite categories.
- Sprites 274, 354 and 356 now render using images.
- Other various bug fixes.


Release 2: (April 2nd, 2010)
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
- Reggie! is finally released after 4 months of work and 18 test builds!
- First release, may have bugs or incomplete sprites. Report any errors to us
  at the forums (link above).


=== Requirements: ===

If you are using the source release:
- Python 2.5 (or newer) - http://www.python.org
- PyQt 4.6 (or newer) - http://www.riverbankcomputing.co.uk/software/pyqt/intro
- NSMBLib 0.4.1 - included with the source package (optional)

If you have a prebuilt/frozen release (for Windows or Mac OS)
you don't need to install anything - all the required libraries are included.

For more information on running Reggie from source and getting the required
libraries, check the Getting Started page inside the help file
(located at reggiedata/help/start.html within the archive)


=== Reggie! Team: ===

Developers:
- Treeki - Creator, Programmer, Data, RE
- Tempus - Programmer, Graphics, Data
- AerialX - CheerIOS, Riivolution
- megazig - Code, Optimisation, Data, RE
- Omega - int(), Python, Testing
- Pop006 - Sprite Images
- Tobias Amaranth - Sprite Info (a lot of it), Event Example Stage

Other Testers and Contributors:
- BulletBillTime, Dirbaio, EdgarAllen, FirePhoenix, GrandMasterJimmy,
  Mooseknuckle2000, MotherBrainsBrain, RainbowIE, Skawo, Sonicandtails,
  Tanks, Vibestar

- Tobias Amaranth and Valeth - Text Tileset Addon


=== Libraries/Resources: ===

Qt - Nokia (http://qt.nokia.com)
PyQt - Riverbank Computing (http://www.riverbankcomputing.co.uk/software/pyqt/intro)
Wii.py - megazig, Xuzz, The Lemon Man, Matt_P, SquidMan, Omega (http://github.com/icefire/Wii.py)
Interface Icons - Yusuke Kamiyamane (http://www.pinvoke.com)


=== Licensing: ===

Reggie! is released under the GNU General Public License v2.
See the license file in the distribution for information.
