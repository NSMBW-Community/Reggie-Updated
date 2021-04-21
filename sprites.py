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

from reggie import importQt

QtCore, QtGui, QtWidgets, QtCompatVersion, QtBindingsVersion, QtName = importQt()

# Some Py2/Py3 compatibility helpers
_ord = ord
def ord(x):
    if isinstance(x, int):
        return x
    return _ord(x)

OutlineColour = None
OutlinePen = None
OutlineBrush = None
ImageCache = None
Tiles = None

# NOTE: standard sprite z-value is 25000

def Setup():
    global OutlineColour, OutlinePen, OutlineBrush, ImageCache
    OutlineColour = QtGui.QColor.fromRgb(255, 255, 255, 80)
    OutlinePen = QtGui.QPen(OutlineColour, 4)
    OutlineBrush = QtGui.QBrush(OutlineColour)
    ImageCache = {}
    LoadBasicSuite()
    LoadEnvItems()
    LoadMovableItems()


class AuxiliaryItem(QtWidgets.QGraphicsItem):
    """Base class for auxiliary objects that accompany specific sprite types"""
    def __init__(self, parent):
        """Generic constructor for auxiliary items"""
        QtWidgets.QGraphicsItem.__init__(self)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, True)
        self.setParentItem(parent)

    def boundingRect(self):
        """Required for Qt"""
        return self.BoundingRect


class AuxiliaryTrackObject(AuxiliaryItem):
    """Track shown behind moving platforms to show where they can move"""
    Horizontal = 1
    Vertical = 2

    def __init__(self, parent, width, height, direction):
        """Constructor"""
        AuxiliaryItem.__init__(self, parent)

        self.BoundingRect = QtCore.QRectF(0,0,width*1.5,height*1.5)
        self.setPos(0,0)
        self.width = width
        self.height = height
        self.direction = direction

    def SetSize(self, width, height):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0,0,width*1.5,height*1.5)
        self.width = width
        self.height = height

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)

        if self.direction == 1:
            lineY = self.height * 0.75
            painter.drawLine(QtCore.QLineF(20, lineY, (self.width*1.5) - 20, lineY))
            painter.drawEllipse(QtCore.QRectF(8, lineY - 4, 8, 8))
            painter.drawEllipse(QtCore.QRectF((self.width*1.5) - 16, lineY - 4, 8, 8))
        elif self.direction == 2:
            lineX = self.width * 0.75
            painter.drawLine(QtCore.QLineF(lineX, 20, lineX, (self.height*1.5) - 20))
            painter.drawEllipse(QtCore.QRectF(lineX - 4, 8, 8, 8))
            painter.drawEllipse(QtCore.QRectF(lineX - 4, (self.height*1.5) - 16, 8, 8))


class AuxiliaryCircleOutline(AuxiliaryItem):
    def __init__(self, parent, width):
        """Constructor"""
        AuxiliaryItem.__init__(self, parent)

        self.BoundingRect = QtCore.QRectF(0,0,width*1.5,width*1.5)
        self.setPos((8 - (width / 2)) * 1.5, 0)
        self.width = width

    def SetSize(self, width):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0,0,width*1.5,width*1.5)
        self.setPos((8 - (width / 2)) * 1.5, 0)
        self.width = width

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawEllipse(self.BoundingRect)

class AuxiliaryRotationAreaOutline(AuxiliaryItem):
    def __init__(self, parent, width):
        """Constructor"""
        AuxiliaryItem.__init__(self, parent)

        self.BoundingRect = QtCore.QRectF(0,0,width*1.5,width*1.5)
        self.setPos((8 - (width / 2)) * 1.5, (8 - (width / 2)) * 1.5)
        self.width = width
        self.startAngle = 0
        self.spanAngle = 0

    def SetAngle(self, startAngle, spanAngle):
        self.startAngle = int(startAngle * 16)
        self.spanAngle = int(spanAngle * 16)

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawPie(self.BoundingRect, self.startAngle, self.spanAngle)


class AuxiliaryImage(AuxiliaryItem):
    def __init__(self, parent, width, height):
        """Constructor"""
        AuxiliaryItem.__init__(self, parent)
        self.BoundingRect = QtCore.QRectF(0,0,width,height)

    def SetSize(self, width, height):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.width = width
        self.height = height

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.drawPixmap(0, 0, self.image)

# ---- Initialisers ----
def InitGoomba(sprite): # 20
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Goomba']
    return (-1,-4,18,20)

def InitParagoomba(sprite): # 21
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Paragoomba']
    return (1,-10,24,26)

def InitMicrogoomba(sprite): # 200
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Microgoomba']
    return (4,8,9,9)

def InitGiantgoomba(sprite): # 198
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Giantgoomba']
    return (-6,-19,32,36)

def InitMegagoomba(sprite): # 199
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Megagoomba']
    return (-11,-37,43,54)

def InitHorzMovingPlatform(sprite): # 23
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    xsize = ((ord(sprite.spritedata[5]) & 0xF) + 1) << 4

    sprite.dynamicSize = True
    sprite.dynSizer = SizeHorzMovingPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintWoodenPlatform

    sprite.aux = AuxiliaryTrackObject(sprite, xsize, 16, AuxiliaryTrackObject.Horizontal)
    return (0,0,xsize,16)

def InitBuzzyBeetle(sprite): # 24
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBuzzyBeetle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    return (0,0,16,16)

def InitSpiny(sprite): # 25
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Spiny']
    return (0,0,16,16)

def InitUpsideDownSpiny(sprite): # 26
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpinyU']
    return (0,0,16,16)

def InitUnusedVertStoneBlock(sprite): # 27
    if 'DSBlockTop' not in ImageCache:
        LoadDSStoneBlocks()

    height = (ord(sprite.spritedata[4]) & 3) >> 4
    ysize = 4 << height

    sprite.dynamicSize = True
    sprite.dynSizer = SizeUnusedVertStoneBlock
    sprite.customPaint = True
    sprite.customPainter = PaintDSStoneBlock

    sprite.aux = AuxiliaryTrackObject(sprite, 32, ysize, AuxiliaryTrackObject.Vertical)
    return (0,0,32,ysize)

def InitUnusedHorzStoneBlock(sprite): # 28
    if 'DSBlockTop' not in ImageCache:
        LoadDSStoneBlocks()

    height = (ord(sprite.spritedata[4]) & 3) >> 4
    ysize = 4 << height

    sprite.dynamicSize = True
    sprite.dynSizer = SizeUnusedHorzStoneBlock
    sprite.customPaint = True
    sprite.customPainter = PaintDSStoneBlock

    sprite.aux = AuxiliaryTrackObject(sprite, 32, ysize, AuxiliaryTrackObject.Horizontal)
    return (0,0,32,ysize)

def InitVertMovingPlatform(sprite): # 31
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    xsize = ((ord(sprite.spritedata[5]) & 0xF) + 1) << 4

    sprite.dynamicSize = True
    sprite.dynSizer = SizeVertMovingPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintWoodenPlatform

    sprite.aux = AuxiliaryTrackObject(sprite, xsize, 16, AuxiliaryTrackObject.Vertical)
    return (0,0,xsize,16)

def InitStarCoin(sprite): # 32, 155, 389
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['StarCoin']
    return (0,3,32,32)

def InitQuestionSwitch(sprite): # 40
    if 'QSwitch' not in ImageCache:
        LoadSwitches()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSwitch
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.switchType = 'Q'
    return (0,0,16,16)

def InitPSwitch(sprite): # 41
    if 'PSwitch' not in ImageCache:
        LoadSwitches()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSwitch
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.switchType = 'P'
    return (0,0,16,16)

def InitExcSwitch(sprite): # 42
    if 'ESwitch' not in ImageCache:
        LoadSwitches()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSwitch
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.switchType = 'E'
    return (0,0,16,16)

def InitQuestionSwitchBlock(sprite): # 43
    if 'QSwitch' not in ImageCache:
        LoadSwitches()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['QSwitchBlock']
    return (0,0,16,16)

def InitPSwitchBlock(sprite): # 44
    if 'PSwitch' not in ImageCache:
        LoadSwitches()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PSwitchBlock']
    return (0,0,16,16)

def InitExcSwitchBlock(sprite): # 45
    if 'ESwitch' not in ImageCache:
        LoadSwitches()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ESwitchBlock']
    return (0,0,16,16)

def InitPodoboo(sprite): # 46
    if 'Podoboo' not in ImageCache:
        LoadCastleStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Podoboo']
    return (0,0,16,16)

def InitThwomp(sprite): # 47
    if 'Thwomp' not in ImageCache:
        LoadCastleStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Thwomp']
    return (-6,-6,44,50)

def InitGiantThwomp(sprite): # 48
    if 'GiantThwomp' not in ImageCache:
        LoadCastleStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GiantThwomp']
    return (-8,-8,80,94)

def InitUnused49(sprite): # 49
    if 'Unused49' not in ImageCache:
        LoadUnusedStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Unused49']
    return (2,-8,252,16)

def InitFallingPlatform(sprite): # 50
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    xsize = ((ord(sprite.spritedata[5]) & 0xF) + 1) << 4

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFallingPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintWoodenPlatform

    return (0,0,xsize,16)

def InitTiltingGirder(sprite): # 51
    if 'TiltingGirder' not in ImageCache:
        LoadPlatformImages()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['TiltingGirder']
    return (0,-18,224,38)

def InitLakitu(sprite): # 54
    if 'Lakitu' not in ImageCache:
        LoadDesertStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Lakitu']
    return (-16,-24,38,56)

def InitKoopaTroopa(sprite): # 57
    sprite.dynamicSize = True
    sprite.dynSizer = SizeKoopaTroopa
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['KoopaG']
    return (-7,-15,24,32)

def InitKoopaParatroopa(sprite): # 58
    sprite.dynamicSize = True
    sprite.dynSizer = SizeKoopaParatroopa
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ParakoopaG']
    return (-7,-12,24,29)

def InitSpikeTop(sprite): # 60
    global ImageCache
    if 'SpikeTopUL' not in ImageCache:
        SpikeTopUp = QtGui.QImage('reggiedata/sprites/spiketop.png')
        SpikeTopDown = QtGui.QImage('reggiedata/sprites/spiketop_u.png')
        ImageCache['SpikeTopUL'] = QtGui.QPixmap.fromImage(SpikeTopUp)
        ImageCache['SpikeTopUR'] = QtGui.QPixmap.fromImage(SpikeTopUp.mirrored(True, False))
        ImageCache['SpikeTopDL'] = QtGui.QPixmap.fromImage(SpikeTopDown)
        ImageCache['SpikeTopDR'] = QtGui.QPixmap.fromImage(SpikeTopDown.mirrored(True, False))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSpikeTop
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,-4,16,20)

def InitBigBoo(sprite): # 61
    global ImageCache
    if 'BigBoo' not in ImageCache:
        ImageCache['BigBoo'] = QtGui.QPixmap('reggiedata/sprites/bigboo.png')

    sprite.aux = AuxiliaryImage(sprite, 243, 248)
    sprite.aux.image = ImageCache['BigBoo']
    sprite.aux.setPos(-48, -48)

    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (-38,-80,96,96)

def InitSpikeBall(sprite): # 63
    if 'SpikeBall' not in ImageCache:
        LoadCastleStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpikeBall']
    return (0,0,32,32)

def InitPipePiranhaUp(sprite): # 65
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipePlantUp']
    return (2,-32,28,32)

def InitPipePiranhaDown(sprite): # 66
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipePlantDown']
    return (2,32,28,32)

def InitPipePiranhaRight(sprite): # 67
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipePlantRight']
    return (32,2,32,28)

def InitPipePiranhaLeft(sprite): # 68
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipePlantLeft']
    return (-32,2,32,28)

def InitPipeFiretrapUp(sprite): # 69
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipeFiretrapUp']
    return (-4,-29,29,29)

def InitPipeFiretrapDown(sprite): # 70
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipeFiretrapDown']
    return (-4,32,29,29)

def InitPipeFiretrapRight(sprite): # 71
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipeFiretrapRight']
    return (32,6,29,29)

def InitPipeFiretrapLeft(sprite): # 72
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipeFiretrapLeft']
    return (-29,6,29,29)

def InitGroundPiranha(sprite): # 73
    sprite.dynamicSize = True
    sprite.dynSizer = SizeGroundPiranha
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GroundPiranha']
    return (-20,0,48,26)

def InitBigGroundPiranha(sprite): # 74
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBigGroundPiranha
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BigGroundPiranha']
    return (-65,0,96,52)

def InitGroundFiretrap(sprite): # 75
    sprite.dynamicSize = True
    sprite.dynSizer = SizeGroundFiretrap
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GroundFiretrap']
    return (5,0,24,44)

def InitBigGroundFiretrap(sprite): # 76
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBigGroundFiretrap
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BigGroundFiretrap']
    return (-14,0,47,88)

def InitShipKey(sprite): # 77
    global ImageCache
    if 'ShipKey' not in ImageCache:
        ImageCache['ShipKey'] = QtGui.QPixmap('reggiedata/sprites/ship_key.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ShipKey']
    return (-1,-8,19,24)

def InitCloudTrampoline(sprite): # 78
    global ImageCache
    if 'CloudTrBig' not in ImageCache:
        ImageCache['CloudTrBig'] = QtGui.QPixmap('reggiedata/sprites/cloud_trampoline_big.png')
        ImageCache['CloudTrSmall'] = QtGui.QPixmap('reggiedata/sprites/cloud_trampoline_small.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeCloudTrampoline
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-2,-2,16,16)

def InitFireBro(sprite): # 80
    global ImageCache
    if 'FireBro' not in ImageCache:
        ImageCache['FireBro'] = QtGui.QPixmap('reggiedata/sprites/firebro.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FireBro']
    return (-8,-22,26,38)

