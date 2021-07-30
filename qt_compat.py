# -*- coding: utf-8 -*-

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


def importQt():
    """
    Find a supported Qt bindings library. Return a tuple containing:
    - QtCore
    - QtGui
    - QtWidgets
    - The runtime Qt version: (a, b, c) for version a.b.c
    - The runtime Qt bindings version: (a, b, c) for version a.b.c
    - The human-friendly string name of the Qt bindings (e.g. "PyQt6")
    """
    def parseQVersion(v):
        return tuple([int(c) for c in v.split('.')])

    def pyqtVersionToTuple(v):
        return (v >> 16, (v >> 8) & 0xff, v & 0xff)

    try:
        from PyQt6 import QtCore, QtGui, QtWidgets
        return QtCore, QtGui, QtWidgets, parseQVersion(QtCore.qVersion()), pyqtVersionToTuple(QtCore.PYQT_VERSION), 'PyQt6'
    except ImportError:
        pass

    try:
        from PyQt5 import QtCore, QtGui, QtWidgets
        return QtCore, QtGui, QtWidgets, parseQVersion(QtCore.qVersion()), pyqtVersionToTuple(QtCore.PYQT_VERSION), 'PyQt5'
    except ImportError:
        pass

    try:
        from PyQt4 import QtCore, QtGui
        return QtCore, QtGui, QtGui, parseQVersion(QtCore.qVersion()), pyqtVersionToTuple(QtCore.PYQT_VERSION), 'PyQt4'
    except ImportError:
        pass

    try:
        import PySide2
        from PySide2 import QtCore, QtGui, QtWidgets
        return QtCore, QtGui, QtWidgets, parseQVersion(QtCore.qVersion()), PySide2.__version_info__, 'PySide2'
    except ImportError:
        pass

    raise RuntimeError('Could not find any supported Qt bindings. Please read the readme for more information.')


QtCore, QtGui, QtWidgets, QtCompatVersion, QtBindingsVersion, QtName = importQt()


# In PyQt4, QtGui.QValidator.validate() returns a 2-tuple (state, pos).
# In PyQt5+, it returns a 3-tuple (state, input, pos)
# This decorator lets you use the PyQt5 style, and it'll drop the
# "input" value automatically on PyQt4.
if QtCompatVersion < (5,0,0):
    def QValidatorValidateCompat(func):
        def wrap(*args, **kwargs):
            state, input, pos = func(*args, **kwargs)
            return state, pos
        return wrap
else:
    def QValidatorValidateCompat(func):
        return func


# PyQt and PySide use different names to represent signals and slots,
# and have a different string name for Python object types.
if hasattr(QtCore, 'pyqtSignal'):  # PyQt
    QtCoreSignal = QtCore.pyqtSignal
    QtCoreSlot = QtCore.pyqtSlot
    PyObject = 'PyQt_PyObject'
else:  # PySide2
    QtCoreSignal = QtCore.Signal
    QtCoreSlot = QtCore.Slot
    PyObject = 'object'


def execQtObject(obj, *args, **kwargs):
    """
    Equivalent to `obj.exec()` on PyQt5/6, and `obj.exec_()` on PyQt4.
    We use this instead of `qm(thing).exec()` because that's a syntax
    error on Python 2 ("exec" keyword), and forcing the application code
    to use `getattr()` every time is ugly.
    """
    if QtCompatVersion < (6,0,0):
        return obj.exec_(*args, **kwargs)
    else:
        # obj.exec() is a syntax error on Python 2 because "exec" is a
        # keyword, so we have to use getattr()
        return getattr(obj, 'exec')(*args, **kwargs)


# Define the "qm()" compatibility function that adds PyQt6-style syntax
# on top of PyQt4/PyQt5 where needed.

