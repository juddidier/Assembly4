#!/usr/bin/env python3
# coding: utf-8
#
# makeBomCmd.py
#
# Parses the Assembly 4 Model tree and creates a list of parts

import os
import json
import re

from PySide import QtGui, QtCore
import FreeCADGui as Gui
import FreeCAD as App

import Asm4_libs as Asm4
import infoPartCmd
import InfoKeys
from FastenersLib import isFastener

crea = infoPartCmd.infoPartUI.makePartInfo
fill = infoPartCmd.infoPartUI.infoDefault

ConfUserDir = os.path.join(App.getUserAppDataDir(),'Templates')
ConfUserFilename = "Asm4_infoPartConf.json"
ConfUserFilejson = os.path.join(ConfUserDir, ConfUserFilename)

'''
# Check if the configuration file exists
try:
    file = open(ConfUserFilejson, 'r')
    file.close()
except:
    partInfoDef = dict()
    for prop in InfoKeys.partInfo:
        partInfoDef.setdefault(prop, {'userData': prop, 'active': True, 'visible': True})
    for prop in InfoKeys.partInfo_Invisible:
        partInfoDef.setdefault(prop, {'userData': prop, 'active': True, 'visible': False})
    try:
        os.mkdir(ConfUserDir)
    except:
        pass
    file = open(ConfUserFilejson, 'x')
    json.dump(partInfoDef, file)
    file.close()

# Load user's config file
file = open(ConfUserFilejson, 'r')
infoKeysUser = json.load(file).copy()
file.close()
'''


class makeBOM:

    def __init__(self, follow_subassemblies=True):
        super(makeBOM, self).__init__()
        self.follow_subassemblies = follow_subassemblies
        '''
        file = open(ConfUserFilejson, 'r')
        self.infoKeysUser = json.load(file).copy()
        file.close()
        '''

    def GetResources(self):

        if self.follow_subassemblies == True:
            menutext = "Bill of Materials"
            tooltip  = "Create the Bill of Materials of the Assembly including sub-assemblies"
            iconFile = os.path.join( Asm4.iconPath, 'Asm4_PartsList_Subassemblies.svg' )
        else:
            menutext = "Local Bill of Materials"
            tooltip  = "Create the Bill of Materials of the Assembly"
            iconFile = os.path.join( Asm4.iconPath, 'Asm4_PartsList.svg' )

        return {
            "MenuText": menutext,
            "ToolTip": tooltip,
            "Pixmap": iconFile
        }

    def IsActive(self):
        if Asm4.getAssembly() is None:
            return False
        else:
            return True

    def Activated(self):
        self.UI = QtGui.QDialog()
        self.modelDoc = App.ActiveDocument
        # open user part info template
        file = open(ConfUserFilejson, 'r')
        self.infoKeysUser = json.load(file).copy()
        file.close()

        try:
            self.model = self.modelDoc.Assembly
            print("ASM4> BOM of the Assembly 4 Model")
        except:
            try:
                self.model = self.modelDoc.Model
                print("ASM4> BOM of the legacy Assembly 4 Model")
            except:
                print("ASM4> BOM might not work with this file")

        self.drawUI()
        self.UI.show()
        self.BOM.clear()
        self.Verbose = str()
        self.PartsList = {}

        if self.follow_subassemblies == True:
            print("ASM4> BOM following sub-assemblies")
        else:
            print("ASM4> BOM local parts only")
        
        self.listParts(self.model)
        self.inSpreadsheet()
        self.BOM.setPlainText(self.Verbose)

    def indent(self, level, tag="|"):
        spaces = (level + 1) * "  "
        return "[{level}]{spaces}{tag} ".format(level=str(level), tag=tag, spaces=spaces)

    def listParts(self, obj, level=0, parent=None):
        def isVariantLink(obj):
            if not obj:
                return False
            if obj.TypeId == 'Part::FeaturePython' and hasattr(obj, 'Type'):
                if 'VariantLink' in getattr(obj, 'Type'):
                    return True
            return False
            
        def isAssembly(obj):
            if not obj:
                return False
            if hasattr(obj, 'Type'):
                if 'Assembly' in getattr(obj, 'Type'):
                    return True
            return False

        file = open(ConfUserFilejson, 'r')
        self.infoKeysUser = json.load(file).copy()
        file.close()

        max_level = 1000
        if self.follow_subassemblies == False:
            max_level = 2;

        if obj == None:
            return

        if self.PartsList == None:
            self.PartsList = {}
        
        if hasattr(obj, 'Type'):
            objType = getattr(obj, 'Type')
        else:
            objType = "none"

        print("ASM4> {level}{obj_typeid} | {obj_name} | {obj_label} | {obj_type}".format(level=self.indent(level), obj_label=obj.Label, obj_name=obj.FullName, obj_typeid=obj.TypeId, obj_type=objType))
        Gui.updateGui()

        if (obj.TypeId=='App::Part') or isVariantLink(obj) or isFastener(obj):
            if (level > 0) and not isAssembly(obj):
                # write PartsList
                # test if the part already exist on PartsList
                try:
                    partName = getattr(obj,self.infoKeysUser.get('PartName').get('userData'))
                except:
                    partName = obj.Label
                if partName in self.PartsList:
                    # if already exist =+ 1 in qty of this part count
                    self.PartsList[partName]['Qty.'] = self.PartsList[partName]['Qty.'] + 1
                else:
                    # if not exist , create a dict() for this part
                    self.PartsList[partName] = dict()
                    for prop in self.infoKeysUser:
                        if self.infoKeysUser.get(prop).get('active'):
                            try:
                                # try to get partInfo in part
                                getattr(obj,self.infoKeysUser.get(prop).get('userData'))
                            except AttributeError:
                                self.Verbose+='create Part Information for '+partName+'\n'
                                self.BOM.setPlainText(self.Verbose);
