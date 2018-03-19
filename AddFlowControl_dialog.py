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
from PyQt4 import QtGui, uic
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QFileInfo
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
        combolist = ['Select control type', 'Reservoir outlfow', 'Inlet', 'Reservoir Operation', 'Sink flow','Source flow']
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

        self.rdoAutomatic.setChecked(True)

        self.rdoRigid.clicked.connect(self.ClickRdoRigid)
        self.rdoUsingConstant.clicked.connect(self.ClickRdoUsingConstant)
        self.btnCancel.clicked.connect(self.Close_Form)
        self.btnOK.clicked.connect(self.Ok_click)

        if ws._AddFlowcontrol_Edit_or_Insert_type != "Insert":
            self.SetControlData()


    def SelectControtype(self, combox, txtinterval, btnLoadFile, btnFileFormat, txtFilePath):
        if combox.currentText() == "Reservoir Operation":
            txtinterval.setEnabled(False)
            btnLoadFile.setEnabled(False)
            btnFileFormat.setEnabled(False)
            txtFilePath.setEnabled(False)
            self.txtIniStorage.setEnabled(True)
            self.txtMaxStorage.setEnabled(True)
            self.txtMaxStorageRatio.setEnabled(True)
        else:
            txtinterval.setEnabled(True)
            btnLoadFile.setEnabled(True)
            btnFileFormat.setEnabled(True)
            txtFilePath.setEnabled(True)
            self.txtIniStorage.setEnabled(False)
            self.txtMaxStorage.setEnabled(False)
            self.txtMaxStorageRatio.setEnabled(False)

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
        if self.txt_Name.text() =="" :
            _util.MessageboxShowInfo("Add Flow Control"," Input name, please")
            self.txt_Name.setFocus()
            return
        else:
            ws._AddFlowcontrolName = self.txt_Name.text()

        if self.cmb_ControlType.currentIndex() == 0:
            _util.MessageboxShowInfo("Add Flow Control", " Please select control type")
            return
        else:
            ws._AddFlowcontrolType = self.cmb_ControlType.currentText()

        if self.txt_TimeInterval.text() == "":
            _util.MessageboxShowInfo("Add Flow Control", " Please enter a time interval")
            self.txt_TimeInterval.setFocus()
            return
        else:
            ws._AddFlowcontrolTimeInterval = self.txt_TimeInterval.text()

        if self.txtFilePath.text()=="":
            _util.MessageboxShowInfo("Add Flow Control", " Please set file path")
            self.txtFilePath.setFocus()
            return
        else:
            ws._AddFlowcontrolFilePath = self.txtFilePath.text()

        ws._Flowcontrolgrid_flag_Insert = True
        self.Close_Form()

    def SetControlData(self):
        count  = _util.FlowControlGrid_XmlCount()
        if ws._Flowcontrolgrid_xmlCount==1:
            # self.txt_TimeInterval.setText(GRM._xmltodict['GRMProject']['FlowControlGrid']['ColX'])
            # self.txt_TimeInterval.setText(GRM._xmltodict['GRMProject']['FlowControlGrid']['RowY'])
            self.txt_Name.setText(GRM._xmltodict['GRMProject']['FlowControlGrid']['Name'])
            controltype =GRM._xmltodict['GRMProject']['FlowControlGrid']['ControlType']
            self.txt_TimeInterval.setText(GRM._xmltodict['GRMProject']['FlowControlGrid']['DT'])
            self.txtFilePath.setText(GRM._xmltodict['GRMProject']['FlowControlGrid']['FlowDataFile'])

        elif ws._Flowcontrolgrid_xmlCount>1:
            for flowitem in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                if flowitem['ColX']==ws._ClickX and flowitem['RowY'] == ws._ClickY :
                    self.txt_Name.setText(flowitem['Name'])
                    controltype = flowitem['ControlType']
                    self.txt_TimeInterval.setText(flowitem['DT'])
                    self.txtFilePath.setText(flowitem['FlowDataFile'])
                    return







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


