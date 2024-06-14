#!/usr/bin/env python3
# coding: utf-8
#
# FastenersLib.py




import os

from PySide import QtGui, QtCore
import FreeCADGui as Gui
import FreeCAD as App
from FreeCAD import Console as FCC
from BearBase import bearBaseObject
#from FastenerBase import FSBaseObject
#from ScrewMaker import screwTables
#import FastenersCmd as FS

import Asm4_libs as Asm4

# icon to show in the Menu, toolbar and widget window
#iconFile = os.path.join( Asm4.iconPath , 'Asm4_mvFastener.svg')

def isBearing(obj):
    if not obj:
        return False
    if (hasattr(obj,'Proxy') and isinstance(obj.Proxy, bearBaseObject)):
        return True
    return False