if QtCompatVersion < (6,0,0):

    class Wrapper:
        """
        A thin wrapper class around an arbitrary Python object, that
        lets you override specific attributes.
        """
        def __init__(self, obj, overrides):
            self._obj = obj
            self._overrides = overrides

        def __getattr__(self, key):
            if key in self._overrides:
                return self._overrides[key]
            return getattr(self._obj, key)

    # This maps id(thing) -> replacement object for thing
    StaticReplaces = {}

    class FakeQtGui:
        """
        Qt 6 moved QAction from QtWidgets to QtGui, so we need qm(QtGui)
        to grab missing attributes ("QAction") from QtWidgets
        """
        def __getattr__(self, key):
            if hasattr(QtGui, key):
                return getattr(QtGui, key)
            return getattr(QtWidgets, key)

    StaticReplaces.update({
        id(QtGui): FakeQtGui(),
    })

    # Return value format for QtWidgets.QFileDialog.get[Open|Save]FileName() changed in PyQt5:

    if QtCompatVersion < (5,0,0):
        def QtW_QFD_getOpenFileName(*args, **kwargs):
            return QtWidgets.QFileDialog.getOpenFileName(*args, **kwargs), ''
        def QtW_QFD_getSaveFileName(*args, **kwargs):
            return QtWidgets.QFileDialog.getSaveFileName(*args, **kwargs), ''
    else:
        QtW_QFD_getOpenFileName = QtWidgets.QFileDialog.getOpenFileName
        QtW_QFD_getSaveFileName = QtWidgets.QFileDialog.getSaveFileName
    StaticReplaces[id(QtWidgets.QFileDialog.getOpenFileName)] = QtW_QFD_getOpenFileName
    StaticReplaces[id(QtWidgets.QFileDialog.getSaveFileName)] = QtW_QFD_getSaveFileName


    def qm(obj):
        """
        Magic Qt Compatibility Wrapper (pre-PyQt6 version):
        Wherever PyQt6 spells something differently from
        PyQt4/PyQt5/PySide2, just add a call to qm() and it'll return a
        wrapper object that adds the PyQt6 syntax.

        For example:
        PyQt4/5:      QtWidgets.QAction()
        PyQt6:        QtGui.QAction()
        Safe for all: qm(QtGui.QAction)()

        This lets the application use the closest possible thing to
        straight PyQt6 syntax while still retaining PyQt4/5
        compatibility, and minimizes the amount of Qt compatibility code
        in the app itself.
        """

        # Handle simple cases that we were able to precompute at launch time
        global StaticReplaces
        result = StaticReplaces.get(id(obj))
        if result is not None:
            return result

        if hasattr(QtCore, 'QVariant') and isinstance(obj, QtCore.QVariant):
            # https://www.riverbankcomputing.com/static/Docs/PyQt5/pyqt_qvariant.html
            # Qt 4 syntax: obj.toPyObject()
            # Qt 5+ syntax: obj
            return obj.toPyObject()

        if isinstance(obj, QtGui.QMouseEvent):
            # Qt 4/5 syntax: obj.pos() -> QPoint
            # Qt 6 syntax: obj.position() -> QPointF (then call .toPoint() to get QPoint if desired)
            return Wrapper(obj, {
                'position': (lambda: QtCore.QPointF(obj.pos())),
            })

        if isinstance(obj, QtWidgets.QButtonGroup):
            # renamed in PyQt6: QButtonGroup.buttonClicked[int] -> QButtonGroup.idClicked
            return Wrapper(obj, {
                'idClicked': obj.buttonClicked[int],
            })

        # We need to just return the original value if we couldn't find
        # a replacement, since it could be, say, a str that *might* have
        # been a QVariant if we were running on PyQt4
        return obj

else:

    def qm(obj):
        """
        Magic Qt Compatibility Wrapper (dummy PyQt6 version)
        """
        # For PyQt6, qm() is just the identity function.
        # This means that if you ignore / get rid of all of the qm()
        # calls, the app is using correct PyQt6 syntax.
        return obj
