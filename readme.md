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
[Reggie! Next](https://github.com/NSMBW-Community/Reggie-Next), another Reggie!
fork with somewhat different project goals.

Original Reggie! Homepage: https://riivolution.github.io/reggie/


Requirements
============

If you are using the source release:

- Python 2.7 (or newer) (3.5 or newer recommended) — https://www.python.org
- Qt for Python or PyQt; your options depend on the version of Python you're using:
  - If using Python 2.x: PyQt 4.8 (or newer, but less than 5) — https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4
  - If using Python 3.x, any of the following:
    - PyQt 6.1.1 (or newer) **(RECOMMENDED)** — `pip install PyQt6`
    - PyQt 5.11 (or newer) (use if PyQt6 isn't available for your system) — `pip install PyQt5`
    - Qt for Python 5.12 (or newer) (NOT RECOMMENDED) — `pip install PySide2`
- NSMBLib 0.4 (or newer) — `pip install nsmblib` (optional)

If you have a prebuilt/frozen release (for Windows, macOS or Ubuntu),
you don't need to install anything — all the required libraries are included.

For more information on running Reggie! from source and getting the required
libraries, check the Getting Started page inside the help file
(located at reggiedata/help/start.html within the archive)


macOS Troubleshooting
=====================

If you get the error "Reggie! Level Editor is damaged and can't be opened.",
it's because the release builds are unsigned. To fix it, launch a Terminal
window and run

    sudo xattr -rd com.apple.quarantine "/path/to/Reggie! Level Editor.app"
    
...with the example path above replaced with the actual path to the app. This
will override the application signature requirement, which should allow you to
launch the app.


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
  Tanks, Vibestar, Kitty-Cats, Zementblock, TMolter
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


Changelog
=========

Reggie-Updated 2022.06.24.0:
----------------------------
- To improve the experience when working with Newer SMBW and its derivatives,
  Reggie now accepts a "Tilesets" folder next to the Stage folder as a
  substitute for a Texture folder within it.
- You can now decide to select game paths detected as invalid if you want to.
  (An example legitimate use for this would be when a work-in-progress mod
  doesn't yet have a 1-1.)
- "Entrance ID" in Area Settings has been renamed to "Starting Entrance ID" to
  make its meaning more obvious.
- The "Open Level by File..." dialog now always defaults to the folder
  containing the level that's currently open.
- Adding a new zone in the Zones dialog now also selects its tab automatically.
- Other smaller changes and bugfixes.


Reggie-Updated 2021.12.04.0:
----------------------------
- New feature in the View menu: "Tileset Slots Mod" -- simulates Newer's code
  patch that lets tilesets work correctly in any tileset slot. Only use this if
  your mod actually includes that code patch, though!
- The layout of the Entrance editor has been changed to make type-specific
  settings clearer.
- Added the "Direction of Other Side" connected-pipe entrance setting.
- Added the recently discovered "Send to World Map" entrance setting.
- Scrolling while holding the Control key now zooms the level view, like in
  most other programs.
- If you drag something near the edge of the level view, it now automatically
  scrolls in that direction.
- "Save As..." now defaults to .arc.LZ if the currently-opened level file is
  compressed.
- Other smaller changes and bugfixes.


Reggie-Updated 2021.11.03.0:
----------------------------
- Reggie Updated can now load and saved LZ11-compressed levels (.arc.LZ). These
  will be found in the upcoming Newer Super Mario Bros. Wii 1.30 update.
- Release builds (apart from the 32-bit/Windows-7 build) are now built with
  Python 3.10.
- Added the newly discovered "Spawn Half a Tile Left" entrance setting (only
  available for certain entrance types).
- Renamed bgA_4102 from "Message Box" to "Iggy Boss Battle Line Guides".
  (Thanks to B1 Gaming for pointing out that this needed to be changed.)
- Changed the default time limit for newly added areas from 400 to 500, to be
  consistent with both the default time limit for new levels and the value
  Nintendo most commonly uses.
- Changed the wording for the "Terrain Lighting" zone setting to better
  indicate recommended usage.
- The `-alpha` command-line flag now works when NSMBLib is in use, if it's
  NSMBLib-Updated 2021.10.14.01 or newer.
- The NSMBLib-Updated version number is now displayed in the Help menu if
  available (specifically, for versions 2021.10.14.01 and newer).
- Many bugfixes.


Reggie-Updated 2021.09.11.0:
----------------------------
- Fixed the "Custom background ID" dialog, which was broken in PyQt6.
- The error message for when Reggie can't find the reggiedata folder now
  additionally tells you that this can be caused by running it from within a
  zip file.
- Moved the changelog to the bottom of readme.md.


Reggie-Updated 2021.07.29.1:
----------------------------
- Fixed "Save As..." and "Level Screenshot...", which were broken by the switch
  to PyQt6 in the previous release.
- Tiles from nonexistent objects are now rendered as a black-and-magenta
  checkerboard, instead of transparent.
- Pipe icons on pipe entrances are now drawn behind the entrance border instead
  of in front.
- Updated requirements_py3.txt to refer to PyQt6 instead of PyQt5.


Reggie-Updated 2021.07.29.0:
----------------------------
- This release adds support for PyQt6, the latest version of PyQt! There were a
  lot of code changes required to make this happen, and it's possible some
  things were overlooked, so please let me know if you encounter any issues
  with this release. Release builds (apart from the "Windows 7" ones) will now
  be built with PyQt6, too.
- Reduced the limit at which Reggie will start warning you about having too
  many zones from 8 to 6. The game can sometimes handle more than 6 zones
  depending on selected background settings, and the incorrect limit of 8 was
  probably determined years ago through experimentation rather than proper
  reverse engineering.
- Fixed the behavior of dragged sprites and entrances in the level overview.
  (Thanks to Grop for the bug report.)
- Removed the "Windows 8.1+ 32-bit" release builds, since PyQt6 doesn't provide
  builds for 32-bit Python. Anyone who was using those builds can use the
  "Windows 7 or 32-bit" (previously called just "Windows 7") builds instead,
  which will continue to use PyQt5.
- Simplified the GitHub Actions build process on macOS. Previously, custom
  builds of Python and PyInstaller were used in order to gain access to the
  system dark mode. This is no longer needed now that Reggie has its own proper
  built-in dark mode.
- Other smaller changes.


Reggie-Updated 2021.05.18.0:
----------------------------
- Reggie Updated now supports spritedata.xml's from Reggie Next! ...Kind of. It
  tries its best to map all of Next's new field formats onto the existing ones,
  and it's not perfect, but it works pretty well in most cases.
- The "Layer 0 Spotlight" and "Full Darkness" options have been converted to
  checkboxes, to support a combined mode with both effects which has been
  discovered. (Thanks to Abood and Ninji for both independently finding this.)
- The "Full Screen" layer 0 spotlight mode has been renamed to "Extremely
  Large", as it turns out that the circle can still be seen at high zoom
  levels. (Thanks to Ninji for discovering this in the code, and to Zementblock
  for testing it.)
- You can now always see the ID of a location, even when the location isn't
  wide enough to fit the text. You can also now drag such a location by its ID,
  too. (Thanks to Grop for pointing this issue out, and suggesting a fix.)
- The "Add" button in the Camera Profiles dialog now adds a new profile with
  (highest event ID) + 1, instead of one with event ID 0. (Thanks to Skawo for
  the suggestion.)
- Renamed a few zone themes to be more clear.
- Fixed a few tooltips that had inaccurate information.
- Replaced the term "Doomship" with "Airship" everywhere, for consistency and
  accuracy.
- Other smaller changes and bugfixes.


Reggie-Updated 2021.03.21.0:
----------------------------
- Added support for "Zone Direction" setting in the Zones dialog.
- Dark Mode has been added! You can find it in the "View" menu.
- The "View" dropdown in the Sprites tab in the Palette now remembers your
  choice when you close and re-open Reggie. No need to instinctively switch to
  the "Search" view every time anymore!
- Removed text labels ("Sprites", "Entrances", "Paths") from Palette tabs, to
  improve compactness so that they all fit on-screen at once without scrolling.
  The original labels have been retained as tooltips, though.
- Fixed a bug where the dock widgets (item editor windows) were displayed
  incorrectly upon first launch.
- Fixed broken "Reggie! Help" icon.
- Reggie now supports "portable.txt", inspired by Dolphin Emulator. Placing a
  file with that name in Reggie's directory will cause it to save/load settings
  locally instead of using the system registry.
- Reggie now enables
  [setUnifiedTitleAndToolBarOnMac](https://doc.qt.io/qt-5/qmainwindow.html#unifiedTitleAndToolBarOnMac-prop)
  for a slightly nicer look on macOS.
- Fixed broken settings on macOS.
- Deleted the sprite image for sprite 376 ("Moving Chain-Link") because it
  looked awful.
- The Help menu now shows the Qt bindings in use, its version number, and the
  version number of Qt itself.
- Renamed "About PyQt" to "About Qt".
- All PNG files have been minified, saving about 1.6 MB.
- Added a new "-clear-settings" CLI argument, which causes all settings to be
  reset to defaults upon launch. This could be helpful if corrupted settings
  are preventing Reggie from loading.
- Added a new "-gamepath=PATH" CLI argument for specifying the game path,
  bypassing the folder picker dialog. This can be used as a workaround since
  the folder picker dialog is bugged and unusable on certain platforms.
- Other smaller changes and bugfixes.


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