def InitOldStoneBlock(sprite): # 81, 82, 83, 84, 85, 86
    global ImageCache
    if 'OldStoneTL' not in ImageCache:
        ImageCache['OldStoneTL'] = QtGui.QPixmap('reggiedata/sprites/oldstone_tl.png')
        ImageCache['OldStoneT'] = QtGui.QPixmap('reggiedata/sprites/oldstone_t.png')
        ImageCache['OldStoneTR'] = QtGui.QPixmap('reggiedata/sprites/oldstone_tr.png')
        ImageCache['OldStoneL'] = QtGui.QPixmap('reggiedata/sprites/oldstone_l.png')
        ImageCache['OldStoneM'] = QtGui.QPixmap('reggiedata/sprites/oldstone_m.png')
        ImageCache['OldStoneR'] = QtGui.QPixmap('reggiedata/sprites/oldstone_r.png')
        ImageCache['OldStoneBL'] = QtGui.QPixmap('reggiedata/sprites/oldstone_bl.png')
        ImageCache['OldStoneB'] = QtGui.QPixmap('reggiedata/sprites/oldstone_b.png')
        ImageCache['OldStoneBR'] = QtGui.QPixmap('reggiedata/sprites/oldstone_br.png')
        ImageCache['SpikeU'] = QtGui.QPixmap('reggiedata/sprites/spike_up.png')
        ImageCache['SpikeL'] = QtGui.QPixmap('reggiedata/sprites/spike_left.png')
        ImageCache['SpikeR'] = QtGui.QPixmap('reggiedata/sprites/spike_right.png')
        ImageCache['SpikeD'] = QtGui.QPixmap('reggiedata/sprites/spike_down.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeOldStoneBlock
    sprite.customPaint = True
    sprite.customPainter = PaintOldStoneBlock
    sprite.aux = AuxiliaryTrackObject(sprite, 16, 16, AuxiliaryTrackObject.Horizontal)
    return (0,0,16,16)

def InitBulletBillLauncher(sprite): # 92
    global ImageCache
    if 'BBLauncherT' not in ImageCache:
        ImageCache['BBLauncherT'] = QtGui.QPixmap('reggiedata/sprites/bullet_launcher_top.png')
        ImageCache['BBLauncherM'] = QtGui.QPixmap('reggiedata/sprites/bullet_launcher_middle.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBulletBillLauncher
    sprite.customPaint = True
    sprite.customPainter = PaintBulletBillLauncher
    return (0,0,16,16)

def InitBanzaiBillLauncher(sprite): # 93
    global ImageCache
    if 'BanzaiLauncher' not in ImageCache:
        ImageCache['BanzaiLauncher'] = QtGui.QPixmap('reggiedata/sprites/banzai_launcher.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BanzaiLauncher']
    return (-32,-68,64,84)

def InitBoomerangBro(sprite): # 94
    global ImageCache
    if 'BoomerangBro' not in ImageCache:
        ImageCache['BoomerangBro'] = QtGui.QPixmap('reggiedata/sprites/boomerangbro.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BoomerangBro']
    return (-8,-22,25,38)

def InitHammerBro(sprite): # 95, 308
    global ImageCache
    if 'HammerBro' not in ImageCache:
        ImageCache['HammerBro'] = QtGui.QPixmap('reggiedata/sprites/hammerbro.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['HammerBro']
    return (-8,-24,25,40)

def InitRotationControllerSwaying(sprite): # 96
    sprite.setZValue(100000)
    sprite.dynamicSize = True
    sprite.dynSizer = SizeRotationControllerSwaying

    sprite.aux = AuxiliaryRotationAreaOutline(sprite, 48)
    return (0,0,16,16)

def InitGiantSpikeBall(sprite): # 98
    if 'SpikeBall' not in ImageCache:
        LoadCastleStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GiantSpikeBall']
    return (-32,-16,64,64)

def InitSwooper(sprite): # 100
    global ImageCache
    if 'Swooper' not in ImageCache:
        ImageCache['Swooper'] = QtGui.QPixmap('reggiedata/sprites/swooper.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Swooper']
    return (2,0,11,18)

def InitBobomb(sprite): # 101
    global ImageCache
    if 'Bobomb' not in ImageCache:
        ImageCache['Bobomb'] = QtGui.QPixmap('reggiedata/sprites/bobomb.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Bobomb']
    return (-8,-8,21,24)

def InitBroozer(sprite): # 102
    global ImageCache
    if 'Broozer' not in ImageCache:
        ImageCache['Broozer'] = QtGui.QPixmap('reggiedata/sprites/broozer.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Broozer']
    return (-9,-17,34,34)

def InitPlatformGenerator(sprite): # 103
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    sprite.dynamicSize = True
    sprite.dynSizer = SizePlatformGenerator
    sprite.customPaint = True
    sprite.customPainter = PaintPlatformGenerator
    return (0,0,16,16)

def InitAmp(sprite): # 104, 108
    global ImageCache
    if 'Amp' not in ImageCache:
        ImageCache['Amp'] = QtGui.QPixmap('reggiedata/sprites/amp.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Amp']
    return (-8,-8,40,34)

def InitPokey(sprite): # 105
    if 'PokeyTop' not in ImageCache:
        LoadDesertStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizePokey
    sprite.customPaint = True
    sprite.customPainter = PaintPokey
    return (-4,0,24,32)

def InitLinePlatform(sprite): # 106
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeLinePlatform
    sprite.customPaint = True
    sprite.customPainter = PaintWoodenPlatform
    return (0,8,16,16)

def InitChainBall(sprite): # 109
    global ImageCache
    if 'ChainBallU' not in ImageCache:
        ImageCache['ChainBallU'] = QtGui.QPixmap('reggiedata/sprites/chainball_up.png')
        ImageCache['ChainBallR'] = QtGui.QPixmap('reggiedata/sprites/chainball_right.png')
        ImageCache['ChainBallD'] = QtGui.QPixmap('reggiedata/sprites/chainball_down.png')
        ImageCache['ChainBallL'] = QtGui.QPixmap('reggiedata/sprites/chainball_left.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeChainBall
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitBlooper(sprite): # 111
    global ImageCache
    if 'Blooper' not in ImageCache:
        ImageCache['Blooper'] = QtGui.QPixmap('reggiedata/sprites/blooper.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Blooper']
    return (-3,-2,23,30)

def InitBlooperBabies(sprite): # 112
    global ImageCache
    if 'BlooperBabies' not in ImageCache:
        ImageCache['BlooperBabies'] = QtGui.QPixmap('reggiedata/sprites/blooper_babies.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BlooperBabies']
    return (-5,-2,27,36)

def InitFlagpole(sprite): # 113
    if 'Flagpole' not in ImageCache:
        LoadFlagpole()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFlagpole
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Flagpole']

    sprite.aux = AuxiliaryImage(sprite, 144, 149)
    return (-30,-144,46,160)

def InitCheep(sprite): # 115
    global ImageCache
    if 'CheepRed' not in ImageCache:
        ImageCache['CheepRed'] = QtGui.QPixmap('reggiedata/sprites/cheep_red.png')
        ImageCache['CheepGreen'] = QtGui.QPixmap('reggiedata/sprites/cheep_green.png')
        ImageCache['CheepYellow'] = QtGui.QPixmap('reggiedata/sprites/cheep_yellow.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeCheep
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-1,-1,19,18)

def InitDryBones(sprite): # 118
    global ImageCache
    if 'DryBones' not in ImageCache:
        ImageCache['DryBones'] = QtGui.QPixmap('reggiedata/sprites/drybones.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['DryBones']
    return (-7,-16,23,32)

def InitGiantDryBones(sprite): # 119
    global ImageCache
    if 'GiantDryBones' not in ImageCache:
        ImageCache['GiantDryBones'] = QtGui.QPixmap('reggiedata/sprites/giant_drybones.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GiantDryBones']
    return (-13,-24,29,40)

def InitSledgeBro(sprite): # 120
    global ImageCache
    if 'SledgeBro' not in ImageCache:
        ImageCache['SledgeBro'] = QtGui.QPixmap('reggiedata/sprites/sledgebro.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SledgeBro']
    return (-8,-28.5,32,45)

def InitOneWayPlatform(sprite): # 122
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeOneWayPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintWoodenPlatform
    return (0,0,16,16)

def InitFenceKoopaHorz(sprite): # 125
    global ImageCache
    if 'FenceKoopaH' not in ImageCache:
        ImageCache['FenceKoopaH'] = QtGui.QPixmap('reggiedata/sprites/fencekoopa_horz.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FenceKoopaH']
    return (-3,-12,22,30)

def InitFenceKoopaVert(sprite): # 126
    global ImageCache
    if 'FenceKoopaV' not in ImageCache:
        ImageCache['FenceKoopaV'] = QtGui.QPixmap('reggiedata/sprites/fencekoopa_vert.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FenceKoopaV']
    return (-2,-12,22,31)

def InitFlipFence(sprite): # 127
    global ImageCache
    if 'FlipFence' not in ImageCache:
        ImageCache['FlipFence'] = QtGui.QPixmap('reggiedata/sprites/flipfence.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FlipFence']
    return (-4,-8,40,48)

def InitFlipFenceLong(sprite): # 128
    global ImageCache
    if 'FlipFenceLong' not in ImageCache:
        ImageCache['FlipFenceLong'] = QtGui.QPixmap('reggiedata/sprites/flipfence_long.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FlipFenceLong']
    return (6,0,180,64)

def Init4Spinner(sprite): # 129
    global ImageCache
    if '4Spinner' not in ImageCache:
        ImageCache['4Spinner'] = QtGui.QPixmap('reggiedata/sprites/4spinner.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['4Spinner']
    return (-62,-48,142,112)

def InitWiggler(sprite): # 130
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Wiggler']
    return (0,-12,54,28)

def InitBoo(sprite): # 131
    global ImageCache
    if 'Boo' not in ImageCache:
        ImageCache['Boo'] = QtGui.QPixmap('reggiedata/sprites/boo.png')

    sprite.aux = AuxiliaryImage(sprite, 50, 51)
    sprite.aux.image = ImageCache['Boo']
    sprite.aux.setPos(-11, -11)

    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (-1,-4,22,22)

def InitStalagmitePlatform(sprite): # 133
    global ImageCache
    if 'StalagmitePlatformTop' not in ImageCache:
        ImageCache['StalagmitePlatformTop'] = QtGui.QPixmap('reggiedata/sprites/stalagmite_platform_top.png')
        ImageCache['StalagmitePlatformBottom'] = QtGui.QPixmap('reggiedata/sprites/stalagmite_platform_bottom.png')

    sprite.aux = AuxiliaryImage(sprite, 48, 156)
    sprite.aux.image = ImageCache['StalagmitePlatformBottom']
    sprite.aux.setPos(24, 60)

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['StalagmitePlatformTop']
    return (0,-8,64,40)

def InitCrow(sprite): # 134
    global ImageCache
    if 'Crow' not in ImageCache:
        ImageCache['Crow'] = QtGui.QPixmap('reggiedata/sprites/crow.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Crow']
    return (-3,-2,27,18)

def InitHangingPlatform(sprite): # 135
    global ImageCache
    if 'HangingPlatformTop' not in ImageCache:
        ImageCache['HangingPlatformTop'] = QtGui.QPixmap('reggiedata/sprites/hanging_platform_top.png')
        ImageCache['HangingPlatformBottom'] = QtGui.QPixmap('reggiedata/sprites/hanging_platform_bottom.png')

    sprite.aux = AuxiliaryImage(sprite, 11, 378)
    sprite.aux.image = ImageCache['HangingPlatformTop']
    sprite.aux.setPos(138,-378)

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['HangingPlatformBottom']
    return (0,0,192,32)

def InitSpikedStake(sprite): # 137, 140, 141, 142
    global ImageCache
    if 'StakeM0up' not in ImageCache:
        for dir in ['up', 'down', 'left', 'right']:
            ImageCache['StakeM0%s' % dir] = QtGui.QPixmap('reggiedata/sprites/stake_%s_m_0.png' % dir)
            ImageCache['StakeM1%s' % dir] = QtGui.QPixmap('reggiedata/sprites/stake_%s_m_1.png' % dir)
            ImageCache['StakeE0%s' % dir] = QtGui.QPixmap('reggiedata/sprites/stake_%s_e_0.png' % dir)
            ImageCache['StakeE1%s' % dir] = QtGui.QPixmap('reggiedata/sprites/stake_%s_e_1.png' % dir)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSpikedStake
    sprite.customPaint = True
    sprite.customPainter = PaintSpikedStake
    return (0,0,16,16)

def InitArrow(sprite): # 143
    global ImageCache
    if 'Arrow0' not in ImageCache:
        for i in range(8):
            ImageCache['Arrow%d' % i] = QtGui.QPixmap('reggiedata/sprites/arrow_%d.png' % i)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeArrow
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitRedCoin(sprite): # 144
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RedCoin']
    return (0,0,16,16)

def InitChainChomp(sprite): # 146
    global ImageCache
    if 'ChainChomp' not in ImageCache:
        ImageCache['ChainChomp'] = QtGui.QPixmap('reggiedata/sprites/chain_chomp.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ChainChomp']
    return (-90,-32,109,54)

def InitCoin(sprite): # 147
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Coin']
    return (0,0,16,16)

def InitSpring(sprite): # 148
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Spring']
    return (0,0,16,16)

def InitRotationControllerSpinning(sprite): # 149
    sprite.setZValue(100000)
    return (0,0,16,16)

def InitPuffer(sprite): # 151
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Puffer']
    return (-16,-18,58,54)

def InitRedCoinRing(sprite): # 156
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RedCoinRing']
    return (-18,-15,51,63)

def InitFireSnake(sprite): # 158
    global ImageCache
    if 'FireSnake' not in ImageCache:
        LoadFireSnake()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFireSnake
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitScrewMushroom(sprite): # 172, 382
    global ImageCache
    if 'Bolt' not in ImageCache:
        ImageCache['Bolt'] = QtGui.QPixmap('reggiedata/sprites/bolt.png')
    if 'ScrewShroomT' not in ImageCache:
        ImageCache['ScrewShroomT'] = QtGui.QPixmap('reggiedata/sprites/screw_shroom_top.png')
        ImageCache['ScrewShroomM'] = QtGui.QPixmap('reggiedata/sprites/screw_shroom_middle.png')
        ImageCache['ScrewShroomB'] = QtGui.QPixmap('reggiedata/sprites/screw_shroom_bottom.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeScrewMushroom
    sprite.customPaint = True
    sprite.customPainter = PaintScrewMushroom
    return (0,0,16,16)

def InitGiantFloatingLog(sprite): # 173
    global ImageCache
    if 'GiantFloatingLog' not in ImageCache:
        ImageCache['GiantFloatingLog'] = QtGui.QPixmap('reggiedata/sprites/giant_floating_log.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GiantFloatingLog']
    return (-152,-32,304,64)

def InitFlyingQBlock(sprite): # 175
    global ImageCache
    if 'FlyingQBlockY' not in ImageCache:
        LoadFlyingBlocks()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFlyingQBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    return (-12,-16,46,36)

def InitRouletteBlock(sprite): # 176
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RouletteBlock']
    return (-6,-6,29,29)

def InitScalePlatform(sprite): # 178
    global ImageCache
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()
    if 'ScaleRopeH' not in ImageCache:
        ImageCache['ScaleRopeH'] = QtGui.QPixmap('reggiedata/sprites/scale_rope_horz.png')
        ImageCache['ScaleRopeV'] = QtGui.QPixmap('reggiedata/sprites/scale_rope_vert.png')
        ImageCache['ScalePulley'] = QtGui.QPixmap('reggiedata/sprites/scale_pulley.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeScalePlatform
    sprite.customPaint = True
    sprite.customPainter = PaintScalePlatform
    return (0,-10,150,150)

def InitCheepChomp(sprite): # 180
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CheepChomp']
    return (-24,-30,76,66)

def InitToadBalloon(sprite): #185
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ToadBalloon']
    return (-4,-4,24,24)

def InitPlayerBlock(sprite): # 187
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PlayerBlock']
    return (0,0,16,16)

def InitMidwayPoint(sprite): # 188
    if 'MidwayFlag' not in ImageCache:
        LoadFlagpole()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MidwayFlag']
    return (0,-37,33,54)

def InitUrchin(sprite): # 193
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Urchin']
    return (-12,-14,39,38)

def InitMegaUrchin(sprite): # 194
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MegaUrchin']
    return (-40,-46,113,108)

def InitHuckit(sprite): # 195
    global ImageCache
    if 'Huckit' not in ImageCache:
        LoadCrabs() # previously GetCrabs lol
    sprite.dynamicSize = True
    sprite.dynSizer = SizeHuckit
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-14,-2,32,19)

def InitFishbones(sprite): # 196
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Fishbones']
    return (0,-2,28,18)

def InitClam(sprite): # 197
    global ImageCache
    if 'Clam0' not in ImageCache:
        LoadClams()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeClam
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-28,-50,74,70)

def InitIcicle(sprite): # 201
    global ImageCache
    if 'IcicleSmall' not in ImageCache:
        LoadIceStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeIcicle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitMGCannon(sprite): # 202
    if 'MGCannon' not in ImageCache:
        LoadMinigameStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MGCannon']
    return (-12,-42,42,60)

def InitMGChest(sprite): # 203
    if 'MGChest' not in ImageCache:
        LoadMinigameStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MGChest']
    return (-12,-11,40,27)

RollingHillSizes = [2*16, 18*16, 32*16, 50*16, 64*16, 10*16, 14*16, 20*16, 0, 0, 0, 0, 0, 0, 0, 0]
def InitRollingHill(sprite): # 212
    size = (ord(sprite.spritedata[3]) >> 4) & 0xF
    realSize = RollingHillSizes[size]

    sprite.dynamicSize = True
    sprite.dynSizer = SizeRollingHill

    sprite.aux = AuxiliaryCircleOutline(sprite, realSize)
    return (0,0,16,16)

def InitSpringBlock(sprite): # 223
    sprite.dynamicSize = True
    sprite.dynSizer = SizeSpringBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    return (0,0,16,16)

def InitJumboRay(sprite): # 224
    global ImageCache
    if 'JumboRay' not in ImageCache:
        Ray = QtGui.QImage('reggiedata/sprites/jumbo_ray.png')
        ImageCache['JumboRayL'] = QtGui.QPixmap.fromImage(Ray)
        ImageCache['JumboRayR'] = QtGui.QPixmap.fromImage(Ray.mirrored(True, False))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeJumboRay
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,171,79)

def InitPipeCannon(sprite): #227
    global ImageCache
    if 'PipeCannon' not in ImageCache:
        LoadPipeCannon()

    sprite.dynamicSize = True
    sprite.dynSizer = SizePipeCannon
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,55,64)

def InitExtendShroom(sprite): # 228
    global ImageCache
    if 'ExtendShroomL' not in ImageCache:
        ImageCache['ExtendShroomB'] = QtGui.QPixmap('reggiedata/sprites/extend_shroom_big.png')
        ImageCache['ExtendShroomS'] = QtGui.QPixmap('reggiedata/sprites/extend_shroom_small.png')
        ImageCache['ExtendShroomC'] = QtGui.QPixmap('reggiedata/sprites/extend_shroom_cont.png')
        ImageCache['ExtendShroomStem'] = QtGui.QPixmap('reggiedata/sprites/extend_shroom_stem.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeExtendShroom
    sprite.customPaint = True
    sprite.customPainter = PaintExtendShroom

    return (0,0,16,16)

def InitBramball(sprite): # 230
    global ImageCache
    if 'Bramball' not in ImageCache:
        ImageCache['Bramball'] = QtGui.QPixmap('reggiedata/sprites/bramball.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Bramball']
    return (-32,-48,80,64)

def InitWiggleShroom(sprite): # 231
    global ImageCache
    if 'WiggleShroomL' not in ImageCache:
        ImageCache['WiggleShroomL'] = QtGui.QPixmap('reggiedata/sprites/wiggle_shroom_left.png')
        ImageCache['WiggleShroomM'] = QtGui.QPixmap('reggiedata/sprites/wiggle_shroom_middle.png')
        ImageCache['WiggleShroomR'] = QtGui.QPixmap('reggiedata/sprites/wiggle_shroom_right.png')
        ImageCache['WiggleShroomS'] = QtGui.QPixmap('reggiedata/sprites/wiggle_shroom_stem.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeWiggleShroom
    sprite.customPaint = True
    sprite.customPainter = PaintWiggleShroom

    return (0,0,16,16)

def InitMechaKoopa(sprite): # 232
    global ImageCache
    if 'Mechakoopa' not in ImageCache:
        ImageCache['Mechakoopa'] = QtGui.QPixmap('reggiedata/sprites/mechakoopa.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Mechakoopa']
    return (-8,-14,30,32)

def InitBulber(sprite): #233
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Bulber']
    return (-16,-16,56,42)

def InitPCoin(sprite): # 237
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PCoin']
    return (0,0,16,16)

def InitFoo(sprite): # 238
    global ImageCache
    if 'Foo' not in ImageCache:
        ImageCache['Foo'] = QtGui.QPixmap('reggiedata/sprites/foo.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Foo']
    return (-8,-16,29,32)

def InitFallingLedgeBar(sprite): # 242
    global ImageCache
    if 'FallingLedgeBar' not in ImageCache:
        ImageCache['FallingLedgeBar'] = QtGui.QPixmap('reggiedata/sprites/falling_ledge_bar.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FallingLedgeBar']

    return (0,0,80,16)

def InitSpecialCoin(sprite): # 253, 371, 390
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpecialCoin']
    return (0,0,16,16)

DoorTypes = {
    182: ('Door', (0,0,32,48)), # Switch Door, same attributes as regular door
    259: ('Door', (0,0,32,48)),
    276: ('GhostDoor', (0,0,32,48)),
    277: ('TowerDoor', (-2,-10.5,53,59)),
    278: ('CastleDoor', (-2,-13,53,62)),
    452: ('BowserDoor', (-53,-134,156,183))
}
def InitDoor(sprite): # 182, 259, 276, 277, 278, 452
    sprite.dynamicSize = True
    sprite.dynSizer = SizeDoor

    sprite.customPaint = True
    if sprite.type == 182: # switch door
        sprite.customPainter = PaintAlphaObject
        sprite.alpha = 0.5
    else:
        sprite.customPainter = PaintGenericObject

    type = DoorTypes[sprite.type]
    sprite.doorType = type[0]
    sprite.doorSize = type[1]
    return type[1]

def InitPoltergeistItem(sprite): #262
    global ImageCache
    if 'PoltergeistItem' not in ImageCache:
        LoadPolterItems()

    sprite.dynamicSize = True
    sprite.dynSizer = SizePoltergeistItem
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-6,-4,30,27)

def InitWaterPiranha(sprite): # 263
    global ImageCache
    if 'WaterPiranha' not in ImageCache:
        ImageCache['WaterPiranha'] = QtGui.QPixmap('reggiedata/sprites/water_piranha.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['WaterPiranha']
    return (-5,-145,26,153)

def InitWalkingPiranha(sprite): # 264
    global ImageCache
    if 'WalkPiranha' not in ImageCache:
        ImageCache['WalkPiranha'] = QtGui.QPixmap('reggiedata/sprites/walk_piranha.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['WalkPiranha']
    return (-4,-50,23,66)

def InitFallingIcicle(sprite): # 265
    global ImageCache
    if 'IcicleSmall' not in ImageCache:
        LoadIceStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFallingIcicle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitRotatingChainLink(sprite): # 266
    global ImageCache
    if 'RotatingChainLink' not in ImageCache:
        ImageCache['RotatingChainLink'] = QtGui.QPixmap('reggiedata/sprites/rotating_chainlink.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RotatingChainLink']
    im = sprite.image
    return (-((2.0/3.0)*(im.width()/2.0-12.0)), -((2.0/3.0)*(im.height()/2.0-12.0)), (2.0/3.0)*im.width(), (2.0/3.0)*im.height())


def InitTiltGrate(sprite): # 267
    global ImageCache
    if 'TiltGrateU' not in ImageCache:
        ImageCache['TiltGrateU'] = QtGui.QPixmap('reggiedata/sprites/tilt_grate_up.png')
        ImageCache['TiltGrateD'] = QtGui.QPixmap('reggiedata/sprites/tilt_grate_down.png')
        ImageCache['TiltGrateL'] = QtGui.QPixmap('reggiedata/sprites/tilt_grate_left.png')
        ImageCache['TiltGrateR'] = QtGui.QPixmap('reggiedata/sprites/tilt_grate_right.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeTiltGrate
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitParabomb(sprite): # 269
    global ImageCache
    if 'Parabomb' not in ImageCache:
        ImageCache['Parabomb'] = QtGui.QPixmap('reggiedata/sprites/parabomb.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Parabomb']
    return (-2,-16,20,32)

def InitLittleMouser(sprite): # 271
    global ImageCache
    if 'LittleMouser0' not in ImageCache:
        LoadMice()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeLittleMouser
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    return (-6,-2,30,18)

def InitIceBro(sprite): # 272
    global ImageCache
    if 'IceBro' not in ImageCache:
        ImageCache['IceBro'] = QtGui.QPixmap('reggiedata/sprites/icebro.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['IceBro']
    return (-5,-23,26,39)

def InitCastleGear(sprite): #274
    global ImageCache
    if 'CastleGearL' not in ImageCache or 'CastleGearS' not in ImageCache:
        LoadCastleGears()
    sprite.dynamicSize = True
    sprite.dynSizer = SizeCastleGear
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    isBig = (ord(sprite.spritedata[4]) & 0xF) == 1
    sprite.image = ImageCache['CastleGearL'] if isBig else ImageCache['CastleGearS']
    return (-(((sprite.image.width()/2.0)-12)*(2.0/3.0)), -(((sprite.image.height()/2.0)-12)*(2.0/3.0)), sprite.image.width()*(2.0/3.0), sprite.image.height()*(2.0/3.0))


def InitGiantIceBlock(sprite): # 280
    global ImageCache
    if 'IcicleSmall' not in ImageCache:
        LoadIceStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeGiantIceBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,64,64)

def InitWoodCircle(sprite): # 286
    global ImageCache
    if 'WoodCircle0' not in ImageCache:
        ImageCache['WoodCircle0'] = QtGui.QPixmap('reggiedata/sprites/wood_circle_0.png')
        ImageCache['WoodCircle1'] = QtGui.QPixmap('reggiedata/sprites/wood_circle_1.png')
        ImageCache['WoodCircle2'] = QtGui.QPixmap('reggiedata/sprites/wood_circle_2.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeWoodCircle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitOldBarrel(sprite): # 288
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['OldBarrel']
    return (1,-7,30,30)

def InitBox(sprite): # 289
    global ImageCache
    if 'BoxWoodSmall' not in ImageCache:
        ImageCache['BoxWoodSmall'] = QtGui.QPixmap('reggiedata/sprites/box_wood_small.png')
        ImageCache['BoxWoodWide'] = QtGui.QPixmap('reggiedata/sprites/box_wood_wide.png')
        ImageCache['BoxWoodTall'] = QtGui.QPixmap('reggiedata/sprites/box_wood_tall.png')
        ImageCache['BoxWoodBig'] = QtGui.QPixmap('reggiedata/sprites/box_wood_big.png')
        ImageCache['BoxMetalSmall'] = QtGui.QPixmap('reggiedata/sprites/box_metal_small.png')
        ImageCache['BoxMetalWide'] = QtGui.QPixmap('reggiedata/sprites/box_metal_wide.png')
        ImageCache['BoxMetalTall'] = QtGui.QPixmap('reggiedata/sprites/box_metal_tall.png')
        ImageCache['BoxMetalBig'] = QtGui.QPixmap('reggiedata/sprites/box_metal_big.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBox
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,32,32)

def InitParabeetle(sprite): # 291
    global ImageCache
    if 'Parabeetle0' not in ImageCache:
        ImageCache['Parabeetle0'] = QtGui.QPixmap('reggiedata/sprites/parabeetle_right.png')
        ImageCache['Parabeetle1'] = QtGui.QPixmap('reggiedata/sprites/parabeetle_left.png')
        ImageCache['Parabeetle2'] = QtGui.QPixmap('reggiedata/sprites/parabeetle_moreright.png')
        ImageCache['Parabeetle3'] = QtGui.QPixmap('reggiedata/sprites/parabeetle_atyou.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeParabeetle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,-8,16,28)

def InitHeavyParabeetle(sprite): # 292
    global ImageCache
    if 'HeavyParabeetle0' not in ImageCache:
        ImageCache['HeavyParabeetle0'] = QtGui.QPixmap('reggiedata/sprites/heavy_parabeetle_right.png')
        ImageCache['HeavyParabeetle1'] = QtGui.QPixmap('reggiedata/sprites/heavy_parabeetle_left.png')
        ImageCache['HeavyParabeetle2'] = QtGui.QPixmap('reggiedata/sprites/heavy_parabeetle_moreright.png')
        ImageCache['HeavyParabeetle3'] = QtGui.QPixmap('reggiedata/sprites/heavy_parabeetle_atyou.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeHeavyParabeetle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,-58,16,67)

def InitIceCube(sprite): # 294
    global ImageCache
    if 'IceCube' not in ImageCache:
        ImageCache['IceCube'] = QtGui.QPixmap('reggiedata/sprites/ice_cube.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['IceCube']
    return (0,0,16,16)

def InitMegaBuzzy(sprite): # 296
    global ImageCache
    if 'MegaBuzzyL' not in ImageCache:
        ImageCache['MegaBuzzyL'] = QtGui.QPixmap('reggiedata/sprites/megabuzzy_left.png')
        ImageCache['MegaBuzzyF'] = QtGui.QPixmap('reggiedata/sprites/megabuzzy_front.png')
        ImageCache['MegaBuzzyR'] = QtGui.QPixmap('reggiedata/sprites/megabuzzy_right.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.dynamicSize = True
    sprite.dynSizer = SizeMegaBuzzy
    return (-41,-80,98,96)

def InitRotCannon(sprite): # 300
    global ImageCache
    if 'RotCannon' not in ImageCache:
        ImageCache['RotCannon'] = QtGui.QPixmap('reggiedata/sprites/rot_cannon.png')
        ImageCache['RotCannonU'] = QtGui.QPixmap('reggiedata/sprites/rot_cannon_u.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeRotCannon
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitRotCannonPipe(sprite): # 301
    global ImageCache
    if 'RotCannonPipe' not in ImageCache:
        ImageCache['RotCannonPipe'] = QtGui.QPixmap('reggiedata/sprites/rot_cannon_pipe.png')
        ImageCache['RotCannonPipeU'] = QtGui.QPixmap('reggiedata/sprites/rot_cannon_pipe_u.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeRotCannonPipe
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitMontyMole(sprite): # 303
    global ImageCache
    if 'Mole' not in ImageCache:
        ImageCache['Mole'] = QtGui.QPixmap('reggiedata/sprites/monty_mole.png')
        ImageCache['MoleCave'] = QtGui.QPixmap('reggiedata/sprites/monty_mole_hole.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeMontyMole
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-6,-4,28,25)

def InitArrowSign(sprite): # 310
    global ImageCache
    if 'ArrowSign0' not in ImageCache:
        for i in range(8):
            ImageCache['ArrowSign%d' % i] = QtGui.QPixmap('reggiedata/sprites/arrow_sign_%d.png' % i)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeArrowSign
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-8,-16,32,32)

def InitMegaIcicle(sprite): # 311
    global ImageCache
    if 'MegaIcicle' not in ImageCache:
        ImageCache['MegaIcicle'] = QtGui.QPixmap('reggiedata/sprites/mega_icicle.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MegaIcicle']
    return (-24,-3,64,85)

def InitBolt(sprite): # 315
    global ImageCache
    if 'Bolt' not in ImageCache:
        ImageCache['Bolt'] = QtGui.QPixmap('reggiedata/sprites/bolt.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Bolt']
    return (2,0,28,16)

def InitBoltBox(sprite): # 316
    global ImageCache
    if 'BoltBox' not in ImageCache:
        ImageCache['BoltBoxTL'] = QtGui.QPixmap('reggiedata/sprites/boltbox_tl.png')
        ImageCache['BoltBoxT'] = QtGui.QPixmap('reggiedata/sprites/boltbox_t.png')
        ImageCache['BoltBoxTR'] = QtGui.QPixmap('reggiedata/sprites/boltbox_tr.png')
        ImageCache['BoltBoxL'] = QtGui.QPixmap('reggiedata/sprites/boltbox_l.png')
        ImageCache['BoltBoxM'] = QtGui.QPixmap('reggiedata/sprites/boltbox_m.png')
        ImageCache['BoltBoxR'] = QtGui.QPixmap('reggiedata/sprites/boltbox_r.png')
        ImageCache['BoltBoxBL'] = QtGui.QPixmap('reggiedata/sprites/boltbox_bl.png')
        ImageCache['BoltBoxB'] = QtGui.QPixmap('reggiedata/sprites/boltbox_b.png')
        ImageCache['BoltBoxBR'] = QtGui.QPixmap('reggiedata/sprites/boltbox_br.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBoltBox
    sprite.customPaint = True
    sprite.customPainter = PaintBoltBox
    return (0,0,16,16)

def InitBoxGenerator(sprite): #318
    if 'BoxGenerator' not in ImageCache:
        ImageCache['BoxGenerator'] = QtGui.QPixmap('reggiedata/sprites/box_generator.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BoxGenerator']
    return (0,-64,64,64)

def InitArrowBlock(sprite): # 321
    global ImageCache
    if 'ArrowBlock0' not in ImageCache:
        ImageCache['ArrowBlock0'] = QtGui.QPixmap('reggiedata/sprites/arrow_block_up.png')
        ImageCache['ArrowBlock1'] = QtGui.QPixmap('reggiedata/sprites/arrow_block_down.png')
        ImageCache['ArrowBlock2'] = QtGui.QPixmap('reggiedata/sprites/arrow_block_left.png')
        ImageCache['ArrowBlock3'] = QtGui.QPixmap('reggiedata/sprites/arrow_block_right.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeArrowBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,32,32)

def InitGhostHouseStand(sprite): # 325
    global ImageCache
    if 'GhostHouseStand' not in ImageCache:
        ImageCache['GhostHouseStand'] = QtGui.QPixmap('reggiedata/sprites/ghost_house_stand.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GhostHouseStand']
    return (0,-16,16,32)

def InitRopeLadder(sprite): # 330
    global ImageCache
    if 'RopeLadder0' not in ImageCache:
        LoadEnvStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeRopeLadder
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-3,-2,22,16)

def InitPlayerBlockPlatform(sprite): #333
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PlayerBlockPlatform']
    return (0,0,64,16)

def InitCheepGiant(sprite): # 334
    global ImageCache
    if 'CheepGiantL' not in ImageCache:
        cheep = QtGui.QImage('reggiedata/sprites/cheep_giant.png')
        ImageCache['CheepGiantL'] = QtGui.QPixmap.fromImage(cheep)
        ImageCache['CheepGiantR'] = QtGui.QPixmap.fromImage(cheep.mirrored(True, False))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeCheepGiant
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-6,-7,28,25)

def InitPipe(sprite): # 339, 353, 377, 378, 379, 380, 450
    global ImageCache
    if 'PipeTop0' not in ImageCache:
        i = 0
        for colour in ['green', 'red', 'yellow', 'blue']:
            ImageCache['PipeTop%d' % i] = QtGui.QPixmap('reggiedata/sprites/pipe_%s_top.png' % colour)
            ImageCache['PipeMiddle%d' % i] = QtGui.QPixmap('reggiedata/sprites/pipe_%s_middle.png' % colour)
            ImageCache['PipeBottom%d' % i] = QtGui.QPixmap('reggiedata/sprites/pipe_%s_bottom.png' % colour)
            ImageCache['PipeLeft%d' % i] = QtGui.QPixmap('reggiedata/sprites/pipe_%s_left.png' % colour)
            ImageCache['PipeCenter%d' % i] = QtGui.QPixmap('reggiedata/sprites/pipe_%s_center.png' % colour)
            ImageCache['PipeRight%d' % i] = QtGui.QPixmap('reggiedata/sprites/pipe_%s_right.png' % colour)
            i += 1

    sprite.dynamicSize = True
    sprite.dynSizer = SizePipe
    sprite.customPaint = True
    sprite.customPainter = PaintPipe
    sprite.setZValue(24999)
    return (0,0,16,16)

def InitBigShell(sprite): # 341
    global ImageCache
    if 'BigShell' not in ImageCache:
        ImageCache['BigShell'] = QtGui.QPixmap('reggiedata/sprites/bigshell.png')
        ImageCache['BigShellGrass'] = QtGui.QPixmap('reggiedata/sprites/bigshell_grass.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBigShell
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-97,-145,215,168)

def InitMuncher(sprite): # 342
    sprite.dynamicSize = True
    sprite.dynSizer = SizeMuncher
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitFuzzy(sprite): # 343
    global ImageCache
    if 'Fuzzy' not in ImageCache:
        ImageCache['Fuzzy'] = QtGui.QPixmap('reggiedata/sprites/fuzzy.png')
        ImageCache['FuzzyGiant'] = QtGui.QPixmap('reggiedata/sprites/fuzzy_giant.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFuzzy
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitChainHolder(sprite): # 345
    global ImageCache
    if 'ChainHolder' not in ImageCache:
        ImageCache['ChainHolder'] = QtGui.QPixmap('reggiedata/sprites/chain_holder.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ChainHolder']
    return (0,0,16,22)

def InitRockyWrench(sprite): # 352
    global ImageCache
    if 'RockyWrench' not in ImageCache:
        ImageCache['RockyWrench'] = QtGui.QPixmap('reggiedata/sprites/rocky_wrench.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RockyWrench']
    return (4,-41,24,26)

def InitRollingHillWithPipe(sprite): # 355, 360
    sprite.aux = AuxiliaryCircleOutline(sprite, 32*16)
    return (0,0,16,16)

def InitBrownBlock(sprite):
    global ImageCache
    if 'BrownBlockTL' not in ImageCache:
        ImageCache['BrownBlockTL'] = QtGui.QPixmap('reggiedata/sprites/brown_block_TL.png')
        ImageCache['BrownBlockTM'] = QtGui.QPixmap('reggiedata/sprites/brown_block_TM.png')
        ImageCache['BrownBlockTR'] = QtGui.QPixmap('reggiedata/sprites/brown_block_TR.png')
        ImageCache['BrownBlockML'] = QtGui.QPixmap('reggiedata/sprites/brown_block_ML.png')
        ImageCache['BrownBlockMM'] = QtGui.QPixmap('reggiedata/sprites/brown_block_MM.png')
        ImageCache['BrownBlockMR'] = QtGui.QPixmap('reggiedata/sprites/brown_block_MR.png')
        ImageCache['BrownBlockBL'] = QtGui.QPixmap('reggiedata/sprites/brown_block_BL.png')
        ImageCache['BrownBlockBM'] = QtGui.QPixmap('reggiedata/sprites/brown_block_BM.png')
        ImageCache['BrownBlockBR'] = QtGui.QPixmap('reggiedata/sprites/brown_block_BR.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBrownBlock
    sprite.customPaint = True
    sprite.customPainter = PaintBrownBlock
    if(sprite.type == 354): return (0,0,16,16)
    sprite.aux = AuxiliaryTrackObject(sprite, 16, 16, AuxiliaryTrackObject.Horizontal)
    return (0,0,16,16)




def InitFruit(sprite): # 357
    sprite.dynamicSize = True
    sprite.dynSizer = SizeFruit
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitWallLantern(sprite): # 359
    global ImageCache
    if 'WallLantern' not in ImageCache:
        ImageCache['WallLantern'] = QtGui.QPixmap('reggiedata/sprites/wall_lantern.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['WallLantern']
    return (0,8,16,16)

def InitColouredBox(sprite): # 362
    global ImageCache
    if 'CBox0TL' not in ImageCache:
        for colour in [0,1,2,3]:
            for direction in ['TL','T','TR','L','M','R','BL','B','BR']:
                ImageCache['CBox%d%s' % (colour,direction)] = QtGui.QPixmap('reggiedata/sprites/cbox_%s_%d.png' % (direction,colour))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeColouredBox
    sprite.customPaint = True
    sprite.customPainter = PaintColouredBox
    return (0,0,16,16)

def InitCubeKinokoRot(sprite): # 366
    global ImageCache
    if 'CubeKinokoG' not in ImageCache:
        ImageCache['CubeKinokoG'] = QtGui.QPixmap('reggiedata/sprites/cube_kinoko_g.png')
        ImageCache['CubeKinokoR'] = QtGui.QPixmap('reggiedata/sprites/cube_kinoko_r.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeCubeKinokoRot
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitCubeKinokoLine(sprite): # 367
    global ImageCache
    if 'CubeKinokoP' not in ImageCache:
        ImageCache['CubeKinokoP'] = QtGui.QPixmap('reggiedata/sprites/cube_kinoko_p.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CubeKinokoP']
    return (0,0,128,128)

def InitSlidingPenguin(sprite): # 369
    global ImageCache
    if 'PenguinL' not in ImageCache:
        penguin = QtGui.QImage('reggiedata/sprites/sliding_penguin.png')
        ImageCache['PenguinL'] = QtGui.QPixmap.fromImage(penguin)
        ImageCache['PenguinR'] = QtGui.QPixmap.fromImage(penguin.mirrored(True, False))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSlidingPenguin
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-2,-4,36,20)

def InitCloudBlock(sprite): # 370
    global ImageCache
    if 'CloudBlock' not in ImageCache:
        ImageCache['CloudBlock'] = QtGui.QPixmap('reggiedata/sprites/cloud_block.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CloudBlock']
    return (-4,-8,24,24)

def InitIceBlock(sprite): # 385
    global ImageCache
    if 'IceBlock00' not in ImageCache:
        for i in range(4):
            for j in range(4):
                ImageCache['IceBlock%d%d' % (i,j)] = QtGui.QPixmap('reggiedata/sprites/iceblock%d%d.png' % (i,j))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeIceBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitPowBlock(sprite): # 386
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['POW']
    return (0,0,16,16)

def InitBush(sprite): # 387
    sprite.setZValue(24999)
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBush
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitBarrel(sprite): # 388
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Barrel']
    return (-4,-8,24,24)

def InitGlowBlock(sprite): # 391
    sprite.aux = AuxiliaryImage(sprite, 48, 48)
    sprite.aux.image = ImageCache['GlowBlock']
    sprite.aux.setPos(-12, -12)

    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (0,0,16,16)

def InitPropellerBlock(sprite): # 393
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PropellerBlock']
    return (-1,-6,18,22)

def InitLemmyBall(sprite): # 394
    global ImageCache
    if 'LemmyBall' not in ImageCache:
        ImageCache['LemmyBall'] = QtGui.QPixmap('reggiedata/sprites/lemmyball.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['LemmyBall']
    return (-6,0,29,29)

def InitSpinyCheep(sprite): # 395
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpinyCheep']
    return (-1,-2,19,19)

def InitBlock(sprite): # 207, 208, 209, 221, 255, 256, 402, 403, 422, 423
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBlock
    sprite.customPaint = True
    sprite.customPainter = PaintBlock
    return (0,0,16,16)

def InitWendyRing(sprite): # 413
    global ImageCache
    if 'WendyRing' not in ImageCache:
        ImageCache['WendyRing'] = QtGui.QPixmap('reggiedata/sprites/wendy_ring.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['WendyRing']
    return (-4,4,24,24)

def InitGabon(sprite): # 414
    global ImageCache
    if 'GabonLeft' not in ImageCache:
        ImageCache['GabonLeft'] = QtGui.QPixmap('reggiedata/sprites/gabon_l.png')
        ImageCache['GabonRight'] = QtGui.QPixmap('reggiedata/sprites/gabon_r.png')
        ImageCache['GabonDown'] = QtGui.QPixmap('reggiedata/sprites/gabon_d.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeGabon
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitInvisibleOneUp(sprite): #416
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['InvisibleOneUp']
    return (3,5,12,11)

def InitSpinjumpCoin(sprite): # 417
    global ImageCache
    if 'SpinjumpCoin' not in ImageCache:
        ImageCache['SpinjumpCoin'] = QtGui.QPixmap('reggiedata/sprites/spinjump_coin.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpinjumpCoin']
    return (0,0,16,16)

def InitPalmTree(sprite): # 424
    global ImageCache
    if 'PalmTree0' not in ImageCache:
        for i in range(8):
            ImageCache['PalmTree%d' % i] = QtGui.QPixmap('reggiedata/sprites/palmtree_%d.png' % i)

    sprite.dynamicSize = True
    sprite.dynSizer = SizePalmTree
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-24.5,0,67,16)

def InitJellybeam(sprite): # 425
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Jellybeam']
    return (-6,0,28,28)

def InitToad(sprite): # 432
    global ImageCache
    if 'Toad' not in ImageCache:
        ImageCache['Toad'] = QtGui.QPixmap('reggiedata/sprites/toad.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Toad']
    return (-1,-16,19,32)

def InitWarpCannon(sprite): # 434
    global ImageCache
    if 'Warp0' not in ImageCache:
        ImageCache['Warp0'] = QtGui.QPixmap('reggiedata/sprites/warp_w5.png')
        ImageCache['Warp1'] = QtGui.QPixmap('reggiedata/sprites/warp_w6.png')
        ImageCache['Warp2'] = QtGui.QPixmap('reggiedata/sprites/warp_w8.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeWarpCannon
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (5,-25,87,106)

def InitPurplePole(sprite): # 437
    global ImageCache
    if 'VertPole' not in ImageCache:
        ImageCache['VertPoleTop'] = QtGui.QPixmap('reggiedata/sprites/purple_pole_top.png')
        ImageCache['VertPole'] = QtGui.QPixmap('reggiedata/sprites/purple_pole_middle.png')
        ImageCache['VertPoleBottom'] = QtGui.QPixmap('reggiedata/sprites/purple_pole_bottom.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizePurplePole
    sprite.customPaint = True
    sprite.customPainter = PaintPurplePole

    return (0,0,16,16)

def InitCagePeachFake(sprite): # 439
    global ImageCache
    if 'CagePeachFake' not in ImageCache:
        ImageCache['CagePeachFake'] = QtGui.QPixmap('reggiedata/sprites/cage_peach_fake.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CagePeachFake']
    return (-18,-106,52,122)

def InitHorizontalRope(sprite): # 440
    global ImageCache
    if 'HorzRope' not in ImageCache:
        ImageCache['HorzRope'] = QtGui.QPixmap('reggiedata/sprites/horizontal_rope_middle.png')
        ImageCache['HorzRopeEnd'] = QtGui.QPixmap('reggiedata/sprites/horizontal_rope_end.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeHorizontalRope
    sprite.customPaint = True
    sprite.customPainter = PaintHorizontalRope

    return (0,0,16,16)

def InitMushroomPlatform(sprite): # 441
    if 'RedShroomL' not in ImageCache:
        LoadMushrooms()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeMushroomPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintMushroomPlatform

    return (0,0,32,32)

def InitReplayBlock(sprite): # 443
    global ImageCache
    if 'ReplayBlock' not in ImageCache:
        ImageCache['ReplayBlock'] = QtGui.QPixmap('reggiedata/sprites/replay_block.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ReplayBlock']
    return (-8,-16,32,32)

def InitSwingingVine(sprite): # 444, 464
    global ImageCache
    if 'SwingVine' not in ImageCache:
        ImageCache['SwingVine'] = QtGui.QPixmap('reggiedata/sprites/swing_vine.png')
        ImageCache['SwingChain'] = QtGui.QPixmap('reggiedata/sprites/swing_chain.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSwingVine
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    return (0,0,16,144)

def InitCagePeachReal(sprite): # 445
    global ImageCache
    if 'CagePeachReal' not in ImageCache:
        ImageCache['CagePeachReal'] = QtGui.QPixmap('reggiedata/sprites/cage_peach_real.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CagePeachReal']
    return (-18,-106,52,122)

def InitMetalBar(sprite): # 448
    global ImageCache
    if 'MetalBar' not in ImageCache:
        ImageCache['MetalBar'] = QtGui.QPixmap('reggiedata/sprites/metal_bar.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MetalBar']
    return (0,-32,32,80)

def InitBowserBossDoor(sprite): # 452
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BowserDoor']
    return (-53,-134,156,183)

def InitSeaweed(sprite): # 453
    global ImageCache
    if 'Seaweed0' not in ImageCache:
        for i in range(4):
            ImageCache['Seaweed%d' % i] = QtGui.QPixmap('reggiedata/sprites/seaweed_%d.png' % i)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSeaweed
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitHammerPlatform(sprite): # 455
    global ImageCache
    if 'HammerPlatform' not in ImageCache:
        ImageCache['HammerPlatform'] = QtGui.QPixmap('reggiedata/sprites/hammer_platform.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['HammerPlatform']
    sprite.setZValue(24999)
    return (-24,-8,65,179)

def InitBossBridge(sprite): # 456
    global ImageCache
    if 'BossBridgeL' not in ImageCache:
        ImageCache['BossBridgeL'] = QtGui.QPixmap('reggiedata/sprites/boss_bridge_left.png')
        ImageCache['BossBridgeM'] = QtGui.QPixmap('reggiedata/sprites/boss_bridge_middle.png')
        ImageCache['BossBridgeR'] = QtGui.QPixmap('reggiedata/sprites/boss_bridge_right.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBossBridge
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,32,40)

def InitSpinningThinBars(sprite): # 457
    global ImageCache
    if 'SpinningThinBars' not in ImageCache:
        ImageCache['SpinningThinBars'] = QtGui.QPixmap('reggiedata/sprites/spinning_thin_bars.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpinningThinBars']
    sprite.setZValue(24999)
    return (-114,-112,244,240)

def InitLavaIronBlock(sprite): # 466
    global ImageCache
    if 'LavaIronBlock' not in ImageCache:
        ImageCache['LavaIronBlock'] = QtGui.QPixmap('reggiedata/sprites/lava_iron_block.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['LavaIronBlock']
    return (-2,-1,145,49)

def InitMovingGemBlock(sprite): # 467
    global ImageCache
    if 'MovingGemBlock' not in ImageCache:
        ImageCache['MovingGemBlock'] = QtGui.QPixmap('reggiedata/sprites/moving_gem_block.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MovingGemBlock']
    return (0,0,48,32)

def InitBoltPlatform(sprite): # 469
    global ImageCache
    if 'BoltPlatformL' not in ImageCache:
        ImageCache['BoltPlatformL'] = QtGui.QPixmap('reggiedata/sprites/bolt_platform_left.png')
        ImageCache['BoltPlatformM'] = QtGui.QPixmap('reggiedata/sprites/bolt_platform_middle.png')
        ImageCache['BoltPlatformR'] = QtGui.QPixmap('reggiedata/sprites/bolt_platform_right.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBoltPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintBoltPlatform

    return (0,-2.5,16,18)

def InitBoltPlatformWire(sprite): # 470
    global ImageCache
    if 'BoltPlatformWire' not in ImageCache:
        ImageCache['BoltPlatformWire'] = QtGui.QPixmap('reggiedata/sprites/bolt_platform_wire.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BoltPlatformWire']
    return (5,-240,6,256)

def InitLiftDokan(sprite): # 471
    global ImageCache
    if 'LiftDokanT' not in ImageCache:
        ImageCache['LiftDokanT'] = QtGui.QPixmap('reggiedata/sprites/lift_dokan_top.png')
        ImageCache['LiftDokanM'] = QtGui.QPixmap('reggiedata/sprites/lift_dokan_middle.png')

    sprite.customPaint = True
    sprite.customPainter = PaintLiftDokan

    return (-12,-2,51,386)


def InitFlyingWrench(sprite): # 476
    if 'Wrench' not in ImageCache:
        LoadAirshipStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Wrench']
    return (0,0,16,16)

def InitSuperGuideBlock(sprite): # 477
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SuperGuide']
    return (-4,-4,24,24)

Initialisers = {
    20: InitGoomba,
    21: InitParagoomba,
    23: InitHorzMovingPlatform,
    24: InitBuzzyBeetle,
    25: InitSpiny,
    26: InitUpsideDownSpiny,
    27: InitUnusedVertStoneBlock,
    28: InitUnusedHorzStoneBlock,
    30: InitOldStoneBlock,
    31: InitVertMovingPlatform,
    32: InitStarCoin,
    40: InitQuestionSwitch,
    41: InitPSwitch,
    42: InitExcSwitch,
    43: InitQuestionSwitchBlock,
    44: InitPSwitchBlock,
    45: InitExcSwitchBlock,
    46: InitPodoboo,
    47: InitThwomp,
    48: InitGiantThwomp,
    #49: InitUnused49,
    50: InitFallingPlatform,
    51: InitTiltingGirder,
    54: InitLakitu,
    57: InitKoopaTroopa,
    58: InitKoopaParatroopa,
    60: InitSpikeTop,
    61: InitBigBoo,
    63: InitSpikeBall,
    65: InitPipePiranhaUp,
    66: InitPipePiranhaDown,
    67: InitPipePiranhaRight,
    68: InitPipePiranhaLeft,
    69: InitPipeFiretrapUp,
    70: InitPipeFiretrapDown,
    71: InitPipeFiretrapRight,
    72: InitPipeFiretrapLeft,
    73: InitGroundPiranha,
    74: InitBigGroundPiranha,
    75: InitGroundFiretrap,
    76: InitBigGroundFiretrap,
    77: InitShipKey,
    78: InitCloudTrampoline,
    80: InitFireBro,
    81: InitOldStoneBlock,
    82: InitOldStoneBlock,
    83: InitOldStoneBlock,
    84: InitOldStoneBlock,
    85: InitOldStoneBlock,
    86: InitOldStoneBlock,
    92: InitBulletBillLauncher,
    93: InitBanzaiBillLauncher,
    94: InitBoomerangBro,
    95: InitHammerBro,
    96: InitRotationControllerSwaying,
    98: InitGiantSpikeBall,
    100: InitSwooper,
    101: InitBobomb,
    102: InitBroozer,
    103: InitPlatformGenerator,
    104: InitAmp,
    105: InitPokey,
    106: InitLinePlatform,
    108: InitAmp,
    109: InitChainBall,
    111: InitBlooper,
    112: InitBlooperBabies,
    113: InitFlagpole,
    115: InitCheep,
    118: InitDryBones,
    119: InitGiantDryBones,
    120: InitSledgeBro,
    122: InitOneWayPlatform,
    125: InitFenceKoopaHorz,
    126: InitFenceKoopaVert,
    127: InitFlipFence,
    128: InitFlipFenceLong,
    129: Init4Spinner,
    130: InitWiggler,
    131: InitBoo,
    133: InitStalagmitePlatform,
    134: InitCrow,
    135: InitHangingPlatform,
    #137: InitSpikedStake,
    #140: InitSpikedStake,
    #141: InitSpikedStake,
    #142: InitSpikedStake,
    143: InitArrow,
    144: InitRedCoin,
    146: InitChainChomp,
    147: InitCoin,
    148: InitSpring,
    149: InitRotationControllerSpinning,
    151: InitPuffer,
    155: InitStarCoin,
    156: InitRedCoinRing,
    158: InitFireSnake,
    172: InitScrewMushroom,
    173: InitGiantFloatingLog,
    175: InitFlyingQBlock,
    176: InitRouletteBlock,
    178: InitScalePlatform,
    180: InitCheepChomp,
    182: InitDoor,
    185: InitToadBalloon,
    187: InitPlayerBlock,
    188: InitMidwayPoint,
    193: InitUrchin,
    194: InitMegaUrchin,
    195: InitHuckit,
    196: InitFishbones,
    197: InitClam,
    198: InitGiantgoomba,
    199: InitMegagoomba,
    200: InitMicrogoomba,
    201: InitIcicle,
    202: InitMGCannon,
    203: InitMGChest,
    207: InitBlock,
    208: InitBlock,
    209: InitBlock,
    212: InitRollingHill,
    221: InitBlock,
    223: InitSpringBlock,
    224: InitJumboRay,
    227: InitPipeCannon,
    228: InitExtendShroom,
    230: InitBramball,
    231: InitWiggleShroom,
    232: InitMechaKoopa,
    233: InitBulber,
    237: InitPCoin,
    238: InitFoo,
    242: InitFallingLedgeBar,
    253: InitSpecialCoin,
    255: InitBlock,
    256: InitBlock,
    259: InitDoor,
    262: InitPoltergeistItem,
    263: InitWaterPiranha,
    264: InitWalkingPiranha,
    265: InitFallingIcicle,
    266: InitRotatingChainLink,
    267: InitTiltGrate,
    269: InitParabomb,
    271: InitLittleMouser,
    272: InitIceBro,
    274: InitCastleGear,
    276: InitDoor,
    277: InitDoor,
    278: InitDoor,
    280: InitGiantIceBlock,
    286: InitWoodCircle,
    288: InitOldBarrel,
    289: InitBox,
    291: InitParabeetle,
    292: InitHeavyParabeetle,
    294: InitIceCube,
    296: InitMegaBuzzy,
    300: InitRotCannon,
    301: InitRotCannonPipe,
    303: InitMontyMole,
    308: InitHammerBro,
    310: InitArrowSign,
    311: InitMegaIcicle,
    315: InitBolt,
    316: InitBoltBox,
    318: InitBoxGenerator,
    321: InitArrowBlock,
    325: InitGhostHouseStand,
    330: InitRopeLadder,
    333: InitPlayerBlockPlatform,
    334: InitCheepGiant,
    339: InitPipe,
    341: InitBigShell,
    342: InitMuncher,
    343: InitFuzzy,
    345: InitChainHolder,
    352: InitRockyWrench,
    353: InitPipe,
    354: InitBrownBlock,
    355: InitRollingHillWithPipe,
    356: InitBrownBlock,
    357: InitFruit,
    359: InitWallLantern,
    360: InitRollingHillWithPipe,
    362: InitColouredBox,
    366: InitCubeKinokoRot,
    367: InitCubeKinokoLine,
    369: InitSlidingPenguin,
    370: InitCloudBlock,
    371: InitSpecialCoin,
    377: InitPipe,
    378: InitPipe,
    379: InitPipe,
    380: InitPipe,
    382: InitScrewMushroom,
    385: InitIceBlock,
    386: InitPowBlock,
    387: InitBush,
    388: InitBarrel,
    389: InitStarCoin,
    390: InitSpecialCoin,
    391: InitGlowBlock,
    393: InitPropellerBlock,
    394: InitLemmyBall,
    395: InitSpinyCheep,
    402: InitBlock,
    403: InitBlock,
    413: InitWendyRing,
    414: InitGabon,
    416: InitInvisibleOneUp,
    417: InitSpinjumpCoin,
    422: InitBlock,
    423: InitBlock,
    424: InitPalmTree,
    425: InitJellybeam,
    432: InitToad,
    434: InitWarpCannon,
    437: InitPurplePole,
    439: InitCagePeachFake,
    440: InitHorizontalRope,
    441: InitMushroomPlatform,
    443: InitReplayBlock,
    444: InitSwingingVine,
    445: InitCagePeachReal,
    448: InitMetalBar,
    450: InitPipe,
    452: InitDoor,
    453: InitSeaweed,
    455: InitHammerPlatform,
    456: InitBossBridge,
    457: InitSpinningThinBars,
    464: InitSwingingVine,
    466: InitLavaIronBlock,
    467: InitMovingGemBlock,
    469: InitBoltPlatform,
    470: InitBoltPlatformWire,
    471: InitLiftDokan,
    476: InitFlyingWrench,
    477: InitSuperGuideBlock,
}

# ---- Dynamic Sizing ----
def SizeHorzMovingPlatform(sprite): # 23
    # get width and distance
    sprite.xsize = ((ord(sprite.spritedata[5]) & 0xF) + 1) << 4
    if sprite.xsize == 16: sprite.xsize = 32

    distance = (ord(sprite.spritedata[4]) & 0xF) << 4

    # update the track
    sprite.aux.SetSize(sprite.xsize + distance, 16)

    if (ord(sprite.spritedata[3]) & 1) == 0:
        # platform goes right
        sprite.aux.setPos(0, 0)
    else:
        # platform goes left
        sprite.aux.setPos(-distance*1.5, 0)

    # set colour
    sprite.colour = (ord(sprite.spritedata[3]) >> 4) & 1

    sprite.aux.update()

def SizeBuzzyBeetle(sprite): # 24
    upsidedown = ord(sprite.spritedata[5]) & 1

    if upsidedown == 0:
        sprite.image = ImageCache['BuzzyBeetle']
    else:
        sprite.image = ImageCache['BuzzyBeetleU']

def SizeUnusedVertStoneBlock(sprite): # 27
    # get height and distance
    width = ord(sprite.spritedata[5]) & 7
    if width == 0: width = 1
    byte5 = ord(sprite.spritedata[4])
    sprite.xsize = (16 + (width << 4))
    sprite.ysize = (16 << ((byte5 & 0x30) >> 4)) - 4
    distance = (byte5 & 0xF) << 4

    # update the track
    sprite.aux.SetSize(sprite.xsize, distance + sprite.ysize)

    if (ord(sprite.spritedata[3]) & 1) == 0:
        # block goes up
        sprite.aux.setPos(0, -distance*1.5)
    else:
        # block goes down
        sprite.aux.setPos(0, 0)

    sprite.aux.update()

def SizeUnusedHorzStoneBlock(sprite): # 28
    # get height and distance
    width = ord(sprite.spritedata[5]) & 7
    if width == 0: width = 1
    byte5 = ord(sprite.spritedata[4])
    sprite.xsize = (16 + (width << 4))
    sprite.ysize = (16 << ((byte5 & 0x30) >> 4)) - 5
    distance = (byte5 & 0xF) << 4

    # update the track
    sprite.aux.SetSize(distance + sprite.xsize, sprite.ysize)

    if (ord(sprite.spritedata[3]) & 1) == 0:
        # block goes right
        sprite.aux.setPos(0, 0)
    else:
        # block goes left
        sprite.aux.setPos(-distance*1.5, 0)

    sprite.aux.update()

def SizeVertMovingPlatform(sprite): # 31
    # get width and distance
    sprite.xsize = ((ord(sprite.spritedata[5]) & 0xF) + 1) << 4
    if sprite.xsize == 16: sprite.xsize = 32

    distance = (ord(sprite.spritedata[4]) & 0xF) << 4

    # update the track
    sprite.aux.SetSize(sprite.xsize, distance + 16)

    if (ord(sprite.spritedata[3]) & 1) == 0:
        # platform goes up
        sprite.aux.setPos(0, -distance*1.5)
    else:
        # platform goes down
        sprite.aux.setPos(0, 0)

    # set colour
    sprite.colour = (ord(sprite.spritedata[3]) >> 4) & 1

    sprite.aux.update()

def SizeSwitch(sprite): # 40,41,42
    upsideDown = ord(sprite.spritedata[5]) & 1

    if upsideDown == 0:
        sprite.image = ImageCache[sprite.switchType + 'Switch']
    else:
        sprite.image = ImageCache[sprite.switchType + 'SwitchU']

def SizeGroundPiranha(sprite): # 73
    upsideDown = ord(sprite.spritedata[5]) & 1

    if upsideDown == 0:
        sprite.yoffset = 6
        sprite.image = ImageCache['GroundPiranha']
    elif upsideDown == 1:
        sprite.yoffset = 0
        sprite.image = ImageCache['GroundPiranhaU']


def SizeBigGroundPiranha(sprite): # 74
    upsideDown = ord(sprite.spritedata[5]) & 1

    if upsideDown == 0:
        sprite.yoffset = -32
        sprite.image = ImageCache['BigGroundPiranha']
    elif upsideDown == 1:
        sprite.yoffset = 0
        sprite.image = ImageCache['BigGroundPiranhaU']


def SizeGroundFiretrap(sprite): # 75
    upsideDown = ord(sprite.spritedata[5]) & 1

    if upsideDown == 0:
        sprite.yoffset = -10
        sprite.image = ImageCache['GroundFiretrap']
    elif upsideDown == 1:
        sprite.yoffset = 0
        sprite.image = ImageCache['GroundFiretrapU']


def SizeBigGroundFiretrap(sprite): # 76
    upsideDown = ord(sprite.spritedata[5]) & 1

    if upsideDown == 0:
        sprite.yoffset = -68
        sprite.image = ImageCache['BigGroundFiretrap']
    elif upsideDown == 1:
        sprite.yoffset = 0
        sprite.image = ImageCache['BigGroundFiretrapU']


def SizeFallingPlatform(sprite): # 50
    # get width
    sprite.xsize = ((ord(sprite.spritedata[5]) & 0xF) + 1) << 4

    # override this for the "glitchy" effect caused by length=0
    if sprite.xsize == 16: sprite.xsize = 24

    # set colour
    colour = (ord(sprite.spritedata[3]) >> 4)
    if colour == 1:
        sprite.colour = 1
    elif colour == 3:
        sprite.colour = 2
    else:
        sprite.colour = 0

def SizeKoopaTroopa(sprite): # 57
    # get properties
    props = ord(sprite.spritedata[5])
    shell = (props >> 4) & 1
    colour = props & 1

    if shell == 0:
        sprite.xoffset = -7
        sprite.yoffset = -15
        sprite.xsize = 24
        sprite.ysize = 32
        sprite.setPos((sprite.objx+sprite.xoffset)*1.5,(sprite.objy+sprite.yoffset)*1.5)

        if colour == 0:
            sprite.image = ImageCache['KoopaG']
        else:
            sprite.image = ImageCache['KoopaR']
    else:
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 16
        sprite.ysize = 16
        sprite.setPos((sprite.objx+sprite.xoffset)*1.5,(sprite.objy+sprite.yoffset)*1.5)

        if colour == 0:
            sprite.image = ImageCache['KoopaShellG']
        else:
            sprite.image = ImageCache['KoopaShellR']

def SizeKoopaParatroopa(sprite): # 58
    # get properties
    colour = ord(sprite.spritedata[5]) & 1

    if colour == 0:
        sprite.image = ImageCache['ParakoopaG']
    else:
        sprite.image = ImageCache['ParakoopaR']

def SizeOldStoneBlock(sprite): # 30, 81, 82, 83, 84, 85, 86
    size = ord(sprite.spritedata[5])
    height = (size & 0xF0) >> 4
    width = size & 0xF
    if sprite.type == 30:
        height = 1 if height == 0 else height
        width = 1 if width == 0 else width
    sprite.xsize = width * 16 + 16
    sprite.ysize = height * 16 + 16

    type = sprite.type

    if type == 81 or type == 83: # left spikes
        sprite.xoffset = -16
        sprite.xsize += 16
    if type == 84 or type == 86: # top spikes
        sprite.yoffset = -16
        sprite.ysize += 16
    if type == 82 or type == 83: # right spikes
        sprite.xsize += 16
    if type == 85 or type == 86: # bottom spikes
        sprite.ysize += 16




    # now set up the track
    direction = ord(sprite.spritedata[2]) & 3
    distance = (ord(sprite.spritedata[4]) & 0xF0) >> 4

    if direction <= 1: # horizontal
        sprite.aux.direction = 1
        sprite.aux.SetSize(sprite.xsize + (distance * 16), sprite.ysize)
    else: # vertical
        sprite.aux.direction = 2
        sprite.aux.SetSize(sprite.xsize, sprite.ysize + (distance * 16))

    if direction == 0 or direction == 3: # right, down
        sprite.aux.setPos(0,0)
    elif direction == 1: # left
        sprite.aux.setPos(-distance * 24,0)
    elif direction == 2: # up
        sprite.aux.setPos(0,-distance * 24)

def SizeBulletBillLauncher(sprite): # 92
    height = (ord(sprite.spritedata[5]) & 0xF0) >> 4

    sprite.ysize = (height + 2) * 16
    sprite.yoffset = (height + 1) * -16

def SizeRotationControllerSwaying(sprite): # 96
    # get the swing arc: 4 == 90 degrees (45 left from the origin, 45 right)
    swingArc = ord(sprite.spritedata[2]) >> 4
    realSwingArc = swingArc * 11.25

    # angle starts at the right position (3 o'clock)
    # negative = clockwise, positive = anti clockwise
    startAngle = 90 - realSwingArc
    spanAngle = realSwingArc * 2

    sprite.aux.SetAngle(startAngle, spanAngle)
    sprite.aux.update()

def SizeSpikeTop(sprite): # 60
    value = ord(sprite.spritedata[5])
    vertical = (value & 0x20) >> 5
    horizontal = value & 1

    if vertical == 0: # up
        sprite.yoffset = -4
        v = 'U'
    else:
        sprite.yoffset = 0
        v = 'D'

    if horizontal == 0: # right
        sprite.image = ImageCache['SpikeTop%sR' % v]
    else:
        sprite.image = ImageCache['SpikeTop%sL' % v]


def SizeCloudTrampoline(sprite): # 78
    size = (ord(sprite.spritedata[4]) & 0x10) >> 4

    if size == 0:
        sprite.image = ImageCache['CloudTrSmall']
        sprite.xsize = 68
        sprite.ysize = 27
    else:
        sprite.image = ImageCache['CloudTrBig']
        sprite.xsize = 132
        sprite.ysize = 32

def SizePlatformGenerator(sprite): # 103
    # get width
    sprite.xsize = (((ord(sprite.spritedata[5]) & 0xF0) >> 4) + 1) << 4

    # length=0 becomes length=4
    if sprite.xsize == 16: sprite.xsize = 64

    # override this for the "glitchy" effect caused by length=0
    if sprite.xsize == 32: sprite.xsize = 24

    sprite.colour = 0

def SizePokey(sprite): # 105
    # get the height
    height = ord(sprite.spritedata[5]) & 0xF
    sprite.ysize = (height * 16) + 16 + 25
    sprite.yoffset = 0 - sprite.ysize + 16

def SizeLinePlatform(sprite): # 106
    # get width
    sprite.xsize = (ord(sprite.spritedata[5]) & 0xF) << 4

    # length=0 becomes length=4
    if sprite.xsize == 0: sprite.xsize = 64

    # override this for the "glitchy" effect caused by length=0
    if sprite.xsize == 16: sprite.xsize = 24

    colour = (ord(sprite.spritedata[4]) & 0xF0) >> 4
    if colour > 1: colour = 0
    sprite.colour = colour

def SizeChainBall(sprite): # 109
    direction = ord(sprite.spritedata[5]) & 3

    if direction % 2 == 0: # horizontal
        sprite.xsize = 96
        sprite.ysize = 38
    else: # vertical
        sprite.xsize = 37
        sprite.ysize = 96

    if direction == 0: # right
        sprite.xoffset = 3
        sprite.yoffset = -8.5
        sprite.image = ImageCache['ChainBallR']
    elif direction == 1: # up
        sprite.xoffset = -8.5
        sprite.yoffset = -81.5
        sprite.image = ImageCache['ChainBallU']
    elif direction == 2: # left
        sprite.xoffset = -83
        sprite.yoffset = -11
        sprite.image = ImageCache['ChainBallL']
    elif direction == 3: # down
        sprite.xoffset = -11
        sprite.yoffset = 3.5
        sprite.image = ImageCache['ChainBallD']


def SizeFlagpole(sprite): # 113
    # get the info
    exit = (ord(sprite.spritedata[2]) >> 4) & 1
    snow = ord(sprite.spritedata[5]) & 1

    if snow == 0:
        sprite.aux.setPos(356,97)
    else:
        sprite.aux.setPos(356,91)

    if exit == 0:
        sprite.image = ImageCache['Flagpole']
        if snow == 0:
            sprite.aux.image = ImageCache['Castle']
        else:
            sprite.aux.image = ImageCache['SnowCastle']
    else:
        sprite.image = ImageCache['FlagpoleSecret']
        if snow == 0:
            sprite.aux.image = ImageCache['CastleSecret']
        else:
            sprite.aux.image = ImageCache['SnowCastleSecret']

def SizeCheep(sprite): # 115
    type = ord(sprite.spritedata[5]) & 0xF
    if type == 1:
        sprite.image = ImageCache['CheepGreen']
    elif type == 8:
        sprite.image = ImageCache['CheepYellow']
    else:
        sprite.image = ImageCache['CheepRed']

def SizeOneWayPlatform(sprite): # 122
    width = ord(sprite.spritedata[5]) & 0xF
    if width < 2: width = 2
    sprite.xsize = width * 32 + 32

    sprite.xoffset = sprite.xsize * -0.5

    colour = (ord(sprite.spritedata[4]) & 0xF0) >> 4
    if colour > 1: colour = 0
    sprite.colour = colour

ArrowOffsets = [(3,0), (5,4), (1,3), (5,-1), (3,0), (-1,-1), (0,3), (-1,4)]
def SizeArrow(sprite): # 143
    direction = ord(sprite.spritedata[5]) & 7
    image = ImageCache['Arrow%d' % direction]
    sprite.image = image

    sprite.xsize = image.width() / 1.5
    sprite.ysize = image.height() / 1.5
    offset = ArrowOffsets[direction]
    sprite.xoffset, sprite.yoffset = offset

def SizeFireSnake(sprite): # 158
    move = ord(sprite.spritedata[5]) & 15

    if move == 1:
        sprite.xsize = 16
        sprite.ysize = 16
        sprite.yoffset = 0
        sprite.image = ImageCache['FireSnakeWait']
    else:
        sprite.xsize = 20
        sprite.ysize = 32
        sprite.yoffset = -16
        sprite.image = ImageCache['FireSnake']

def SizeScrewMushroom(sprite): # 172, 382
    # I wish I knew what this does
    SomeOffset = ord(sprite.spritedata[3])
    if SomeOffset == 0 or SomeOffset > 8: SomeOffset = 8

    sprite.xsize = 122
    sprite.ysize = 198
    sprite.xoffset = 3
    sprite.yoffset = SomeOffset * -16
    if sprite.type == 172: # with bolt
        sprite.ysize += 16
        sprite.yoffset -= 16

def SizeFlyingQBlock(sprite): #175
    color = ord(sprite.spritedata[4]) >> 4
    if color == 0:
        color = 'yellow'
    elif color == 1:
        color = 'blue'
    elif color == 2:
        color = 'gray'
    elif color == 3:
        color = 'red'
    sprite.image = ImageCache['FlyingQBlock%s' % color]

def SizeScalePlatform(sprite): # 178
    info1 = ord(sprite.spritedata[4])
    info2 = ord(sprite.spritedata[5])
    sprite.platformWidth = (info1 & 0xF0) >> 4
    if sprite.platformWidth > 12: sprite.platformWidth = -1

    sprite.ropeLengthLeft = info1 & 0xF
    sprite.ropeLengthRight = (info2 & 0xF0) >> 4
    sprite.ropeWidth = info2 & 0xF

    ropeWidth = sprite.ropeWidth * 16
    platformWidth = (sprite.platformWidth + 3) * 16
    sprite.xsize = ropeWidth + platformWidth

    maxRopeHeight = max(sprite.ropeLengthLeft, sprite.ropeLengthRight)
    sprite.ysize = maxRopeHeight * 16 + 19
    if maxRopeHeight == 0: sprite.ysize += 8

    sprite.xoffset = -((sprite.platformWidth + 3) * 16 / 2)

def SizeHuckit(sprite): # 195
    type = ord(sprite.spritedata[5]) & 15
    right = type == 1
    if right:
        imgDirection = 'Flipped'
        sprite.xoffset = 0
    else:
        imgDirection = ''
        sprite.xoffset = -14

    sprite.image = ImageCache['Huckit%s' % imgDirection]

def SizeClam(sprite): # 197
    upsidedown = ord(sprite.spritedata[4]) & 15
    contents = ord(sprite.spritedata[5]) & 15

    if upsidedown == 1 and contents == 4:
        sprite.image = ImageCache['ClamPSwitchU']
    else:
        sprite.image = ImageCache['Clam%d' % contents]

def SizeIcicle(sprite): # 201
    size = ord(sprite.spritedata[5]) & 1

    if size == 0:
        sprite.image = ImageCache['IcicleSmallS']
        sprite.ysize = 16
    else:
        sprite.image = ImageCache['IcicleLargeS']
        sprite.ysize = 32

def SizeBlock(sprite): # 207, 208, 209, 221, 255, 256, 402, 403, 422, 423
    # Sprite types:
    # 207 = Question Block
    # 208 = Question Block (unused)
    # 209 = Brick Block
    # 221 = Invisible Block
    # 255 = Rotating Question Block
    # 256 = Rotating Brick Block
    # 402 = Line Question Block
    # 403 = Line Brick Block
    # 422 = Toad Question Block
    # 423 = Toad Brick Block

    type = sprite.type
    contents = ord(sprite.spritedata[5]) & 0xF

    # SET TILE TYPE
    if type == 207 or type == 208 or type == 255 or type == 402 or type == 422:
        sprite.tilenum = 49
    elif type == 209 or type == 256 or type == 403 or type == 423:
        sprite.tilenum = 48
    else:
        sprite.tilenum = 1315

    # SET CONTENTS
    # In the blocks.png file:
    # 0 = Empty, 1 = Coin, 2 = Mushroom, 3 = Fire Flower, 4 = Propeller, 5 = Penguin Suit,
    # 6 = Mini Shroom, 7 = Star, 8 = Continuous Star, 9 = Yoshi Egg, 10 = 10 Coins,
    # 11 = 1-up, 12 = Vine, 13 = Spring, 14 = Shroom/Coin, 15 = Ice Flower, 16 = Toad

    if type == 422 or type == 423: # Force Toad
        contents = 16
    elif type == 255 or type == 256: # Contents is a different nybble here
        contents = ord(sprite.spritedata[4]) & 0xF

    if contents == 2: # 1 and 2 are always fire flowers
        contents = 3

    if contents == 12 and (type == 208 or type == 255 or type == 256 or type == 402):
        contents = 2 # 12 is a mushroom on some types

    sprite.image = ImageCache['Blocks'][contents]

    # SET UP ROTATION
    if type == 255 or type == 256:
        transform = QtGui.QTransform()
        transform.translate(12, 12)

        angle = (ord(sprite.spritedata[4]) & 0xF0) >> 4
        leftTilt = ord(sprite.spritedata[3]) & 1

        angle *= (45.0 / 16.0)

        if leftTilt == 0:
            transform.rotate(angle)
        else:
            transform.rotate(360.0 - angle)

        transform.translate(-12, -12)
        sprite.setTransform(transform)

def SizeRollingHill(sprite): # 212
    size = (ord(sprite.spritedata[3]) >> 4) & 0xF
    realSize = RollingHillSizes[size]

    sprite.aux.SetSize(realSize)
    sprite.aux.update()

def SizeSpringBlock(sprite): # 223
    type = ord(sprite.spritedata[5]) & 1
    if type == 0:
        sprite.image = ImageCache['SpringBlock1']
    else:
        sprite.image = ImageCache['SpringBlock2']

def SizeJumboRay(sprite): # 224
    flyleft = ord(sprite.spritedata[4]) & 15

    if flyleft == 1:
        sprite.image = ImageCache['JumboRayL']
    else:
        sprite.xoffset = -152
        sprite.yoffset = 0
        sprite.xsize = 171
        sprite.ysize = 79
        sprite.image = ImageCache['JumboRayR']

def SizePipeCannon(sprite): # 227
    fireDirection = ord(sprite.spritedata[5]) & 15

    if fireDirection == 1 or fireDirection == 3 or fireDirection == 6:
        imgDirection = 'Flipped'
    else:
        imgDirection = ''

    if fireDirection == 0 or fireDirection == 1:
        imgNumber = 0
    elif fireDirection == 2 or fireDirection == 3:
        imgNumber = 1
    elif fireDirection == 4:
        imgNumber = 2
    elif fireDirection == 5 or fireDirection == 6:
        imgNumber = 3

    if fireDirection == 0:
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 55
        sprite.ysize = 64
    elif fireDirection == 1:
        sprite.xoffset = -22
        sprite.yoffset = 0
        sprite.xsize = 55
        sprite.ysize = 64
    elif fireDirection == 2:
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 40
        sprite.ysize = 64
    elif fireDirection == 3:
        sprite.xoffset = -11
        sprite.yoffset = 0
        sprite.xsize = 40
        sprite.ysize = 64
    elif fireDirection == 4:
        sprite.xoffset = -4
        sprite.yoffset = -16
        sprite.xsize = 40
        sprite.ysize = 80
    elif fireDirection == 5:
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 59
        sprite.ysize = 64
    elif fireDirection == 6:
        sprite.xoffset = -28
        sprite.yoffset = 0
        sprite.xsize = 59
        sprite.ysize = 64

    sprite.image = ImageCache['PipeCannon%s%d' % (imgDirection, imgNumber)]


def SizeExtendShroom(sprite): # 228
    props = ord(sprite.spritedata[5])

    width = ord(sprite.spritedata[4]) & 1
    start = (props & 0x10) >> 4
    stemlength = props & 0xF

    if start == 0: # contracted
        sprite.image = ImageCache['ExtendShroomC']
        xsize = 32
    else:
        if width == 0: # big
            sprite.image = ImageCache['ExtendShroomB']
            xsize = 160
        else: # small
            sprite.image = ImageCache['ExtendShroomS']
            xsize = 96

    sprite.xoffset = 8 - (xsize / 2)
    sprite.xsize = xsize
    sprite.ysize = stemlength * 16 + 48

    sprite.setZValue(24999)

def SizeWiggleShroom(sprite): # 231
    width = (ord(sprite.spritedata[4]) & 0xF0) >> 4
    stemlength = ord(sprite.spritedata[3]) & 3

    sprite.xoffset = width * -8 - 20
    sprite.xsize = width * 16 + 56
    sprite.ysize = stemlength * 16 + 48 + 16

    sprite.setZValue(24999)

def SizeTiltGrate(sprite): # 256
    direction = ord(sprite.spritedata[5]) & 3

    if direction < 2:
        sprite.xsize = 69
        sprite.ysize = 166
    else:
        sprite.xsize = 166
        sprite.ysize = 69

    if direction == 0:
        sprite.xoffset = -36
        sprite.yoffset = -115
        sprite.image = ImageCache['TiltGrateU']
    elif direction == 1:
        sprite.xoffset = -36
        sprite.yoffset = 12
        sprite.image = ImageCache['TiltGrateD']
    elif direction == 2:
        sprite.xoffset = -144
        sprite.yoffset = 0
        sprite.image = ImageCache['TiltGrateL']
    elif direction == 3:
        sprite.xoffset = -20
        sprite.yoffset = 0
        sprite.image = ImageCache['TiltGrateR']


def SizeDoor(sprite): # 182, 259, 276, 277, 278, 452
    rotstatus = ord(sprite.spritedata[4])
    if rotstatus & 1 == 0:
        direction = 0
    else:
        direction = (rotstatus & 0x30) >> 4

    doorType = sprite.doorType
    doorSize = sprite.doorSize
    if direction == 0:
        sprite.image = ImageCache[doorType+'U']
        sprite.xoffset = doorSize[0]
        sprite.yoffset = doorSize[1]
        sprite.xsize = doorSize[2]
        sprite.ysize = doorSize[3]
    elif direction == 1:
        sprite.image = ImageCache[doorType+'L']
        sprite.xoffset = (doorSize[2] / 2) + doorSize[0] - doorSize[3]
        sprite.yoffset = doorSize[1] + (doorSize[3] - (doorSize[2] / 2))
        sprite.xsize = doorSize[3]
        sprite.ysize = doorSize[2]
    elif direction == 2:
        sprite.image = ImageCache[doorType+'D']
        sprite.xoffset = doorSize[0]
        sprite.yoffset = doorSize[1]+doorSize[3]
        sprite.xsize = doorSize[2]
        sprite.ysize = doorSize[3]
    elif direction == 3:
        sprite.image = ImageCache[doorType+'R']
        sprite.xoffset = doorSize[0] + (doorSize[2] / 2)
        sprite.yoffset = doorSize[1] + (doorSize[3] - (doorSize[2] / 2))
        sprite.xsize = doorSize[3]
        sprite.ysize = doorSize[2]

def SizePoltergeistItem(sprite): # 262
    style = ord(sprite.spritedata[5]) & 15

    if style == 0:
        sprite.image = ImageCache['PolterQBlock']
    else:
        sprite.xsize = 28
        sprite.ysize = 40
        sprite.yoffset = -23
        sprite.image = ImageCache['PolterStand']

def SizeFallingIcicle(sprite): # 265
    size = ord(sprite.spritedata[5]) & 1

    if size == 0:
        sprite.image = ImageCache['IcicleSmall']
        sprite.ysize = 19
    else:
        sprite.image = ImageCache['IcicleLarge']
        sprite.ysize = 36

def SizeLittleMouser(sprite): # 271
    mice = ord(sprite.spritedata[5]) >> 4
    one = mice == 0
    two = mice == 1
    three = mice == 2
    four = mice == 3
    direction = ord(sprite.spritedata[5]) & 15
    if direction == 0:
        imgDirection = ''
    else:
        imgDirection = 'Flipped'

    sprite.image = ImageCache['LittleMouser%s%d' % (imgDirection, mice)]
    if imgDirection == '':
        if one:
            sprite.xoffset = -6
            sprite.xsize = 30
        elif two:
            sprite.xoffset = -36
            sprite.xsize = 61
        elif three:
            sprite.xoffset = -70
            sprite.xsize = 95
        elif four:
            sprite.xoffset = -103
            sprite.xsize = 128
    else:
        if one:
            sprite.xsize = 30
        elif two:
            sprite.xsize = 61
        elif three:
            sprite.xsize = 95
        elif four:
            sprite.xsize = 128

def SizeCastleGear(sprite): #274
    isBig = (ord(sprite.spritedata[4]) & 0xF) == 1
    sprite.image = ImageCache['CastleGearL'] if isBig else ImageCache['CastleGearS']
    sprite.xoffset = -(((sprite.image.width()/2.0)-12)*(2.0/3.0))
    sprite.yoffset = -(((sprite.image.height()/2.0)-12)*(2.0/3.0))
    sprite.xsize = sprite.image.width()*(2.0/3.0)
    sprite.ysize = sprite.image.height()*(2.0/3.0)



def SizeGiantIceBlock(sprite): # 280
    item = ord(sprite.spritedata[5]) & 3
    if item == 3: item = 0

    if item == 0:
        sprite.image = ImageCache['BigIceBlockEmpty']
    elif item == 1:
        sprite.image = ImageCache['BigIceBlockBobomb']
    elif item == 2:
        sprite.image = ImageCache['BigIceBlockSpikeBall']

def SizeWoodCircle(sprite): # 286
    size = ord(sprite.spritedata[5]) & 3
    if size == 3: size = 0

    sprite.image = ImageCache['WoodCircle%d' % size]

    if size == 0:
        sprite.xoffset = -24
        sprite.yoffset = -24
        sprite.xsize = 64
        sprite.ysize = 64
    elif size == 1:
        sprite.xoffset = -40
        sprite.yoffset = -40
        sprite.xsize = 96
        sprite.ysize = 96
    elif size == 2:
        sprite.xoffset = -56
        sprite.yoffset = -56
        sprite.xsize = 128
        sprite.ysize = 128


BoxSizes = [('Small', 32, 32), ('Wide', 64, 32), ('Tall', 32, 64), ('Big', 64, 64)]
def SizeBox(sprite): # 289
    style = ord(sprite.spritedata[4]) & 1
    size = (ord(sprite.spritedata[5]) >> 4) & 3

    style = 'Wood' if style == 0 else 'Metal'
    size = BoxSizes[size]

    sprite.image = ImageCache['Box%s%s' % (style, size[0])]
    sprite.xsize = size[1]
    sprite.ysize = size[2]

def SizeParabeetle(sprite): # 291
    direction = ord(sprite.spritedata[5]) & 3
    sprite.image = ImageCache['Parabeetle%d' % direction]

    if direction == 0: # right
        sprite.xoffset = -12
        sprite.xsize = 39
    elif direction == 1: # left
        sprite.xoffset = -10
        sprite.xsize = 39
    elif direction == 2: # more right
        sprite.xoffset = -12
        sprite.xsize = 40
    elif direction == 3: # at you
        sprite.xoffset = -26
        sprite.xsize = 67


def SizeHeavyParabeetle(sprite): # 292
    direction = ord(sprite.spritedata[5]) & 3
    sprite.image = ImageCache['HeavyParabeetle%d' % direction]

    if direction == 0: # right
        sprite.xoffset = -38
        sprite.xsize = 93
    elif direction == 1: # left
        sprite.xoffset = -38
        sprite.xsize = 94
    elif direction == 2: # more right
        sprite.xoffset = -38
        sprite.xsize = 93
    elif direction == 3: # at you
        sprite.xoffset = -52
        sprite.xsize = 110


def SizeMegaBuzzy(sprite): # 296
    dir = ord(sprite.spritedata[5]) & 3

    if dir == 0 or dir == 3:
        sprite.image = ImageCache['MegaBuzzyR']
    elif dir == 1:
        sprite.image = ImageCache['MegaBuzzyL']
    elif dir == 2:
        sprite.image = ImageCache['MegaBuzzyF']

def SizeRotCannon(sprite): # 300
    direction = (ord(sprite.spritedata[5]) & 0x10) >> 4

    sprite.xsize = 40
    sprite.ysize = 45

    if direction == 0:
        sprite.xoffset = -12
        sprite.yoffset = -29
        sprite.image = ImageCache['RotCannon']
    elif direction == 1:
        sprite.xoffset = -12
        sprite.yoffset = 0
        sprite.image = ImageCache['RotCannonU']


def SizeRotCannonPipe(sprite): # 301
    direction = (ord(sprite.spritedata[5]) & 0x10) >> 4

    sprite.xsize = 80
    sprite.ysize = 90

    if direction == 0:
        sprite.xoffset = -40
        sprite.yoffset = -74
        sprite.image = ImageCache['RotCannonPipe']
    elif direction == 1:
        sprite.xoffset = -40
        sprite.yoffset = 0
        sprite.image = ImageCache['RotCannonPipeU']


def SizeMontyMole(sprite): # 303
    mode = ord(sprite.spritedata[5])
    if mode == 1:
        sprite.image = ImageCache['Mole']
    else:
        sprite.image = ImageCache['MoleCave']

def SizeArrowSign(sprite): # 310
    direction = ord(sprite.spritedata[5]) & 7
    sprite.image = ImageCache['ArrowSign%d' % direction]

def SizeBoltBox(sprite): # 316
    size = ord(sprite.spritedata[5])
    sprite.xsize = (size & 0xF) * 16 + 32
    sprite.ysize = ((size & 0xF0) >> 4) * 16 + 32

def SizeArrowBlock(sprite): # 321
    direction = ord(sprite.spritedata[5]) & 3
    sprite.image = ImageCache['ArrowBlock%d' % direction]

def SizeRopeLadder(sprite): # 330
    size = ord(sprite.spritedata[5])
    if size > 2: size = 0
    sprite.image = ImageCache['RopeLadder%d' % size]
    if size == 0:
        sprite.ysize = 74
    elif size == 1:
        sprite.ysize = 108
    elif size == 2:
        sprite.ysize = 140

def SizeCheepGiant(sprite): # 334
    mode = ord(sprite.spritedata[5]) & 0xF

    if mode != 3:
        sprite.image = ImageCache['CheepGiantL']
    else:
        sprite.image = ImageCache['CheepGiantR']

def SizePipe(sprite): # 339, 353, 377, 378, 379, 380, 450
    # Sprite types:
    # 339 = Moving Pipe Facing Up
    # 353 = Moving Pipe Facing Down
    # 377 = Pipe Up
    # 378 = Pipe Down
    # 379 = Pipe Right
    # 380 = Pipe Left
    # 450 = Enterable Pipe Up

    type = sprite.type
    props = ord(sprite.spritedata[5])

    if type > 353: # normal pipes
        sprite.moving = False
        sprite.colour = (props & 0x30) >> 4
        length = props & 0xF

        size = length * 16 + 32
        if type == 379 or type == 380: # horizontal
            sprite.xsize = size
            sprite.ysize = 32
            sprite.orientation = 'H'
            if type == 379:   # faces right
                sprite.direction = 'R'
                sprite.xoffset = 0
            else:             # faces left
                sprite.direction = 'L'
                sprite.xoffset = 16 - size
            sprite.yoffset = 0

        else: # vertical
            sprite.xsize = 32
            sprite.ysize = size
            sprite.orientation = 'V'
            if type == 378: # faces down
                sprite.direction = 'D'
                sprite.yoffset = 0
            else:                          # faces up
                sprite.direction = 'U'
                sprite.yoffset = 16 - size
            sprite.xoffset = 0

    else: # moving pipes
        sprite.moving = True

        sprite.colour = ord(sprite.spritedata[3])
        length1 = (props & 0xF0) >> 4
        length2 = (props & 0xF)
        size = max(length1, length2) * 16 + 32

        sprite.xsize = 32
        sprite.ysize = size
        sprite.orientation = 'V'

        if type == 339: # facing up
            sprite.direction = 'U'
            sprite.yoffset = 16 - size
        else:
            sprite.direction = 'D'
            sprite.yoffset = 0

        sprite.length1 = length1 * 16 + 32
        sprite.length2 = length2 * 16 + 32


def SizeBigShell(sprite): # 341
    style = ord(sprite.spritedata[5]) & 1
    if style == 0:
        sprite.image = ImageCache['BigShellGrass']
    else:
        sprite.image = ImageCache['BigShell']

def SizeMuncher(sprite): # 342
    frozen = ord(sprite.spritedata[5]) & 1
    if frozen == 0:
        sprite.image = ImageCache['Muncher']
    else:
        sprite.image = ImageCache['MuncherF']

def SizeFuzzy(sprite): # 343
    giant = ord(sprite.spritedata[4]) & 1

    if giant == 0:
        sprite.xoffset = -7
        sprite.yoffset = -7
        sprite.xsize = 30
        sprite.ysize = 30
        sprite.image = ImageCache['Fuzzy']
    else:
        sprite.xoffset = -18
        sprite.yoffset = -18
        sprite.xsize = 52
        sprite.ysize = 52
        sprite.image = ImageCache['FuzzyGiant']

def SizeBrownBlock(sprite): # 356
    size = ord(sprite.spritedata[5])
    height = (size & 0xF0) >> 4
    width = size & 0xF
    height = 1 if height == 0 else height
    width = 1 if width == 0 else width
    sprite.xsize = width * 16 + 16
    sprite.ysize = height * 16 + 16

    type = sprite.type
    # now set up the track
    if(type == 354): return
    direction = ord(sprite.spritedata[2]) & 3
    distance = (ord(sprite.spritedata[4]) & 0xF0) >> 4

    if direction <= 1: # horizontal
        sprite.aux.direction = 1
        sprite.aux.SetSize(sprite.xsize + (distance * 16), sprite.ysize)
    else: # vertical
        sprite.aux.direction = 2
        sprite.aux.SetSize(sprite.xsize, sprite.ysize + (distance * 16))

    if direction == 0 or direction == 3: # right, down
        sprite.aux.setPos(0,0)
    elif direction == 1: # left
        sprite.aux.setPos(-distance * 24,0)
    elif direction == 2: # up
        sprite.aux.setPos(0,-distance * 24)


def SizeFruit(sprite): # 357
    style = ord(sprite.spritedata[5]) & 1
    if style == 0:
        sprite.image = ImageCache['Fruit']
    else:
        sprite.image = ImageCache['Cookie']

def SizeColouredBox(sprite): # 362
    sprite.colour = (ord(sprite.spritedata[3]) >> 4) & 3

    size = ord(sprite.spritedata[4])
    width = size >> 4
    height = size & 0xF

    sprite.xsize = ((width + 3) * 16)
    sprite.ysize = ((height + 3) * 16)

def SizeCubeKinokoRot(sprite): # 366
    style = (ord(sprite.spritedata[4]) & 1)

    if style == 0:
        sprite.image = ImageCache['CubeKinokoR']
        sprite.xsize = 80
        sprite.ysize = 80
    else:
        sprite.image = ImageCache['CubeKinokoG']
        sprite.xsize = 240
        sprite.ysize = 240

def SizeSlidingPenguin(sprite): # 369
    direction = ord(sprite.spritedata[5]) & 1

    if direction == 0:
        sprite.image = ImageCache['PenguinL']
    else:
        sprite.image = ImageCache['PenguinR']

def SizeIceBlock(sprite): # 385
    size = ord(sprite.spritedata[5])
    height = (size & 0x30) >> 4
    width = size & 3

    sprite.image = ImageCache['IceBlock%d%d' % (width,height)]
    sprite.xoffset = width * -4
    sprite.yoffset = height * -8
    sprite.xsize = width * 8 + 16
    sprite.ysize = height * 8 + 16

def SizeBush(sprite): # 387
    props = ord(sprite.spritedata[5])
    style = (props >> 4) & 1
    size = props & 3

    sprite.image = ImageCache['Bush%d%d' % (style, size)]

    if size == 0:
        sprite.xoffset = -22
        sprite.yoffset = -25
        sprite.xsize = 45
        sprite.ysize = 30
    elif size == 1:
        sprite.xoffset = -29
        sprite.yoffset = -45
        sprite.xsize = 60
        sprite.ysize = 51
    elif size == 2:
        sprite.xoffset = -41
        sprite.yoffset = -61
        sprite.xsize = 83
        sprite.ysize = 69
    elif size == 3:
        sprite.xoffset = -52
        sprite.yoffset = -80
        sprite.xsize = 108
        sprite.ysize = 86


def SizeGabon(sprite): # 414
    throwdir = ord(sprite.spritedata[5]) & 1
    facing = ord(sprite.spritedata[4]) & 1

    if throwdir == 0: # down
        sprite.image = ImageCache['GabonDown']
        sprite.xoffset = -5
        sprite.yoffset = -29
        sprite.xsize = 26
        sprite.ysize = 47
    else: # left/right
        if facing == 0:
            sprite.image = ImageCache['GabonLeft']
            sprite.xoffset = -7
            sprite.yoffset = -31
        else:
            sprite.image = ImageCache['GabonRight']
            sprite.xoffset = -5
            sprite.yoffset = -30
        sprite.xsize = 29
        sprite.ysize = 49


def SizePalmTree(sprite): # 424
    size = ord(sprite.spritedata[5]) & 7
    image = ImageCache['PalmTree%d' % size]
    sprite.image = image
    sprite.ysize = image.height() / 1.5
    sprite.yoffset = 16 - (image.height() / 1.5)

def SizeWarpCannon(sprite): # 434
    dest = ord(sprite.spritedata[5]) & 3
    if dest == 3: dest = 0
    sprite.image = ImageCache['Warp%d' % dest]

def SizePurplePole(sprite): # 437
    length = ord(sprite.spritedata[5])
    sprite.ysize = (length+3) * 16

def SizeHorizontalRope(sprite): # 440
    length = ord(sprite.spritedata[5])
    sprite.xsize = (length+3) * 16

def SizeMushroomPlatform(sprite): # 441
    # get size/colour
    sprite.colour = ord(sprite.spritedata[4]) & 1
    sprite.shroomsize = (ord(sprite.spritedata[5]) >> 4) & 1
    sprite.ysize = 16 * (sprite.shroomsize+1)

    # get width
    width = ord(sprite.spritedata[5]) & 0xF
    if sprite.shroomsize == 0:
        sprite.xsize = (width << 4) + 32
        sprite.xoffset = 0 - (int((width + 1) / 2) << 4)
        sprite.yoffset = 0
    else:
        sprite.xsize = (width << 5) + 64
        sprite.xoffset = 16 - (sprite.xsize / 2)
        sprite.yoffset = -16


def SizeSwingVine(sprite): # 444, 464
    style = ord(sprite.spritedata[5]) & 1
    if sprite.type == 444: style = 0

    if style == 0:
        sprite.image = ImageCache['SwingVine']
    else:
        sprite.image = ImageCache['SwingChain']


SeaweedSizes = [0, 1, 2, 2, 3]
SeaweedXOffsets = [-26, -22, -31, -42]
def SizeSeaweed(sprite): # 453
    style = ord(sprite.spritedata[5]) & 0xF
    if style > 4: style = 4
    size = SeaweedSizes[style]

    image = ImageCache['Seaweed%d' % size]
    sprite.image = image
    sprite.xsize = image.width() / 1.5
    sprite.ysize = image.height() / 1.5
    sprite.xoffset = SeaweedXOffsets[size]
    sprite.yoffset = 17 - sprite.ysize
    sprite.setZValue(24998)

def SizeBossBridge(sprite): # 456
    style = ord(sprite.spritedata[5]) & 3
    if style == 0 or style == 3:
        sprite.image = ImageCache['BossBridgeM']
    elif style == 1:
        sprite.image = ImageCache['BossBridgeR']
    elif style == 2:
        sprite.image = ImageCache['BossBridgeL']

def SizeBoltPlatform(sprite): # 469
    length = ord(sprite.spritedata[5]) & 0xF
    sprite.xsize = (length+2) * 16

# ---- Resource Loaders ----
def LoadBasicSuite():
    global ImageCache
    ImageCache['Coin'] = QtGui.QPixmap('reggiedata/sprites/coin.png')
    ImageCache['SpecialCoin'] = QtGui.QPixmap('reggiedata/sprites/special_coin.png')
    ImageCache['PCoin'] = QtGui.QPixmap('reggiedata/sprites/p_coin.png')
    ImageCache['RedCoin'] = QtGui.QPixmap('reggiedata/sprites/redcoin.png')
    ImageCache['RedCoinRing'] = QtGui.QPixmap('reggiedata/sprites/redcoinring.png')
    ImageCache['Goomba'] = QtGui.QPixmap('reggiedata/sprites/goomba.png')
    ImageCache['Paragoomba'] = QtGui.QPixmap('reggiedata/sprites/paragoomba.png')
    ImageCache['Fishbones'] = QtGui.QPixmap('reggiedata/sprites/fishbones.png')
    ImageCache['SpinyCheep'] = QtGui.QPixmap('reggiedata/sprites/spiny_cheep.png')
    ImageCache['Jellybeam'] = QtGui.QPixmap('reggiedata/sprites/jellybeam.png')
    ImageCache['Bulber'] = QtGui.QPixmap('reggiedata/sprites/bulber.png')
    ImageCache['CheepChomp'] = QtGui.QPixmap('reggiedata/sprites/cheep_chomp.png')
    ImageCache['Urchin'] = QtGui.QPixmap('reggiedata/sprites/urchin.png')
    ImageCache['MegaUrchin'] = QtGui.QPixmap('reggiedata/sprites/mega_urchin.png')
    ImageCache['Puffer'] = QtGui.QPixmap('reggiedata/sprites/porcu_puffer.png')
    ImageCache['Microgoomba'] = QtGui.QPixmap('reggiedata/sprites/microgoomba.png')
    ImageCache['Giantgoomba'] = QtGui.QPixmap('reggiedata/sprites/giantgoomba.png')
    ImageCache['Megagoomba'] = QtGui.QPixmap('reggiedata/sprites/megagoomba.png')
    ImageCache['KoopaG'] = QtGui.QPixmap('reggiedata/sprites/koopa_green.png')
    ImageCache['KoopaR'] = QtGui.QPixmap('reggiedata/sprites/koopa_red.png')
    ImageCache['KoopaShellG'] = QtGui.QPixmap('reggiedata/sprites/koopa_green_shell.png')
    ImageCache['KoopaShellR'] = QtGui.QPixmap('reggiedata/sprites/koopa_red_shell.png')
    ImageCache['ParakoopaG'] = QtGui.QPixmap('reggiedata/sprites/parakoopa_green.png')
    ImageCache['ParakoopaR'] = QtGui.QPixmap('reggiedata/sprites/parakoopa_red.png')
    ImageCache['BuzzyBeetle'] = QtGui.QPixmap('reggiedata/sprites/buzzy_beetle.png')
    ImageCache['BuzzyBeetleU'] = QtGui.QPixmap('reggiedata/sprites/buzzy_beetle_u.png')
    ImageCache['Spiny'] = QtGui.QPixmap('reggiedata/sprites/spiny.png')
    ImageCache['SpinyU'] = QtGui.QPixmap('reggiedata/sprites/spiny_u.png')
    ImageCache['Wiggler'] = QtGui.QPixmap('reggiedata/sprites/wiggler.png')
    ImageCache['SuperGuide'] = QtGui.QPixmap('reggiedata/sprites/superguide_block.png')
    ImageCache['RouletteBlock'] = QtGui.QPixmap('reggiedata/sprites/roulette.png')
    ImageCache['PlayerBlock'] = QtGui.QPixmap('reggiedata/sprites/player_block.png')
    ImageCache['PlayerBlockPlatform'] = QtGui.QPixmap('reggiedata/sprites/player_block_platform.png')
    ImageCache['BoxGenerator'] = QtGui.QPixmap('reggiedata/sprites/box_generator.png')
    ImageCache['StarCoin'] = QtGui.QPixmap('reggiedata/sprites/starcoin.png')
    ImageCache['InvisibleOneUp'] = QtGui.QPixmap('reggiedata/sprites/invisible_1up.png')
    ImageCache['ToadBalloon'] = QtGui.QPixmap('reggiedata/sprites/toad_balloon.png')
    ImageCache['PipePlantUp'] = QtGui.QPixmap('reggiedata/sprites/piranha_pipe_up.png')
    ImageCache['PipePlantDown'] = QtGui.QPixmap('reggiedata/sprites/piranha_pipe_down.png')
    ImageCache['PipePlantLeft'] = QtGui.QPixmap('reggiedata/sprites/piranha_pipe_left.png')
    ImageCache['PipePlantRight'] = QtGui.QPixmap('reggiedata/sprites/piranha_pipe_right.png')
    ImageCache['PipeFiretrapUp'] = QtGui.QPixmap('reggiedata/sprites/firetrap_pipe_up.png')
    ImageCache['PipeFiretrapDown'] = QtGui.QPixmap('reggiedata/sprites/firetrap_pipe_down.png')
    ImageCache['PipeFiretrapLeft'] = QtGui.QPixmap('reggiedata/sprites/firetrap_pipe_left.png')
    ImageCache['PipeFiretrapRight'] = QtGui.QPixmap('reggiedata/sprites/firetrap_pipe_right.png')

    GP = QtGui.QImage('reggiedata/sprites/ground_piranha.png')
    ImageCache['GroundPiranha'] = QtGui.QPixmap.fromImage(GP)
    ImageCache['GroundPiranhaU'] = QtGui.QPixmap.fromImage(GP.mirrored(False, True))

    BGP = QtGui.QImage('reggiedata/sprites/big_ground_piranha.png')
    ImageCache['BigGroundPiranha'] = QtGui.QPixmap.fromImage(BGP)
    ImageCache['BigGroundPiranhaU'] = QtGui.QPixmap.fromImage(BGP.mirrored(False, True))

    GF = QtGui.QImage('reggiedata/sprites/ground_firetrap.png')
    ImageCache['GroundFiretrap'] = QtGui.QPixmap.fromImage(GF)
    ImageCache['GroundFiretrapU'] = QtGui.QPixmap.fromImage(GF.mirrored(False, True))

    BGF = QtGui.QImage('reggiedata/sprites/big_ground_firetrap.png')
    ImageCache['BigGroundFiretrap'] = QtGui.QPixmap.fromImage(BGF)
    ImageCache['BigGroundFiretrapU'] = QtGui.QPixmap.fromImage(BGF.mirrored(False, True))

    BlockImage = QtGui.QPixmap('reggiedata/sprites/blocks.png')
    Blocks = []
    count = BlockImage.width() // 24
    for i in range(count):
        Blocks.append(BlockImage.copy(i*24, 0, 24, 24))
    ImageCache['Blocks'] = Blocks

def LoadDesertStuff():
    global ImageCache
    ImageCache['PokeyTop'] = QtGui.QPixmap('reggiedata/sprites/pokey_top.png')
    ImageCache['PokeyMiddle'] = QtGui.QPixmap('reggiedata/sprites/pokey_middle.png')
    ImageCache['PokeyBottom'] = QtGui.QPixmap('reggiedata/sprites/pokey_bottom.png')
    ImageCache['Lakitu'] = QtGui.QPixmap('reggiedata/sprites/lakitu.png')

def LoadPlatformImages():
    global ImageCache
    ImageCache['WoodenPlatformL'] = QtGui.QPixmap('reggiedata/sprites/wood_platform_left.png')
    ImageCache['WoodenPlatformM'] = QtGui.QPixmap('reggiedata/sprites/wood_platform_middle.png')
    ImageCache['WoodenPlatformR'] = QtGui.QPixmap('reggiedata/sprites/wood_platform_right.png')
    ImageCache['StonePlatformL'] = QtGui.QPixmap('reggiedata/sprites/stone_platform_left.png')
    ImageCache['StonePlatformM'] = QtGui.QPixmap('reggiedata/sprites/stone_platform_middle.png')
    ImageCache['StonePlatformR'] = QtGui.QPixmap('reggiedata/sprites/stone_platform_right.png')
    ImageCache['BonePlatformL'] = QtGui.QPixmap('reggiedata/sprites/bone_platform_left.png')
    ImageCache['BonePlatformM'] = QtGui.QPixmap('reggiedata/sprites/bone_platform_middle.png')
    ImageCache['BonePlatformR'] = QtGui.QPixmap('reggiedata/sprites/bone_platform_right.png')
    ImageCache['TiltingGirder'] = QtGui.QPixmap('reggiedata/sprites/tilting_girder.png')

def LoadDSStoneBlocks():
    global ImageCache
    ImageCache['DSBlockTopLeft'] = QtGui.QPixmap('reggiedata/sprites/dsblock_topleft.png')
    ImageCache['DSBlockTop'] = QtGui.QPixmap('reggiedata/sprites/dsblock_top.png')
    ImageCache['DSBlockTopRight'] = QtGui.QPixmap('reggiedata/sprites/dsblock_topright.png')
    ImageCache['DSBlockLeft'] = QtGui.QPixmap('reggiedata/sprites/dsblock_left.png')
    ImageCache['DSBlockRight'] = QtGui.QPixmap('reggiedata/sprites/dsblock_right.png')
    ImageCache['DSBlockBottomLeft'] = QtGui.QPixmap('reggiedata/sprites/dsblock_bottomleft.png')
    ImageCache['DSBlockBottom'] = QtGui.QPixmap('reggiedata/sprites/dsblock_bottom.png')
    ImageCache['DSBlockBottomRight'] = QtGui.QPixmap('reggiedata/sprites/dsblock_bottomright.png')

def LoadSwitches():
    global ImageCache
    q = QtGui.QImage('reggiedata/sprites/q_switch.png')
    p = QtGui.QImage('reggiedata/sprites/p_switch.png')
    e = QtGui.QImage('reggiedata/sprites/e_switch.png')
    ImageCache['QSwitch'] = QtGui.QPixmap.fromImage(q)
    ImageCache['PSwitch'] = QtGui.QPixmap.fromImage(p)
    ImageCache['ESwitch'] = QtGui.QPixmap.fromImage(e)
    ImageCache['QSwitchU'] = QtGui.QPixmap.fromImage(q.mirrored(True, True))
    ImageCache['PSwitchU'] = QtGui.QPixmap.fromImage(p.mirrored(True, True))
    ImageCache['ESwitchU'] = QtGui.QPixmap.fromImage(e.mirrored(True, True))
    ImageCache['QSwitchBlock'] = QtGui.QPixmap('reggiedata/sprites/q_switch_block.png')
    ImageCache['PSwitchBlock'] = QtGui.QPixmap('reggiedata/sprites/p_switch_block.png')
    ImageCache['ESwitchBlock'] = QtGui.QPixmap('reggiedata/sprites/e_switch_block.png')

def LoadCastleStuff():
    global ImageCache
    ImageCache['Podoboo'] = QtGui.QPixmap('reggiedata/sprites/podoboo.png')
    ImageCache['Thwomp'] = QtGui.QPixmap('reggiedata/sprites/thwomp.png')
    ImageCache['GiantThwomp'] = QtGui.QPixmap('reggiedata/sprites/giant_thwomp.png')
    ImageCache['SpikeBall'] = QtGui.QPixmap('reggiedata/sprites/spike_ball.png')
    ImageCache['GiantSpikeBall'] = QtGui.QPixmap('reggiedata/sprites/giant_spike_ball.png')

def LoadEnvItems():
    global ImageCache
    ImageCache['SpringBlock1'] = QtGui.QPixmap('reggiedata/sprites/spring_block.png')
    ImageCache['SpringBlock2'] = QtGui.QPixmap('reggiedata/sprites/spring_block_alt.png')
    ImageCache['RopeLadder0'] = QtGui.QPixmap('reggiedata/sprites/ropeladder_0.png')
    ImageCache['RopeLadder1'] = QtGui.QPixmap('reggiedata/sprites/ropeladder_1.png')
    ImageCache['RopeLadder2'] = QtGui.QPixmap('reggiedata/sprites/ropeladder_2.png')
    ImageCache['Fruit'] = QtGui.QPixmap('reggiedata/sprites/fruit.png')
    ImageCache['Cookie'] = QtGui.QPixmap('reggiedata/sprites/cookie.png')
    ImageCache['Muncher'] = QtGui.QPixmap('reggiedata/sprites/muncher.png')
    ImageCache['MuncherF'] = QtGui.QPixmap('reggiedata/sprites/muncher_frozen.png')
    ImageCache['Bush00'] = QtGui.QPixmap('reggiedata/sprites/bush_green_small.png')
    ImageCache['Bush01'] = QtGui.QPixmap('reggiedata/sprites/bush_green_med.png')
    ImageCache['Bush02'] = QtGui.QPixmap('reggiedata/sprites/bush_green_large.png')
    ImageCache['Bush03'] = QtGui.QPixmap('reggiedata/sprites/bush_green_xlarge.png')
    ImageCache['Bush10'] = QtGui.QPixmap('reggiedata/sprites/bush_yellow_small.png')
    ImageCache['Bush11'] = QtGui.QPixmap('reggiedata/sprites/bush_yellow_med.png')
    ImageCache['Bush12'] = QtGui.QPixmap('reggiedata/sprites/bush_yellow_large.png')
    ImageCache['Bush13'] = QtGui.QPixmap('reggiedata/sprites/bush_yellow_xlarge.png')

    doors = {'Door': 'door', 'GhostDoor': 'ghost_door', 'TowerDoor': 'tower_door', 'CastleDoor': 'castle_door', 'BowserDoor': 'bowser_door'}
    transform90 = QtGui.QTransform()
    transform180 = QtGui.QTransform()
    transform270 = QtGui.QTransform()
    transform90.rotate(90)
    transform180.rotate(180)
    transform270.rotate(270)

    for door, filename in doors.items():
        image = QtGui.QImage('reggiedata/sprites/%s.png' % filename)
        ImageCache[door+'U'] = QtGui.QPixmap.fromImage(image)
        ImageCache[door+'R'] = QtGui.QPixmap.fromImage(image.transformed(transform90))
        ImageCache[door+'D'] = QtGui.QPixmap.fromImage(image.transformed(transform180))
        ImageCache[door+'L'] = QtGui.QPixmap.fromImage(image.transformed(transform270))

def LoadMovableItems():
    global ImageCache
    ImageCache['Barrel'] = QtGui.QPixmap('reggiedata/sprites/barrel.png')
    ImageCache['OldBarrel'] = QtGui.QPixmap('reggiedata/sprites/old_barrel.png')
    ImageCache['POW'] = QtGui.QPixmap('reggiedata/sprites/pow.png')
    ImageCache['GlowBlock'] = QtGui.QPixmap('reggiedata/sprites/glow_block.png')
    ImageCache['PropellerBlock'] = QtGui.QPixmap('reggiedata/sprites/propeller_block.png')
    ImageCache['Spring'] = QtGui.QPixmap('reggiedata/sprites/spring.png')

def LoadClams():
    global ImageCache
    ImageCache['ClamPSwitchU'] = QtGui.QPixmap('reggiedata/sprites/clam_5.png')
    for i in range(8):
        ImageCache['Clam%d' % i] = QtGui.QPixmap('reggiedata/sprites/clam_%d.png' % i)

def LoadMice():
    for i in range(8):
        ImageCache['LittleMouser%d' % i] = QtGui.QPixmap('reggiedata/sprites/little_mouser_%d.png' % i)
        originalImg = QtGui.QImage('reggiedata/sprites/little_mouser_%d.png' % i)
        ImageCache['LittleMouserFlipped%d' % i] = QtGui.QPixmap.fromImage(originalImg.mirrored(True, False))

def LoadCrabs():
    global ImageCache
    ImageCache['Huckit'] = QtGui.QPixmap('reggiedata/sprites/huckit_crab.png')
    originalImg = QtGui.QImage('reggiedata/sprites/huckit_crab.png')
    ImageCache['HuckitFlipped'] = QtGui.QPixmap.fromImage(originalImg.mirrored(True, False))

def LoadFireSnake():
    global ImageCache
    ImageCache['FireSnakeWait'] = QtGui.QPixmap('reggiedata/sprites/fire_snake_0.png')
    ImageCache['FireSnake'] = QtGui.QPixmap('reggiedata/sprites/fire_snake_1.png')

def LoadPolterItems():
    global ImageCache
    ImageCache['PolterStand'] = QtGui.QPixmap('reggiedata/sprites/polter_stand.png')
    ImageCache['PolterQBlock'] = QtGui.QPixmap('reggiedata/sprites/polter_qblock.png')

def LoadFlyingBlocks():
    global ImageCache
    for color in ['yellow', 'blue', 'gray', 'red']:
        ImageCache['FlyingQBlock%s' % color] = QtGui.QPixmap('reggiedata/sprites/flying_qblock_%s.png' % color)

def LoadPipeCannon():
    for i in range(8):
        ImageCache['PipeCannon%d' % i] = QtGui.QPixmap('reggiedata/sprites/pipe_cannon_%d.png' % i)
        originalImg = QtGui.QImage('reggiedata/sprites/pipe_cannon_%d.png' % i)
        ImageCache['PipeCannonFlipped%d' % i] = QtGui.QPixmap.fromImage(originalImg.mirrored(True, False))

def LoadIceStuff():
    global ImageCache
    ImageCache['IcicleSmall'] = QtGui.QPixmap('reggiedata/sprites/icicle_small.png')
    ImageCache['IcicleLarge'] = QtGui.QPixmap('reggiedata/sprites/icicle_large.png')
    ImageCache['IcicleSmallS'] = QtGui.QPixmap('reggiedata/sprites/icicle_small_static.png')
    ImageCache['IcicleLargeS'] = QtGui.QPixmap('reggiedata/sprites/icicle_large_static.png')
    ImageCache['BigIceBlockEmpty'] = QtGui.QPixmap('reggiedata/sprites/big_ice_block_empty.png')
    ImageCache['BigIceBlockBobomb'] = QtGui.QPixmap('reggiedata/sprites/big_ice_block_bobomb.png')
    ImageCache['BigIceBlockSpikeBall'] = QtGui.QPixmap('reggiedata/sprites/big_ice_block_spikeball.png')

def LoadMushrooms():
    global ImageCache
    ImageCache['RedShroomL'] = QtGui.QPixmap('reggiedata/sprites/red_mushroom_left.png')
    ImageCache['RedShroomM'] = QtGui.QPixmap('reggiedata/sprites/red_mushroom_middle.png')
    ImageCache['RedShroomR'] = QtGui.QPixmap('reggiedata/sprites/red_mushroom_right.png')
    ImageCache['GreenShroomL'] = QtGui.QPixmap('reggiedata/sprites/green_mushroom_left.png')
    ImageCache['GreenShroomM'] = QtGui.QPixmap('reggiedata/sprites/green_mushroom_middle.png')
    ImageCache['GreenShroomR'] = QtGui.QPixmap('reggiedata/sprites/green_mushroom_right.png')
    ImageCache['BlueShroomL'] = QtGui.QPixmap('reggiedata/sprites/blue_mushroom_left.png')
    ImageCache['BlueShroomM'] = QtGui.QPixmap('reggiedata/sprites/blue_mushroom_middle.png')
    ImageCache['BlueShroomR'] = QtGui.QPixmap('reggiedata/sprites/blue_mushroom_right.png')
    ImageCache['OrangeShroomL'] = QtGui.QPixmap('reggiedata/sprites/orange_mushroom_left.png')
    ImageCache['OrangeShroomM'] = QtGui.QPixmap('reggiedata/sprites/orange_mushroom_middle.png')
    ImageCache['OrangeShroomR'] = QtGui.QPixmap('reggiedata/sprites/orange_mushroom_right.png')

def LoadFlagpole():
    global ImageCache
    ImageCache['MidwayFlag'] = QtGui.QPixmap('reggiedata/sprites/midway_flag.png')
    ImageCache['Flagpole'] = QtGui.QPixmap('reggiedata/sprites/flagpole.png')
    ImageCache['FlagpoleSecret'] = QtGui.QPixmap('reggiedata/sprites/flagpole_secret.png')
    ImageCache['Castle'] = QtGui.QPixmap('reggiedata/sprites/castle.png')
    ImageCache['CastleSecret'] = QtGui.QPixmap('reggiedata/sprites/castle_secret.png')
    ImageCache['SnowCastle'] = QtGui.QPixmap('reggiedata/sprites/snow_castle.png')
    ImageCache['SnowCastleSecret'] = QtGui.QPixmap('reggiedata/sprites/snow_castle_secret.png')

def LoadAirshipStuff():
    global ImageCache
    ImageCache['Wrench'] = QtGui.QPixmap('reggiedata/sprites/wrench.png')

def LoadUnusedStuff():
    global ImageCache
    ImageCache['Unused49'] = QtGui.QPixmap('reggiedata/sprites/unused_platform_49.png')

def LoadMinigameStuff():
    global ImageCache
    ImageCache['MGCannon'] = QtGui.QPixmap('reggiedata/sprites/mg_cannon.png')
    ImageCache['MGChest'] = QtGui.QPixmap('reggiedata/sprites/mg_chest.png')
    ImageCache['MGToad'] = QtGui.QPixmap('reggiedata/sprites/toad.png')

def LoadCastleGears():
    global ImageCache
    ImageCache['CastleGearL'] = QtGui.QPixmap('reggiedata/sprites/castle_gear_large.png')
    ImageCache['CastleGearS'] = QtGui.QPixmap('reggiedata/sprites/castle_gear_small.png')


# ---- Custom Painters ----
def PaintNothing(sprite, painter):
    pass

def PaintGenericObject(sprite, painter):
    painter.drawPixmap(0, 0, sprite.image)

def PaintAlphaObject(sprite, painter):
    painter.save()
    painter.setOpacity(sprite.alpha)
    painter.drawPixmap(0, 0, sprite.image)
    painter.restore()

def PaintBlock(sprite, painter):
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    if Tiles[sprite.tilenum] is not None:
        painter.drawPixmap(0, 0, Tiles[sprite.tilenum])
    painter.drawPixmap(0, 0, sprite.image)

def PaintWoodenPlatform(sprite, painter):
    if sprite.colour == 0:
        colour = 'Wooden'
    elif sprite.colour == 1:
        colour = 'Stone'
    elif sprite.colour == 2:
        colour = 'Bone'

    if sprite.xsize > 32:
        painter.drawTiledPixmap(QtCore.QRectF(27, 0, ((sprite.xsize * 1.5) - 51), 24), ImageCache[colour + 'PlatformM'])

    if sprite.xsize == 24:
        # replicate glitch effect forced by sprite 50
        painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache[colour + 'PlatformR'])
        painter.drawPixmap(QtCore.QPointF(8, 0), ImageCache[colour + 'PlatformL'])
    else:
        # normal rendering
        painter.drawPixmap(QtCore.QPointF((sprite.xsize - 16) * 1.5, 0), ImageCache[colour + 'PlatformR'])
        painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache[colour + 'PlatformL'])

def PaintPlatformGenerator(sprite, painter):
    PaintWoodenPlatform(sprite, painter)
    # todo: add arrows

def PaintDSStoneBlock(sprite, painter):
    middle_width = (sprite.xsize - 32) * 1.5
    middle_height = (sprite.ysize * 1.5) - 16
    bottom_y = (sprite.ysize * 1.5) - 8
    right_x = (sprite.xsize - 16) * 1.5

    painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache['DSBlockTopLeft'])
    painter.drawTiledPixmap(QtCore.QRectF(24, 0, middle_width, 8), ImageCache['DSBlockTop'])
    painter.drawPixmap(QtCore.QPointF(right_x, 0), ImageCache['DSBlockTopRight'])

    painter.drawTiledPixmap(QtCore.QRectF(0, 8, 24, middle_height), ImageCache['DSBlockLeft'])
    painter.drawTiledPixmap(QtCore.QRectF(right_x, 8, 24, middle_height), ImageCache['DSBlockRight'])

    painter.drawPixmap(QtCore.QPointF(0, bottom_y), ImageCache['DSBlockBottomLeft'])
    painter.drawTiledPixmap(QtCore.QRectF(24, bottom_y, middle_width, 8), ImageCache['DSBlockBottom'])
    painter.drawPixmap(QtCore.QPointF(right_x, bottom_y), ImageCache['DSBlockBottomRight'])

def PaintOldStoneBlock(sprite, painter):
    blockX = 0
    blockY = 0
    type = sprite.type
    width = sprite.xsize*1.5
    height = sprite.ysize*1.5

    if type == 81 or type == 83: # left spikes
        painter.drawTiledPixmap(QtCore.QRectF(0, 0, 24, height), ImageCache['SpikeL'])
        blockX = 24
        width -= 24
    if type == 84 or type == 86: # top spikes
        painter.drawTiledPixmap(QtCore.QRectF(0, 0, width, 24), ImageCache['SpikeU'])
        blockY = 24
        height -= 24
    if type == 82 or type == 83: # right spikes
        painter.drawTiledPixmap(QtCore.QRectF(blockX+width-24, 0, 24, height), ImageCache['SpikeR'])
        width -= 24
    if type == 85 or type == 86: # bottom spikes
        painter.drawTiledPixmap(QtCore.QRectF(0, blockY+height-24, width, 24), ImageCache['SpikeD'])
        height -= 24

    column2x = blockX + 24
    column3x = blockX + width - 24
    row2y = blockY + 24
    row3y = blockY + height - 24

    painter.drawPixmap(QtCore.QPointF(blockX, blockY), ImageCache['OldStoneTL'])
    painter.drawTiledPixmap(QtCore.QRectF(column2x, blockY, width-48, 24), ImageCache['OldStoneT'])
    painter.drawPixmap(QtCore.QPointF(column3x, blockY), ImageCache['OldStoneTR'])

    painter.drawTiledPixmap(QtCore.QRectF(blockX, row2y, 24, height-48), ImageCache['OldStoneL'])
    painter.drawTiledPixmap(QtCore.QRectF(column2x, row2y, width-48, height-48), ImageCache['OldStoneM'])
    painter.drawTiledPixmap(QtCore.QRectF(column3x, row2y, 24, height-48), ImageCache['OldStoneR'])

    painter.drawPixmap(QtCore.QPointF(blockX, row3y), ImageCache['OldStoneBL'])
    painter.drawTiledPixmap(QtCore.QRectF(column2x, row3y, width-48, 24), ImageCache['OldStoneB'])
    painter.drawPixmap(QtCore.QPointF(column3x, row3y), ImageCache['OldStoneBR'])

def PaintMushroomPlatform(sprite, painter):
    tilesize = 24 + (sprite.shroomsize * 24)
    if sprite.shroomsize == 0:
        if sprite.colour == 0:
            colour = 'Orange'
        else:
            colour = 'Blue'
    else:
        if sprite.colour == 0:
            colour = 'Red'
        else:
            colour = 'Green'

    painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache[colour + 'ShroomL'])
    painter.drawTiledPixmap(QtCore.QRectF(tilesize, 0, (sprite.xsize*1.5) - (tilesize * 2), tilesize), ImageCache[colour + 'ShroomM'])
    painter.drawPixmap(QtCore.QPointF((sprite.xsize*1.5) - tilesize, 0), ImageCache[colour + 'ShroomR'])

def PaintPurplePole(sprite, painter):
    painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache['VertPoleTop'])
    painter.drawTiledPixmap(QtCore.QRectF(0, 24, 24, sprite.ysize*1.5 - 48), ImageCache['VertPole'])
    painter.drawPixmap(QtCore.QPointF(0, sprite.ysize*1.5 - 24), ImageCache['VertPoleBottom'])

def PaintHorizontalRope(sprite, painter):
    endpiece = ImageCache['HorzRopeEnd']
    painter.drawPixmap(QtCore.QPointF(0, 0), endpiece)
    painter.drawTiledPixmap(QtCore.QRectF(24, 0, sprite.xsize*1.5 - 48, 24), ImageCache['HorzRope'])
    painter.drawPixmap(QtCore.QPointF(sprite.xsize*1.5 - 24, 0), endpiece)

def PaintPokey(sprite, painter):
    painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache['PokeyTop'])
    painter.drawTiledPixmap(QtCore.QRectF(0, 37, 36, sprite.ysize*1.5 - 61), ImageCache['PokeyMiddle'])
    painter.drawPixmap(QtCore.QPointF(0, sprite.ysize*1.5 - 24), ImageCache['PokeyBottom'])

def PaintColouredBox(sprite, painter):
    prefix = 'CBox%d' % sprite.colour
    xsize = sprite.xsize*1.5
    ysize = sprite.ysize*1.5

    painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache[prefix+'TL'])
    painter.drawPixmap(QtCore.QPointF(xsize-25, 0), ImageCache[prefix+'TR'])
    painter.drawPixmap(QtCore.QPointF(0, ysize-25), ImageCache[prefix+'BL'])
    painter.drawPixmap(QtCore.QPointF(xsize-25, ysize-25), ImageCache[prefix+'BR'])

    painter.drawTiledPixmap(QtCore.QRectF(25, 0, xsize-50, 25), ImageCache[prefix+'T'])
    painter.drawTiledPixmap(QtCore.QRectF(25, ysize-25, xsize-50, 25), ImageCache[prefix+'B'])
    painter.drawTiledPixmap(QtCore.QRectF(0, 25, 25, ysize-50), ImageCache[prefix+'L'])
    painter.drawTiledPixmap(QtCore.QRectF(xsize-25, 25, 25, ysize-50), ImageCache[prefix+'R'])

    painter.drawTiledPixmap(QtCore.QRectF(25, 25, xsize-50, ysize-50), ImageCache[prefix+'M'])

def PaintBoltBox(sprite, painter):
    xsize = sprite.xsize*1.5
    ysize = sprite.ysize*1.5

    painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache['BoltBoxTL'])
    painter.drawTiledPixmap(QtCore.QRectF(24, 0, xsize-48, 24), ImageCache['BoltBoxT'])
    painter.drawPixmap(QtCore.QPointF(xsize-24, 0), ImageCache['BoltBoxTR'])

    painter.drawTiledPixmap(QtCore.QRectF(0, 24, 24, ysize-48), ImageCache['BoltBoxL'])
    painter.drawTiledPixmap(QtCore.QRectF(24, 24, xsize-48, ysize-48), ImageCache['BoltBoxM'])
    painter.drawTiledPixmap(QtCore.QRectF(xsize-24, 24, 24, ysize-48), ImageCache['BoltBoxR'])

    painter.drawPixmap(QtCore.QPointF(0, ysize-24), ImageCache['BoltBoxBL'])
    painter.drawTiledPixmap(QtCore.QRectF(24, ysize-24, xsize-48, 24), ImageCache['BoltBoxB'])
    painter.drawPixmap(QtCore.QPointF(xsize-24, ysize-24), ImageCache['BoltBoxBR'])

def PaintLiftDokan(sprite, painter):
    painter.drawPixmap(0, 0, ImageCache['LiftDokanT'])
    painter.drawTiledPixmap(12, 143, 52, 579, ImageCache['LiftDokanM'])

def PaintScrewMushroom(sprite, painter):
    y = 0
    if sprite.type == 172: # with bolt
        painter.drawPixmap(70, 0, ImageCache['Bolt'])
        y += 24
    painter.drawPixmap(0, y, ImageCache['ScrewShroomT'])
    painter.drawTiledPixmap(76, y+93, 31, 172, ImageCache['ScrewShroomM'])
    painter.drawPixmap(76, y+253, ImageCache['ScrewShroomB'])

def PaintScalePlatform(sprite, painter):
    # this is FUN!! (not)
    ropeLeft = sprite.ropeLengthLeft * 24 + 4
    if sprite.ropeLengthLeft == 0: ropeLeft += 12

    ropeRight = sprite.ropeLengthRight * 24 + 4
    if sprite.ropeLengthRight == 0: ropeRight += 12

    ropeWidth = sprite.ropeWidth * 24 + 8
    platformWidth = (sprite.platformWidth + 3) * 24

    ropeX = platformWidth / 2 - 4

    painter.drawTiledPixmap(QtCore.QRectF(ropeX + 8, 0, ropeWidth - 16, 8), ImageCache['ScaleRopeH'])

    ropeVertImage = ImageCache['ScaleRopeV']
    painter.drawTiledPixmap(QtCore.QRectF(ropeX, 8, 8, ropeLeft - 8), ropeVertImage)
    painter.drawTiledPixmap(QtCore.QRectF(ropeX + ropeWidth - 8, 8, 8, ropeRight - 8), ropeVertImage)

    pulleyImage = ImageCache['ScalePulley']
    painter.drawPixmap(QtCore.QPointF(ropeX, 0), pulleyImage)
    painter.drawPixmap(QtCore.QPointF(ropeX + ropeWidth - 20, 0), pulleyImage)

    platforms = [(0, ropeLeft), (ropeX+ropeWidth-(platformWidth/2)-4, ropeRight)]
    for x,y in platforms:
        painter.drawPixmap(QtCore.QPointF(x, y), ImageCache['WoodenPlatformL'])
        painter.drawTiledPixmap(QtCore.QRectF(x + 27, y, (platformWidth - 51), 24), ImageCache['WoodenPlatformM'])
        painter.drawPixmap(QtCore.QPointF(x + platformWidth - 24, y), ImageCache['WoodenPlatformR'])

def PaintBulletBillLauncher(sprite, painter):
    painter.drawPixmap(0, 0, ImageCache['BBLauncherT'])
    painter.drawTiledPixmap(QtCore.QRectF(0, 48, 24, sprite.ysize*1.5 - 48), ImageCache['BBLauncherM'])

def PaintWiggleShroom(sprite, painter):
    xsize = sprite.xsize * 1.5
    painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache['WiggleShroomL'])
    painter.drawTiledPixmap(QtCore.QRectF(18, 0, xsize-36, 24), ImageCache['WiggleShroomM'])
    painter.drawPixmap(QtCore.QPointF(xsize-18, 0), ImageCache['WiggleShroomR'])
    painter.drawTiledPixmap(QtCore.QRectF(xsize / 2 - 12, 24, 24, sprite.ysize * 1.5 - 24), ImageCache['WiggleShroomS'])

def PaintExtendShroom(sprite, painter):
    painter.drawPixmap(0, 0, sprite.image)
    painter.drawTiledPixmap(QtCore.QRectF((sprite.xsize * 1.5) / 2 - 14, 48, 28, sprite.ysize * 1.5 - 48), ImageCache['ExtendShroomStem'])

def PaintBoltPlatform(sprite, painter):
    painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache['BoltPlatformL'])
    painter.drawTiledPixmap(QtCore.QRectF(24, 3, sprite.xsize*1.5 - 48, 24), ImageCache['BoltPlatformM'])
    painter.drawPixmap(QtCore.QPointF(sprite.xsize*1.5 - 24, 0), ImageCache['BoltPlatformR'])

def PaintBrownBlock(sprite, painter):
    blockX = 0
    blockY = 0
    type = sprite.type
    width = sprite.xsize*1.5
    height = sprite.ysize*1.5

    column2x = blockX + 24
    column3x = blockX + width - 24
    row2y = blockY + 24
    row3y = blockY + height - 24

    painter.drawPixmap(QtCore.QPointF(blockX, blockY), ImageCache['BrownBlockTL'])
    painter.drawTiledPixmap(QtCore.QRectF(column2x, blockY, width-48, 24), ImageCache['BrownBlockTM'])
    painter.drawPixmap(QtCore.QPointF(column3x, blockY), ImageCache['BrownBlockTR'])

    painter.drawTiledPixmap(QtCore.QRectF(blockX, row2y, 24, height-48), ImageCache['BrownBlockML'])
    painter.drawTiledPixmap(QtCore.QRectF(column2x, row2y, width-48, height-48), ImageCache['BrownBlockMM'])
    painter.drawTiledPixmap(QtCore.QRectF(column3x, row2y, 24, height-48), ImageCache['BrownBlockMR'])

    painter.drawPixmap(QtCore.QPointF(blockX, row3y), ImageCache['BrownBlockBL'])
    painter.drawTiledPixmap(QtCore.QRectF(column2x, row3y, width-48, 24), ImageCache['BrownBlockBM'])
    painter.drawPixmap(QtCore.QPointF(column3x, row3y), ImageCache['BrownBlockBR'])


def PaintPipe(sprite, painter):
    colour = sprite.colour
    xsize = sprite.xsize*1.5
    ysize = sprite.ysize*1.5

    if not sprite.moving:
        # Static pipes
        if sprite.orientation == 'V': # vertical
            if sprite.direction == 'U':
                painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache['PipeTop%d' % colour])
                painter.drawTiledPixmap(QtCore.QRectF(0, 24, 48, ysize-24), ImageCache['PipeMiddle%d' % colour])
            else:
                painter.drawTiledPixmap(QtCore.QRectF(0, 0, 48, ysize-24), ImageCache['PipeMiddle%d' % colour])
                painter.drawPixmap(QtCore.QPointF(0, ysize-24), ImageCache['PipeBottom%d' % colour])
        else: # horizontal
            if sprite.direction == 'L':
                painter.drawPixmap(QtCore.QPointF(0, 0), ImageCache['PipeLeft%d' % colour])
                painter.drawTiledPixmap(QtCore.QRectF(24, 0, xsize-24, 48), ImageCache['PipeCenter%d' % colour])
            else:
                painter.drawTiledPixmap(QtCore.QRectF(0, 0, xsize-24, 48), ImageCache['PipeCenter%d' % colour])
                painter.drawPixmap(QtCore.QPointF(xsize-24, 0), ImageCache['PipeRight%d' % colour])
    else:
        # Moving pipes
        length1 = sprite.length1*1.5
        length2 = sprite.length2*1.5
        low = min(length1, length2)
        high = max(length1, length2)

        if sprite.direction == 'U':
            y1 = ysize - low
            y2 = ysize - high

            # draw semi transparent pipe
            painter.save()
            painter.setOpacity(0.5)
            painter.drawPixmap(QtCore.QPointF(0, y2), ImageCache['PipeTop%d' % colour])
            painter.drawTiledPixmap(QtCore.QRectF(0, y2+24, 48, high-24), ImageCache['PipeMiddle%d' % colour])
            painter.restore()

            # draw opaque pipe
            painter.drawPixmap(QtCore.QPointF(0, y1), ImageCache['PipeTop%d' % colour])
            painter.drawTiledPixmap(QtCore.QRectF(0, y1+24, 48, low-24), ImageCache['PipeMiddle%d' % colour])

        else:
            # draw semi transparent pipe
            painter.save()
            painter.setOpacity(0.5)
            painter.drawTiledPixmap(QtCore.QRectF(0, 0, 48, high-24), ImageCache['PipeMiddle%d' % colour])
            painter.drawPixmap(QtCore.QPointF(0, high-24), ImageCache['PipeBottom%d' % colour])
            painter.restore()

            # draw opaque pipe
            painter.drawTiledPixmap(QtCore.QRectF(0, 0, 48, low-24), ImageCache['PipeMiddle%d' % colour])
            painter.drawPixmap(QtCore.QPointF(0, low-24), ImageCache['PipeBottom%d' % colour])

