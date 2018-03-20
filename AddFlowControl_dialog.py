# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FlatDialog
                                 A QGIS plugin
 Flat
                             -------------------
        begin                : 2017-04-26
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Hermesys
        email                : shpark@hermesys.co.kr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

# from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui, uic
from FileFormat_dialog import FileFormat
import GRM_Plugin_dockwidget as GRM
import Watershed_Stetup_dialog as ws
import ElementTree as ET
import Util


_FilePath = ""

_util = Util.util()

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'AddFlowControl_dialog_base.ui'))


class AddFlowControl(QtGui.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(AddFlowControl, self).__init__(parent)

        self.setupUi(self)
        combolist = ['Reservoir outflow', 'Inlet', 'Reservoir operation', 'Sink flow','Source flow']
        self.cmb_ControlType.addItems(combolist)
        self.cmb_ControlType.currentIndexChanged.connect(
            lambda: self.SelectControtype(self.cmb_ControlType, self.txt_TimeInterval, self.btnLoadFile,
                                          self.btnFileFormat, self.txtFilePath))
        self.btnLoadFile.clicked.connect(lambda: self.FileSelectDialog(self.txtFilePath))
        self.btnFileFormat.clicked.connect(self.ViewFileFormat)
        self.rdoAutomatic.clicked.connect(self.ClickRdoAutomatic)
        self.txt_cms.setEnabled(False)
        self.txt_hours.setEnabled(False)
        self.txt_Constant_discharge.setEnabled(False)
        self.SelectControtype(self.cmb_ControlType, self.txt_TimeInterval, self.btnLoadFile,self.btnFileFormat, self.txtFilePath)
        self.rdoAutomatic.setChecked(True)

        self.rdoRigid.clicked.connect(self.ClickRdoRigid)
        self.rdoUsingConstant.clicked.connect(self.ClickRdoUsingConstant)
        self.btnCancel.clicked.connect(self.Close_Form)
        self.btnOK.clicked.connect(self.Ok_click)

        if ws._AddFlowcontrol_Edit_or_Insert_type != "Insert":
            self.SetControlData()




    def SelectControtype(self, combox, txtinterval, btnLoadFile, btnFileFormat, txtFilePath):
        if combox.currentText() == "Reservoir operation":
            txtinterval.setEnabled(True)
            btnLoadFile.setEnabled(False)
            btnFileFormat.setEnabled(False)
            txtFilePath.setEnabled(False)
            self.txtIniStorage.setEnabled(True)
            self.txtMaxStorage.setEnabled(True)
            self.txtMaxStorageRatio.setEnabled(True)
            self.rdoAutomatic.setEnabled(True)
            self.rdoRigid.setEnabled(True)
            self.rdoUsingConstant.setEnabled(True)
            # self.txt_cms.setEnabled(True)
            # self.txt_Constant_discharge.setEnabled(True)
            # self.txt_hours.setEnabled(True)


            if self.rdoAutomatic.isChecked():
                self.txt_cms.setEnabled(False)
                self.txt_Constant_discharge.setEnabled(False)
                self.txt_hours.setEnabled(False)
            elif self.rdoRigid.isChecked():
                self.txt_cms.setText(ws._EditFlowROConstQ)
                self.ClickRdoRigid()
            elif self.rdoUsingConstant.isChecked():
                self.rdoUsingConstant.setChecked(True)
                self.txt_Constant_discharge.setText(ws._EditFlowROConstQ)
                self.txt_hours.setText(ws._EditFlowROConstQDuration)
                self.ClickRdoUsingConstant()




        else:
            txtinterval.setEnabled(True)
            btnLoadFile.setEnabled(True)
            btnFileFormat.setEnabled(True)
            txtFilePath.setEnabled(True)
            self.txtIniStorage.setEnabled(False)
            self.txtMaxStorage.setEnabled(False)
            self.txtMaxStorageRatio.setEnabled(False)
            self.rdoAutomatic.setEnabled(False)
            self.rdoRigid.setEnabled(False)
            self.rdoUsingConstant.setEnabled(False)
            self.txt_cms.setEnabled(False)
            self.txt_Constant_discharge.setEnabled(False)
            self.txt_hours.setEnabled(False)

    def FileSelectDialog(self, txtpath):
        txtpath.clear();
        dir = os.path.dirname(os.path.realpath(__file__))
        self.filename = QFileDialog.getOpenFileName(self, "select file ", dir, "*.txt")
        txtpath.setText(self.filename)

    def ClickRdoAutomatic(self):
        self.txt_cms.setEnabled(False)
        self.txt_hours.setEnabled(False)
        self.txt_Constant_discharge.setEnabled(False)

    def ClickRdoRigid(self):
        self.txt_cms.setEnabled(True)
        self.txt_hours.setEnabled(False)
        self.txt_Constant_discharge.setEnabled(False)

    def ClickRdoUsingConstant(self):
        self.txt_cms.setEnabled(False)
        self.txt_hours.setEnabled(True)
        self.txt_Constant_discharge.setEnabled(True)

    def ViewFileFormat(self):
        results = FileFormat()
        results.exec_()

    def Close_Form(self):
        self.close()

    def Ok_click(self):
        if ws._AddFlowcontrol_Edit_or_Insert_type == "Insert":
            if self.txt_Name.text() =="" :
                _util.MessageboxShowInfo("Add Flow Control"," Input name, please")
                self.txt_Name.setFocus()
                return
            else:
                ws._AddFlowcontrolName = self.txt_Name.text()

            ws._AddFlowcontrolType = self.cmb_ControlType.currentText()
            if self.txt_TimeInterval.text() == "":
                _util.MessageboxShowInfo("Add Flow Control", " Please enter a time interval")
                self.txt_TimeInterval.setFocus()
                return
            else:
                ws._AddFlowcontrolTimeInterval = self.txt_TimeInterval.text()
            if self.cmb_ControlType.currentText() != "Reservoir operation":
                if self.txtFilePath.text()=="":
                    _util.MessageboxShowInfo("Add Flow Control", " Please set file path")
                    self.txtFilePath.setFocus()
                    return
                else:
                    ws._AddFlowcontrolFilePath = self.txtFilePath.text()
            else :
                ws._EditFlowFlowDataFile = "ResurvoirOperation"
            if self.cmb_ControlType.currentText() == "Reservoir operation":
                if self.txtIniStorage.text() !="":
                    ws._AddFlowcontrol_IniStorage = self.txtIniStorage.text()
                if self.txtMaxStorage.text()!="":
                    ws._AddFlowcontrol_MaxStorage = self.txtMaxStorage.text()
                if self.txtMaxStorageRatio.text()!="":
                    ws._AddFlowcontrol_MaxStorageR = self.txtMaxStorageRatio.text()
                if self.rdoAutomatic.isChecked():
                    ws._AddFlowcontrol_ROType = "AutoROM"

                elif self.rdoRigid.isChecked():
                    ws._AddFlowcontrol_ROType = "RigidROM"
                    ws._AddFlowcontrol_ROConstQ = self.txt_cms.text()

                elif self.rdoUsingConstant.isChecked():
                    ws._AddFlowcontrol_ROType = "ConstantQ"
                    ws._AddFlowcontrol_ROConstQ = self.txt_Constant_discharge.text()
                    ws._AddFlowcontrol_ROConstQDuration = self.txt_hours.text()
                ws._Flowcontrolgrid_flag_Insert = True
            else:
                ws._AddFlowcontrol_IniStorage = ""
                ws._AddFlowcontrol_MaxStorage = ""
                ws._AddFlowcontrol_MaxStorageR = ""
                ws._AddFlowcontrol_ROType = ""
                ws._AddFlowcontrol_ROConstQ = ""
                ws._AddFlowcontrol_ROConstQDuration = ""
                ws._Flowcontrolgrid_flag_Insert = True
            self.Close_Form()

        else:
            if self.txt_Name.text() == "":
                _util.MessageboxShowInfo("Add Flow Control", " Input name, please")
                self.txt_Name.setFocus()
                return
            else:
                ws._EditFlowName = self.txt_Name.text()

            ws._EditFlowControlType = self.cmb_ControlType.currentText()

            if self.txt_TimeInterval.text() == "":
                _util.MessageboxShowInfo("Add Flow Control", " Please enter a time interval")
                self.txt_TimeInterval.setFocus()
                return
            else:
                ws._EditFlowDT = self.txt_TimeInterval.text()

            if self.cmb_ControlType.currentText() != "Reservoir operation":
                if self.txtFilePath.text() == "":
                    _util.MessageboxShowInfo("Add Flow Control", " Please set file path")
                    self.txtFilePath.setFocus()
                    return
                else:
                    ws._EditFlowFlowDataFile = self.txtFilePath.text()
            else:
                ws._EditFlowFlowDataFile = "ResurvoirOperation"

            if self.cmb_ControlType.currentText() == "Reservoir operation":
                if self.txtIniStorage.text() != "":
                    ws._EditFlowIniStorage = self.txtIniStorage.text()

                if self.txtMaxStorage.text() != "":
                    ws._EditFlowMaxStorage = self.txtMaxStorage.text()

                if self.txtMaxStorageRatio.text() != "":
                    ws._EditFlowMaxStorageR = self.txtMaxStorageRatio.text()

                if self.rdoAutomatic.isChecked():
                    ws._EditFlowROType = "AutoROM"

                elif self.rdoRigid.isChecked():
                    ws._EditFlowROType = "RigidROM"
                    ws._EditFlowROConstQ = self.txt_cms.text()

                elif self.rdoUsingConstant.isChecked():
                    ws._EditFlowROType = "ConstantQ"
                    ws._EditFlowROConstQ = self.txt_Constant_discharge.text()
                    ws._EditFlowROConstQDuration = self.txt_hours.text()
            else:
                ws._EditFlowIniStorage = ""
                ws._EditFlowMaxStorage = ""
                ws._EditFlowMaxStorageR = ""
                ws._EditFlowROType = ""
                ws._EditFlowROConstQ = ""
                ws._EditFlowROConstQDuration = self.txt_hours.text()

            self.UpdateEditTable()
            self.Close_Form()


    def SetControlData(self):
        self.txt_Name.setText(ws._EditFlowName)
        controltype =ws._EditFlowControlType
        index = self.cmb_ControlType.findText(str(controltype), Qt.MatchFixedString)
        if index >= 0:
            self.cmb_ControlType.setCurrentIndex(index)
        self.txt_TimeInterval.setText(ws._EditFlowDT)
        self.txtFilePath.setText(ws._EditFlowFlowDataFile)
        self.txtIniStorage.setText(ws._EditFlowIniStorage)
        self.txtMaxStorage.setText(ws._EditFlowMaxStorage)
        self.txtMaxStorageRatio.setText(ws._EditFlowMaxStorageR)

        if ws._EditFlowROType == "AutoROM":
            self.rdoAutomatic.setChecked(True)
        elif ws._EditFlowROType == "RigidROM":
            self.rdoRigid.setChecked(True)
            self.txt_cms.setText(ws._EditFlowROConstQ)
            self.ClickRdoRigid()
        elif ws._EditFlowROType == "ConstantQ":
            self.rdoUsingConstant.setChecked(True)
            self.txt_Constant_discharge.setText(ws._EditFlowROConstQ )
            self.txt_hours.setText(ws._EditFlowROConstQDuration)
            self.ClickRdoUsingConstant()
        self.SelectControtype(self.cmb_ControlType, self.txt_TimeInterval, self.btnLoadFile,
                              self.btnFileFormat, self.txtFilePath)

    def UpdateEditTable(self):
        ws._FlowControlTable.setItem(ws._EditFlowCurrentRow, 2, QTableWidgetItem(ws._EditFlowName))
        ws._FlowControlTable.setItem(ws._EditFlowCurrentRow, 3, QTableWidgetItem(ws._EditFlowDT))
        ws._FlowControlTable.setItem(ws._EditFlowCurrentRow, 4, QTableWidgetItem(ws._EditFlowControlType))
        ws._FlowControlTable.setItem(ws._EditFlowCurrentRow, 5, QTableWidgetItem(ws._EditFlowFlowDataFile))
        ws._FlowControlTable.setItem(ws._EditFlowCurrentRow, 6, QTableWidgetItem(ws._EditFlowIniStorage))
        ws._FlowControlTable.setItem(ws._EditFlowCurrentRow, 7, QTableWidgetItem(ws._EditFlowMaxStorage))
        ws._FlowControlTable.setItem(ws._EditFlowCurrentRow, 8, QTableWidgetItem(ws._EditFlowMaxStorageR))
        ws._FlowControlTable.setItem(ws._EditFlowCurrentRow, 9, QTableWidgetItem(ws._EditFlowROType))
        ws._FlowControlTable.setItem(ws._EditFlowCurrentRow, 10, QTableWidgetItem(ws._EditFlowROConstQ))
        ws._FlowControlTable.setItem(ws._EditFlowCurrentRow, 11, QTableWidgetItem(ws._EditFlowROConstQDuration))




        # if self.rdoAutomatic.isChecked():
        #     ws._AddFlowcontrol_ROType = "AutoROM"
        #
        # elif self.rdoRigid.isChecked():
        #     ws._AddFlowcontrol_ROType = "RigidROM"
        #     ws._AddFlowcontrol_ROConstQ = self.txt_cms.text()
        #
        # elif self.rdoUsingConstant.isChecked():
        #     ws._AddFlowcontrol_ROType = "ConstantQ"
        #     ws._AddFlowcontrol_ROConstQ = self.txt_Constant_discharge.text()
        #     ws._AddFlowcontrol_ROConstQDuration = self.txt_hours.text()



        # self.txt_cms(ws._Edit)
        #
        # rdoAutomatic
        # rdoRigid
        # rdoUsingConstant


        # count  = _util.FlowControlGrid_XmlCount()
        # if ws._Flowcontrolgrid_xmlCount==1:
        #     self.txt_Name.setText(GRM._xmltodict['GRMProject']['FlowControlGrid']['Name'])
        #     controltype =GRM._xmltodict['GRMProject']['FlowControlGrid']['ControlType']
        #     self.txt_TimeInterval.setText(GRM._xmltodict['GRMProject']['FlowControlGrid']['DT'])
        #     self.txtFilePath.setText(GRM._xmltodict['GRMProject']['FlowControlGrid']['FlowDataFile'])
        #
        # elif ws._Flowcontrolgrid_xmlCount>1:
        #     for flowitem in GRM._xmltodict['GRMProject']['FlowControlGrid']:
        #         if flowitem['ColX']==ws._ClickX and flowitem['RowY'] == ws._ClickY :
        #             self.txt_Name.setText(flowitem['Name'])
        #             controltype = flowitem['ControlType']
        #             self.txt_TimeInterval.setText(flowitem['DT'])
        #             self.txtFilePath.setText(flowitem['FlowDataFile'])
        #             return
        #






        # if 'Name' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
        #     _util.MessageboxShowError("count", "1")
        #     for flowitem in GRM._xmltodict['GRMProject']['FlowControlGrid']:
        #         _util.MessageboxShowError("count", "2")
        #         test.append(flowitem['name@'])
        #         _util.MessageboxShowError("count", "3")
        #         # _util.MessageboxShowError("count",str(len(test)))
        # else:
        #     _util.MessageboxShowError("OUT", "OUT")






        # ProjectFile = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
        # doc = ET.parse(ProjectFile)
        # root = doc.getroot()
        # for element in root.findall('{http://tempuri.org/GRMProject.xsd}FlowControlGrid'):
        #     # if x== element.findtext("{http://tempuri.org/GRMProject.xsd}ColX") and y ==element.findtext("{http://tempuri.org/GRMProject.xsd}RowY") :
        #     if element.findtext("{http://tempuri.org/GRMProject.xsd}ColX")=="90" and element.findtext("{http://tempuri.org/GRMProject.xsd}RowY")=="51":
        #         self.txt_Name.setText(element.findtext("{http://tempuri.org/GRMProject.xsd}Name"))
        #         self.txt_TimeInterval.setText(element.findtext("{http://tempuri.org/GRMProject.xsd}DT"))
        #         self.txtFilePath.setText(element.findtext("{http://tempuri.org/GRMProject.xsd}FlowDataFile"))
        #         self.txtIniStorage.setText(element.findtext("{http://tempuri.org/GRMProject.xsd}IniStorage"))
        #         self.txtMaxStorage.setText(element.findtext("{http://tempuri.org/GRMProject.xsd}MaxStorage"))
        #         self.txtMaxStorageRatio.setText(element.findtext("{http://tempuri.org/GRMProject.xsd}MaxStorageR"))
        #         types=element.findtext("{http://tempuri.org/GRMProject.xsd}ROType")
        #         if types=="AutoROM":
        #             self.rdoAutomatic.setChecked(True)
        #         elif types == "RigidROM":
        #             self.rdoRigidsetChecked(True)
        #         elif types == "ConstantQ":
        #             self.rdoUsingStorageEqation.setChecked(True)
        #
        #         self.txt_Constant_discharge.setText(element.findtext("{http://tempuri.org/GRMProject.xsd}ROConstQ"))
        #         self.txt_hours.setText(element.findtext("{http://tempuri.org/GRMProject.xsd}ROConstQDuration"))
        #         self.txt_hours.setText(element.findtext("{http://tempuri.org/GRMProject.xsd}ROConstQDuration"))
        #







                # self.tlbFlowControl.setItem(row, 4, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}ControlType")))
                # self.tlbFlowControl.setItem(row, 5, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}FlowDataFile")))
                # row = row + 1


