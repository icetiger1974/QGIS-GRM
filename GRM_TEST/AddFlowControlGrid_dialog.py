# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FillSinkDialog
                                 A QGIS plugin
 FillSink plug-in
                             -------------------
        begin                : 2017-03-13
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
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QFileInfo
import os
import Util
from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'AddFlowControlGrid.ui'))

_layerPath=""
_util = Util.util()
class AddFlowControlGridDialog(QtGui.QDialog, FORM_CLASS):

    # ReservoirOutflow  #상류모의, 저류량 고려하지 않고, 댐에서의 방류량만 고려함
    # Inlet   # 상류 모의하지 않는것. 저류량 고려하지 않고, inlet grid에서의 outfow 만 고려함.
    # SinkFlow   # '상류모의, 입력된 sink flow data 고려함. 저수지 고려안함.
    # SourceFlow # '상류모의, 입력된 source flow data 고려함. 저수지 고려안함.
    # ReservoirOperation # '상류모의, 저수지 고려, 방류량은 operation rule에 의해서 결정됨. 사용자 입력 인터페이스 구현하지 않음.# ' 저류량-방류량, 유입량-방류량 관계식을 이용해서 소스코드에 반영 가능
    # NONE

    def __init__(self, parent=None):
        """Constructor."""
        super(AddFlowControlGridDialog, self).__init__(parent)
        self.setupUi(self)
        self.SetCombo(self.cmbControType)
        self.btnCancel.clicked.connect(self.Close_Form)
        self.btnOk.clicked.connect(self.ClickOK)
        self.cmbControType.activated.connect(self.changeRadio)
        # self.rbROConstantQ.activated.connect(self)



    #콤보 박스 셋팅
    def SetCombo(self,commbobox):
        commbobox.clear()
        # 추후 이사 갈것임 임시로 여기서 셋팅
        layer_list = ['ReservoirOutflow', 'Inlet', 'SinkFlow', 'SourceFlow', 'ReservoirOperation', 'NONE']
        combolist = ['select layer']
        combolist.extend(layer_list)
        commbobox.addItems(combolist)

    # 열거형 사용 추후 사용 변경
    def enum(*sequential, **named):
        enums = dict(zip(sequential, range(len(sequential))), **named)
        reverse = dict((value, key) for key, value in enums.iteritems())
        enums['reverse_mapping'] = reverse
        return type('Enum', (), enums)

    def ClickOK(self):
        self.ValidateInput()
        self.close()

    #폼 종료
    def Close_Form(self):
        self.close()

    # 콤보 박스 값에 따라 그룹 박스 및 텍스트 박스 활성/ 비활성
    def changeRadio(self):
        if self.cmbControType.currentText() == 'ReservoirOperation':
            self.txtFCDataDT.setText = ""
            self.txtFCDataDT.setEnabled(False)
            self.gbReservoirOperation.setEnabled(True)
            self.gbStorageCondition.setEnabled(True)
        else:
            self.txtFCDataDT.setEnabled(True)
            self.gbReservoirOperation.setEnabled(False)
            self.gbStorageCondition.setEnabled(False)

    def ValidateInput(self):
        if self.txtFCGridName.text()=="" :
            _util.MessageboxShowInfo("GRM","Flow control name is invalid.")
            self.txtFCGridName.setFocus()
            return False

        if self.cmbControType.Text != "ReservoirOperation" :
            self.cmbControType.setFocus()
            _util.MessageboxShowInfo("Flow control data time interval is invalid.")
            return False
        return  True



    def rbRO_CheckedChanged(self):
        if gbReservoirOperation.Enabled == True:
            txtRORigidROMConstQ.setEnabled(rbRORigidROM.checkState())
            txtROConstantQ.setEnabled(rbROConstantQ.checkState())
            txtROConstantQDuration.setEnabled(rbROConstantQ.checkState())

    # def ValidateForStorageAndReservoir(self):
    #     If txtFCDataDT = True
    #     If Not mtxtValTimeInterval.Validate
    #     MsgBox(mtxtValTimeInterval.ErrorMsg, MsgBoxStyle.Exclamation, cGRM.BuildInfo.ProductName)
    #     mTxtValRORigid.TextBox.Focus()
    #     Return False