#                                self.Verbose+='you don\'t have fill the info of this Part :'+ obj.Label +'\n'
                                crea(self,obj)
#                                self.Verbose+='info create for :'+ obj.Label +'\n'
                                fill(obj)
#                                self.Verbose+='info auto filled for :'+ obj.Label+'\n'
                            self.PartsList[partName][self.infoKeysUser.get(prop).get('userData')] = getattr(obj,self.infoKeysUser.get(prop).get('userData'))
                    self.PartsList[partName]['Qty.'] = 1

        #===================================
        # Continue walking inside the groups
        #===================================

        if obj.TypeId == 'App::Link':
            # Navigate on objects inside a App:Links
            if obj.ElementCount > 0:
                for i in range(obj.ElementCount):
                    self.listParts(obj.LinkedObject, level, parent=obj)
            else:
                self.listParts(obj.LinkedObject, level + 1, parent=obj)

        # Navigate on objects inide a folders
        if obj.TypeId == 'App::DocumentObjectGroup':
            for objname in obj.getSubObjects():
                subobj = obj.Document.getObject(objname[0:-1])
                self.listParts(subobj, level, parent=obj)

        # Navigate on objects inide a ASM4 Part (Links and Folders)
        if obj.TypeId == 'App::Part' and hasattr(obj, 'Type') and getattr(obj, 'Type')=='Assembly':# or isVariantLink(obj):
            print(str(obj.getSubObjects()))
            for objname in obj.getSubObjects():
                subobj = obj.Document.getObject(objname[0:-1])
                self.listParts(subobj, level+1, parent=obj)

        return
        self.Verbose += '\nBOM creation is done\n'


    # Copy Parts list to Spreadsheet
    def inSpreadsheet(self):
        document = App.ActiveDocument
        plist = self.PartsList

        if len(plist) == 0:
            return

        if self.follow_subassemblies:
            if not hasattr(document, 'BOM'):
                spreadsheet = document.addObject('Spreadsheet::Sheet', 'BOM')
            else:
                spreadsheet = document.BOM
            spreadsheet.Label = "BOM"
        else:
            if not hasattr(document, 'BOM_Local'):
                spreadsheet = document.addObject('Spreadsheet::Sheet', 'BOM_Local')
            else:
                spreadsheet = document.BOM_Local
            spreadsheet.Label = "BOM_Local"

        spreadsheet.clearAll()


        # Write rows in the spreadsheet
        def wrow(drow: [str], row: int):
            for i, d in enumerate(drow):
                if row == 0:
                    spreadsheet.set(str(chr(ord('a') + i)).upper() + str(row + 1), infoPartCmd.decodeXml(str(d)))
                else:
                    spreadsheet.set(str(chr(ord('a') + i)).upper() + str(row + 1), str(d))

        data = list(plist.values()) # present data in the order it is in the Object tree

        wrow(data[0].keys(), 0)
        for i, _ in enumerate(data):
            wrow(data[i].values(), i + 1)

        document.recompute()

        self.Verbose += "\n" + spreadsheet.Label + ' spreadsheet was created.\n'


    def onOK(self):
        document = App.ActiveDocument
        if self.follow_subassemblies:
            Gui.Selection.addSelection(document.Name, 'BOM')
        else:
            Gui.Selection.addSelection(document.Name, 'BOM_Local')
        self.UI.close()

    # Define the UI (static elements, only)
    def drawUI(self):
        # Main Window (QDialog)
        self.UI.setWindowTitle('Parts List (BOM)')
        self.UI.setWindowIcon(QtGui.QIcon(os.path.join(Asm4.iconPath , 'FreeCad.svg')))
        self.UI.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.UI.setModal(False)
        self.mainLayout = QtGui.QVBoxLayout(self.UI)

        # Help and Log
        self.LabelBOML1 = QtGui.QLabel()
        self.LabelBOML1.setText('BOM generates bill of materials.\n\nIt uses the Parts\' info to generate entries on BOM, unless autofill is set.\n')
        self.LabelBOML2 = QtGui.QLabel()
        self.LabelBOML2.setText("Check <a href='https://github.com/Zolko-123/FreeCAD_Assembly4/tree/master/Examples/ConfigBOM/README.md'>BOM tutorial</a>")
        self.LabelBOML2.setOpenExternalLinks(True)
        self.LabelBOML3 = QtGui.QLabel()
        self.LabelBOML3.setText('\n\nReport:')

        self.mainLayout.addWidget(self.LabelBOML1)
        self.mainLayout.addWidget(self.LabelBOML2)
        self.mainLayout.addWidget(self.LabelBOML3)

        # The Log view is a plain text field
        self.BOM = QtGui.QPlainTextEdit()
        self.BOM.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.mainLayout.addWidget(self.BOM)

        # the button row definition
        self.buttonLayout = QtGui.QHBoxLayout()

        # OK button
        self.OkButton = QtGui.QPushButton('OK')
        self.OkButton.setDefault(True)
        self.buttonLayout.addWidget(self.OkButton)
        self.mainLayout.addLayout(self.buttonLayout)

        # finally, apply the layout to the main window
        self.UI.setLayout(self.mainLayout)

        # Actions
        self.OkButton.clicked.connect(self.onOK)


# Add the command in the workbench
Gui.addCommand('Asm4_makeLocalBOM', makeBOM(follow_subassemblies=False))
Gui.addCommand('Asm4_makeBOM', makeBOM(follow_subassemblies=True))
