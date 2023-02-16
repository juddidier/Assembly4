#!/usr/bin/env python3
# coding: utf-8
#
# LGPL
# Copyright JUD Didier
#
# infoPartConfigCmd.py

import os, json

from PySide import QtGui, QtCore
import FreeCADGui as Gui
import FreeCAD as App
from FreeCAD import Console as FCC

import Asm4_libs as Asm4
import InfoKeys

ConfUserDir = os.path.join(App.getUserAppDataDir(),'Templates')
ConfUserFilename = "Asm4_infoPartConf.json"
ConfUserFilejson = os.path.join(ConfUserDir, ConfUserFilename)


"""
    +-----------------------------------------------+
    |                  Helper Tools                 |
    +-----------------------------------------------+
"""
def writeXml(text):
    text = text.encode('unicode_escape').decode().replace('\\', '_x_m_l_')
    return text

def decodeXml(text):
    text = text.replace('_x_m_l_', '\\').encode().decode('unicode_escape')
    return text


"""
    +-----------------------------------------------+
    |                Info Part Command              |
    +-----------------------------------------------+
"""
class infoBomConfigCmd():

    def __init__(self):
        super(infoBomConfigCmd, self).__init__()

    def GetResources(self):
        tooltip  = "<p>Modify which colums are displayed in BOM list</p>"
        iconFile = os.path.join(Asm4.iconPath, 'Asm4_EditPartInfo.svg')
        return {"MenuText": "Edit BOM configuration", "ToolTip": tooltip, "Pixmap": iconFile}

    def IsActive(self):
        if App.ActiveDocument:
            return True
        return False

    def Activated(self):
        Gui.Control.showDialog(infoBomConfigUI())



class infoBOMConfigUI():

    def __init__(self):
        self.base = QtGui.QWidget()
        self.form = self.base
        iconFile = os.path.join(Asm4.iconPath, 'Asm4_EditPartInfo.svg')
        self.form.setWindowIcon(QtGui.QIcon(iconFile))
        self.form.setWindowTitle("Edit BOM configuration")
        self.drawConfigUI()


    def finish(self):
        Gui.Control.closeDialog()


    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)


    def reject(self):
        self.finish()


    def accept(self):
        self.finish()


    # Define the UI
    # TODO : make it static
    def drawConfigUI(self):
        self.label = []
        self.infos = []
        self.checker = []
        self.combo = []
        self.upcombo = []

        # Place the widgets with layouts
        self.mainLayout = QtGui.QVBoxLayout(self.form)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayoutButtons = QtGui.QGridLayout()
        self.gridLayoutUpdate = QtGui.QGridLayout()

        # 1st column holds the field names
        default = QtGui.QLabel('Field')
        self.gridLayout.addWidget(default, 0, 0)

        i = 1
        for prop in self.confTemplate:
            if self.confTemplate.get(prop).get('visible'):
                default = QtGui.QLabel(prop)
                default.setToolTip(self.infoToolTip.get(prop))
                self.gridLayout.addWidget(default, i, 0)
                self.label.append(default)
                i += 1

        self.addnewLab = QtGui.QLabel('Field')
        self.gridLayoutButtons.addWidget(self.addnewLab, 0, 0)

        self.suppLab = QtGui.QLabel('Field')
        self.gridLayoutButtons.addWidget(self.suppLab, 1, 0)

        # 2nd column holds the data
        user = QtGui.QLabel('Name')
        self.gridLayout.addWidget(user, 0, 1)

        i = 1
        for prop in self.confTemplate:
            if self.confTemplate.get(prop).get('visible'):
                propValue = QtGui.QLineEdit()
                propValue.setText(decodeXml(self.confTemplate.get(prop).get('userData')))
                self.gridLayout.addWidget(propValue, i, 1)
                self.infos.append(propValue)
                i += 1

        self.newOne = QtGui.QLineEdit()
        self.i = i
        self.gridLayoutButtons.addWidget(self.newOne, 0, 1)

        self.suppCombo =  QtGui.QComboBox()
        for prop in self.confTemplate:
            if self.confTemplate.get(prop).get('visible'):
                if prop[0:6] == 'Field_':
                    fieldRef = prop
                    fieldData = decodeXml(self.confTemplate.get(prop).get('userData'))
                    self.suppCombo.addItem(fieldRef + " - " + fieldData)

        self.gridLayoutButtons.addWidget(self.suppCombo, 1, 1)

        # 3rd column has the Active checkbox
        active = QtGui.QLabel('Active')
        self.gridLayout.addWidget(active, 0, 2)

        i = 1
        for prop in self.confTemplate:
            if self.confTemplate.get(prop).get('visible'):
                checkLayout = QtGui.QVBoxLayout()
                checked = QtGui.QCheckBox()
                checked.setChecked(self.confTemplate.get(prop).get('active'))
                self.gridLayout.addWidget(checked, i, 2)
                self.checker.append(checked)
                i += 1

        self.addnew = QtGui.QPushButton('Add')
        self.gridLayoutButtons.addWidget(self.addnew, 0, 2)
        self.suppBut = QtGui.QPushButton('Delete')
        self.gridLayoutButtons.addWidget(self.suppBut, 1, 2)

        # Actions
        self.addnew.clicked.connect(self.addNewManField)
        self.suppBut.clicked.connect(self.deleteField)

        # Insert layout in mainlayout
        self.mainLayout.addLayout(self.gridLayout)
        self.mainLayout.addLayout(self.gridLayoutButtons)

        # Show the update if any
        if self.updateAutoFieldlist() != None:
            updateLab = QtGui.QLabel('Update automatic input field')
            self.gridLayoutUpdate.addWidget(updateLab, 0, 0)
            self.upCombo = QtGui.QComboBox()
            self.gridLayoutUpdate.addWidget(self.upCombo, 1, 0)

            for prop in self.updateAutoFieldlist():
                self.upCombo.addItem(prop)
            self.upBut = QtGui.QPushButton('Update')
            self.gridLayoutUpdate.addWidget(self.upBut, 1, 1)

            # Actions
            self.upBut.clicked.connect(self.updateAutoField)

            # Insert layout in mainlayout
            self.mainLayout.addLayout(self.gridLayoutUpdate)


# Add the command in the workbench
Gui.addCommand('Asm4_BomConfig', infoBomConfigCmd())
