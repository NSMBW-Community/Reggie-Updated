Reggie! Level Editor ("Reggie-Updated" fork)
============================================

Advanced level editor for New Super Mario Bros. Wii, created by Treeki and
Tempus using Python, PyQt and Wii.py.

The "Reggie-Updated" fork is a modern evolution of the original Reggie!
codebase, focusing on stability, future-proofing, and incorporating the latest
level-file-format research.

Bugfixes are a priority. Minor new features are allowed, so long as most people
are in favor of them. Major new features that aren't really necessary will
generally be declined. Support for newly discovered level options/settings will
always be added when possible, though I may wait until they've been thoroughly
tested first.

If you want a NSMBW level editor with more features (possibly at the expense of
some stability and simplicity), consider
[Reggie! Next](https://github.com/CLF78/Reggie-Next), another Reggie! fork with
somewhat different project goals.

Original Reggie! Homepage: http://www.rvlution.net/reggie/


Changelog
=========

Reggie-Updated 2021.01.27.1:
----------------------------
- Essentially the same as the previous release. It was requested that I add a
  Windows-7-compatible build, so I adjusted the CI infrastructure to do that.
  These will be included in future releases, too.


Reggie-Updated 2021.01.27.0:
----------------------------
**Note:** Due to the second-to-last change listed below, the dock editor
windows (for sprites, entrances, paths, and locations) may not display
correctly when launching Reggie for the first time after upgrading from a
previous version. This fixes itself as soon as you select anything, and does
not happen again after the first launch.

- Added support for Camera Profiles, a recently discovered unused feature that
  allows camera settings to be activated by events. The new dialog has been
  added to the Settings menu. Unfortunately, there's no transition animation,
  limiting this feature's usefulness. The abrupt switch can be hidden by a Zoom
  sprite (206), though. (Thanks to Ninji and especially Zementblock for helping
  with the research on this!)
- Redesigned the bounds settings in the Zones dialog to reflect recent
  findings. (Huge thanks to Zementblock for doing most of the research here!)
- The Zones dialog now uses a two-column layout, because it was starting to be
  taller than some people's screens.
- Music track names are now defined in reggiedata/music.txt instead of being
  hardcoded.
- Renamed "Volcano" music to "Lava Underground", to better distinguish it from
  "Lava".
- The Level Overview window now paints its background color across its whole
  area.
- Docked editor windows (for sprites, paths, etc) now become grayed-out instead
  of disappearing when the item is deselected. This is a less-buggy solution to
  the "level view jolts when a dock appears on the left side of the window"
  issue referred to in the last update. (Bugs in the previous version reported
  by Meatball132, alternative solution suggested by Explos.)
- Other smaller changes and bugfixes.


Reggie-Updated 2021.01.10.0:
----------------------------
- Redesigned the camera settings in the Zones dialog to be much more accurate
  to how the game actually works.
- Each release will now include 32-bit Windows builds, in addition to the
  64-bit ones.
- Updated the application icon for macOS to match the new Big Sur conventions.
  (Thanks to Meorge for making this.)
- Fixed zone visibility settings on Python 3.
- Fixed and optimized level metadata (File -> Level Information) parsing on
  Python 3 / PyQt5.
- Level view no longer jolts when a dock (e.g. the sprite data editor) appears
  on the left side of the window. (Thanks to Meatball132 for reporting.)
- Improved shebang in reggie.py, for more reliable `./reggie.py` launching on
  Linux.


Reggie-Updated 2020.10.26.0:
----------------------------
- You can now set arbitrary music IDs.
- Looped paths now show a dotted line from the last node to the first.
- Fixed various bugs related to paths.
- Release builds now use Python 3.9.
- Implemented a new technique to shrink download sizes. Windows builds are now
  ~29% smaller compared to the previous release, and Ubuntu builds are ~10%
  smaller. macOS is unfortunately not affected.
    - I've tested this as best I can, but there is a small chance this change
      may prevent Reggie from running for some users. Please open an issue if
      the previous release works for you and this one doesn't.
- The version numbers for Python and nsmblib are now displayed in the Help
  menu.
- Fix "Open With" functionality on Windows. (Thanks to Danstor64 for
  reporting.)
- File -> Exit now uses the system default keyboard shortcut instead of
  `Ctrl+Q`.
- The source code now includes several `requirements.txt`s, to make it easier
  to install dependencies.
- Other smaller changes.


Reggie-Updated 2020.09.22.0:
----------------------------
- Release builds for macOS now support system-wide dark mode.
    - This unfortunately required dropping support in the release builds for
      macOS older than 10.13 (High Sierra). You can still run Reggie-Updated
      from source code on older macOS versions, though.
- The editor no longer crashes when run from a directory other than its own.
  (Thanks to Kitty-Cats for the bug report and PR.)
- Palette tabs on macOS have been adjusted to look more consistent with other
  platforms, and less glitchy in dark mode.
- Other smaller changes.


Reggie-Updated 2020.06.01.0:
----------------------------
- Copypasting sprites no longer crashes the editor when running on Python 3
  (thanks to Garnet_04 for the bug report)
- Loading a tileset into the wrong slot no longer crashes the editor (ibid)
- You can now use middle-click-and-drag to scroll around the level view
  (requested by Explos)
- Ctrl+= is now an alternative "zoom in" shortcut
- Window titles have been fixed
- ReggieID (the "Created by Reggie" string stored in levels) has been updated
  to reflect the name of the fork


Reggie-Updated 2020.05.29.0:
----------------------------
- Resized pipe entrances to cover the whole top of the pipe, for easier
  placement. This admittedly could be a controversial change, but nobody has
  told me they don't want it, and it's been requested a lot, so I've gone ahead
  with it anyway.
- Added support for setting default events 33-64 in the Area Settings dialog.
- Various bugs fixed.


Reggie-Updated 2020.05.18.0:
----------------------------
- This release fixes the "Custom Background ID" feature, which was previously
  broken on both Python 3 and PyQt5.


Reggie-Updated 2020.05.16.0:
----------------------------
- Reggie! is now compatible with Python 3, PyQt5, and Qt for Python (PySide2).
  Python 2 and PyQt4 are also still supported.
- NSMBLib has been removed from this repository — you can find it at
  https://github.com/RoadrunnerWMC/NSMBLib-Updated
- Made loading times much faster when running without NSMBLib
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

- Python 2.7 (or newer) (3.5 or newer recommended) — https://www.python.org
- Qt for Python or PyQt; your options depend on the version of Python you're using:
  - If using Python 2.x: PyQt 4.8 (or newer, but less than 5) — https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4
  - If using Python 3.x, either of the following:
    - PyQt 5.11 (or newer) **(RECOMMENDED)** — `pip install PyQt5`
    - Qt for Python 5.12 (or newer) (NOT RECOMMENDED) — `pip install PySide2`
- NSMBLib 0.4 (or newer) — `pip install nsmblib` (optional)
- Darkdetect 0.1.0 (or newer) — `pip install darkdetect` (optional)

If you have a prebuilt/frozen release (for Windows, macOS or Ubuntu)
you don't need to install anything — all the required libraries are included.

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
  Tanks, Vibestar, Kitty-Cats, Zementblock
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
