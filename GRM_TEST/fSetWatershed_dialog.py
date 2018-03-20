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
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import QWebView
import os
import Util
from PyQt4 import QtGui, uic
import GRM_Plugin
import ElementTree as ET
import GRM_Plugin_dockwidget as GRM

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'fSetWatershed.ui'))
_util =Util.util()

class FSetWatershedDialog(QtGui.QDialog, FORM_CLASS):
    plot1= None
    def __init__(self, parent=None):
        """Constructor."""
        super(FSetWatershedDialog, self).__init__(parent)
        self.setupUi(self)
        # 2017-11-28 박: 최박사님과 협의 하여 프로그램 기능 변경 시행 (화면 UI 및 기능 변경)
        #콤보 박스 레이어 목록 셋팅
        self.SetComboxLayerList()
        # 2017-06-22 프로젝트 파일에 콤보박스 레이어 목록과 QGIS 레이어 목록 비교하여 
        # 둘이 동일한 파일이 있을시에 콤보 박스에 셋팅 기능
        self.SetProjectToCombobox()
        #chkStreamLayer 체크 박스 체크시 이벤트 처리
        self.chkStreamLayer.setChecked(True)   # 기본 설정은 체크
        #체크 박스 체크시 비활성화 체크 박스 
        self.chkStreamLayer.stateChanged.connect(self.chkStreamLayer_CheckedChanged)

        # chkChannelWidthLayer 체크 박스 체크시 이벤트 처리
        # self.chkChannelWidthLayer.setChecked(False)  # 기본 설정은 체크 안함
        # self.cmbChannelWidthLayer.setEnabled(False)  # 기본 설정은 사용 안함
        # self.chkiniSoilRatioLayer.setChecked(False)  # 기본 설정은 사용 안함
        # self.cmbiniSoilRatioLayer.setEnabled(False)  # 기본 설정은 사용 안함

        #체크 박스 클릭 이벤트 연동
        self.chkiniSoilRatioLayer.stateChanged.connect(self.chkiniSoilRatioLayer_CheckedChanged)
        self.chkChannelWidthLayer.stateChanged.connect(self.chkChannelWidthLayer_CheckedChanged)
        self.chkIniFlow.stateChanged.connect(self.chkIniFlow_CheckedChanged)


        # OK 버튼 처리 이벤트
        self.btnOK.clicked.connect(self.ClickOK)

        # 폼 종료 버튼 이벤트 처리
        self.btnCancel.clicked.connect(self.Close_Form)


    def SetComboxLayerList(self):
        # QGIS 레이어 목록 받아오기
        layers = GRM_Plugin._iface.legendInterface().layers()
        # 레전드에서 받아온 레이어 목록을 콤보 박스에 셋팅
        _util.SetCommbox(layers, self.cmbWatershedArea, "tif")
        _util.SetCommbox(layers, self.cmbWatershedSlope, "tif")
        _util.SetCommbox(layers, self.cmbFdir, "tif")
        _util.SetCommbox(layers, self.cmbFac, "tif")
        _util.SetCommbox(layers, self.cmbStream, "tif")
        _util.SetCommbox(layers, self.cmbChannelWidthLayer, "tif")
        _util.SetCommbox(layers, self.cmbiniSoilRatioLayer, "tif")
        _util.SetCommbox(layers, self.cmbiniFlowLayer, "tif")


    # chkStreamLayer 체크 박스 이벤트
    def chkStreamLayer_CheckedChanged(self):
        self.cmbStream.setEnabled(self.chkStreamLayer.checkState())
        self.chkChannelWidthLayer.setEnabled(self.chkStreamLayer.checkState())
        self.chkIniFlow.setEnabled(self.chkStreamLayer.checkState())
        self.cmbiniFlowLayer.setEnabled(self.chkIniFlow.checkState())

        if self.chkStreamLayer.checkState() ==False:
            self.chkChannelWidthLayer.setChecked(False)
            self.cmbChannelWidthLayer.setEnabled(False)

            self.chkIniFlow.setChecked(False)
            self.cmbiniFlowLayer.setEnabled(False)

            # self.chkiniSoilRatioLayer.setChecked(False)
            # self.cmbiniSoilRatioLayer.setEnabled(False)

    # chkChannelWidthLayer 체크 박스 이벤트
    def chkChannelWidthLayer_CheckedChanged(self):
        if self.chkChannelWidthLayer.isChecked():
            self.cmbChannelWidthLayer.setEnabled(True)
        else:
            self.cmbChannelWidthLayer.setEnabled(False)

    def chkiniSoilRatioLayer_CheckedChanged(self):
        if self.chkiniSoilRatioLayer.isChecked():
            self.cmbiniSoilRatioLayer.setEnabled(True)
        else:
            self.cmbiniSoilRatioLayer.setEnabled(False)


    def chkIniFlow_CheckedChanged(self):
        self.cmbiniFlowLayer.setEnabled(self.chkIniFlow.checkState())


    def SetProjectToCombobox(self):
        # 각각의 변수에 XML 값 할당

        self.mGridWSFPN = GRM._xmltodict['GRMProject']['ProjectSettings']['WatershedFile']
        if self.mGridWSFPN != "" and self.mGridWSFPN is not None:
            mGridNameWS = _util.GetFilename(self.mGridWSFPN)
            self.Setcombobox(self.cmbWatershedArea, mGridNameWS, self.mGridWSFPN)

        # Slop
        self.mGridSlopeFPN = GRM._xmltodict['GRMProject']['ProjectSettings']['SlopeFile']
        if self.mGridSlopeFPN != "" and self.mGridSlopeFPN is not None:
            mGridNameSlope = _util.GetFilename(self.mGridSlopeFPN)
            self.Setcombobox(self.cmbWatershedSlope, mGridNameSlope, self.mGridSlopeFPN)

        # Flowdirection
        self.mGridFdirFPN = GRM._xmltodict['GRMProject']['ProjectSettings']['FlowDirectionFile']
        if self.mGridFdirFPN != "" and self.mGridFdirFPN is not None:
            mGridNameFdir = _util.GetFilename(self.mGridFdirFPN)
            self.Setcombobox(self.cmbFdir, mGridNameFdir, self.mGridFdirFPN)

        # FlowAC
        self.mGridFacFPN = GRM._xmltodict['GRMProject']['ProjectSettings']['FlowAccumFile']
        if self.mGridFacFPN != "" and self.mGridFacFPN is not None:
            mGridNameFac = _util.GetFilename(self.mGridFacFPN)
            self.Setcombobox(self.cmbFac, mGridNameFac, self.mGridFacFPN)

        # Stream
        self.mGridStreamFPN = GRM._xmltodict['GRMProject']['ProjectSettings']['StreamFile']
        if self.mGridStreamFPN != "" and self.mGridStreamFPN is not None:
            mGridNameStream = _util.GetFilename(self.mGridStreamFPN)
            self.Setcombobox(self.cmbStream, mGridNameStream, self.mGridStreamFPN)

        # Channel
        #  파싱 방법을 바꿔야 하는데 임시로 처리 흠 흠.....
        # 프로젝트 파일에서 null 처리
        self.mGridChannelWidthFPN = GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthFile']

        if self.mGridChannelWidthFPN is None or self.mGridChannelWidthFPN=="" :
            self.chkChannelWidthLayer.setChecked(False)
            self.cmbChannelWidthLayer.setEnabled(False)
        else :
            self.chkChannelWidthLayer.setChecked(True)
            self.cmbChannelWidthLayer.setEnabled(True)
            mGridNameChannelWidth = _util.GetFilename(self.mGridChannelWidthFPN)
            self.Setcombobox(self.cmbChannelWidthLayer, mGridNameChannelWidth, self.mGridChannelWidthFPN)

        self.miniSoilRatio = GRM._xmltodict['GRMProject']['ProjectSettings']['InitialSoilSaturationRatioFile']
        if self.miniSoilRatio is not None and self.miniSoilRatio !="":
            self.chkiniSoilRatioLayer.setChecked(True)
            self.cmbiniSoilRatioLayer.setEnabled(True)
            name = _util.GetFilename(self.miniSoilRatio)
            self.Setcombobox(self.cmbiniSoilRatioLayer, name, self.miniSoilRatio)
        else:
            self.chkiniSoilRatioLayer.setChecked(False)
            self.cmbiniSoilRatioLayer.setEnabled(False)

        self.InitialChannelFlowFile = GRM._xmltodict['GRMProject']['ProjectSettings']['InitialChannelFlowFile']
        if self.InitialChannelFlowFile is not None and  self.InitialChannelFlowFile !="":
            self.chkIniFlow.setChecked(True)
            self.cmbiniFlowLayer.setEnabled(True)
            name = _util.GetFilename(self.InitialChannelFlowFile)
            self.Setcombobox(self.cmbiniFlowLayer, name, self.InitialChannelFlowFile)
        else:
            self.chkIniFlow.setChecked(False)
            self.cmbiniFlowLayer.setEnabled(False)


        # FD
        self.mFDType = GRM._xmltodict['GRMProject']['ProjectSettings']['FlowDirectionType']

        if self.mFDType == "StartsFromN" :
            self.rbFDIndexTypeN.setChecked(True)
        elif self.mFDType == "StartsFromNE":
            self.rbFDIndexTypeNE.setChecked(True)
        elif self.mFDType == "StartsFromE":
            self.rdioEAST.setChecked(True)
        else:
            self.rdioTaudem.setChecked(True)


    # 콤보 박스에 있는 목록중에 프로젝트 상에 있는 레이어 비교 하여 셋팅
    def Setcombobox(self,commbox,layername,filepath):
        index = commbox.findText(str(layername), Qt.MatchFixedString)
        if _util.GetTxtToLayerPath(layername) == filepath :
            if index >= 0:
                commbox.setCurrentIndex(index)

    # OK 버튼 이벤트
    def ClickOK(self):
        # 콤보 박스와 체크 박스등 기본적인 선택 내용 확인 하여 오류 메시지 출력

        try:

            flag=self.ValidateInputs()
            if flag :
                raise Exception
            # 선택된 값들 글로벌 변수에 값을 넣음 나중에 값을 XML에 넣을 것임
            self.mGridWSFPN = _util.GetcomboSelectedLayerPath(self.cmbWatershedArea)
            self.mGridSlopeFPN = _util.GetcomboSelectedLayerPath(self.cmbWatershedSlope)
            self.mGridFdirFPN = _util.GetcomboSelectedLayerPath(self.cmbFdir)
            self.mGridFacFPN = _util.GetcomboSelectedLayerPath(self.cmbFac)

            if self.rbFDIndexTypeN.isChecked()==True :
                self.mFDType = "StartsFromN"
            elif self.rbFDIndexTypeNE.isChecked()==True :
                self.mFDType = "StartsFromNE"
            elif self.rdioEAST.isChecked()==True :
                self.mFDType = "StartsFromE"
            else:
                self.mFDType = "StartsFromE_TauDEM"

            if self.chkiniSoilRatioLayer.checkState() :
                if self.cmbiniSoilRatioLayer.currentIndex() != 0:
                    self.miniSoilRatio =  _util.GetcomboSelectedLayerPath(self.cmbiniSoilRatioLayer)
                else:
                    self.miniSoilRatio=""

            if self.chkStreamLayer.checkState() :
                self.mGridStreamFPN = _util.GetcomboSelectedLayerPath(self.cmbStream)
                if self.chkChannelWidthLayer.checkState() :
                    if self.cmbChannelWidthLayer.currentIndex()!=0:
                        self.mGridChannelWidthFPN = _util.GetcomboSelectedLayerPath(self.cmbChannelWidthLayer)
                    else :
                        self.mGridChannelWidthFPN =""



            if self.chkIniFlow.checkState():
                if self.cmbiniFlowLayer.currentIndex()!=0:
                    self.InitialChannelFlowFile = _util.GetcomboSelectedLayerPath(self.cmbiniFlowLayer)
                else:
                    self.InitialChannelFlowFile=""

            self.SetXML()

        except Exception :
            pass
        else:
            quit_msg = " Watershed setup is completed.   "
            reply = QtGui.QMessageBox.information(self, 'Watershed',quit_msg, QtGui.QMessageBox.Ok)
            if reply == QtGui.QMessageBox.Ok:
                self.close()


    

    def ValidateInputs(self):
        #각각 콥보 박스중 선택된것이 없을때 메시지 출력및 포커스 이동
       try:
           if self.cmbWatershedArea.currentIndex() == 0:
                self.cmbWatershedArea.setFocus()
                raise Exception("\n No layer selected. \n")
           elif self.cmbWatershedSlope.currentIndex() == 0:
               self.cmbWatershedSlope.setFocus()
               raise Exception("\n No layer selected. \n")
           elif self.cmbFdir.currentIndex() == 0:
               self.cmbFdir.setFocus()
               raise Exception("\n No layer selected. \n")
           elif self.cmbFac.currentIndex() == 0:
               self.cmbFac.setFocus()
               raise Exception("\n No layer selected. \n")
       except Exception as exce:
            _util.MessageboxShowError("Setup watershed data", exce.args[0])
            return True




    # def ErrorMessage(self,combox):
    #     _util.MessageboxShowInfo("Setup watershed data", "\n No layer selected. \n")
    #     combox.setFocus()
    #     return

    def SetXML(self):
        # WatershedFile
        GRM._xmltodict['GRMProject']['ProjectSettings']['WatershedFile'] = self.mGridWSFPN
        # Slop
        GRM._xmltodict['GRMProject']['ProjectSettings']['SlopeFile'] = self.mGridSlopeFPN
        # Flowdirection
        GRM._xmltodict['GRMProject']['ProjectSettings']['FlowDirectionFile'] = self.mGridFdirFPN
        # FlowAccu
        GRM._xmltodict['GRMProject']['ProjectSettings']['FlowAccumFile'] = self.mGridFacFPN
        # FDType
        GRM._xmltodict['GRMProject']['ProjectSettings']['FlowDirectionType'] = self.mFDType
        # Stream

        if self.chkIniFlow.checkState():
            GRM._xmltodict['GRMProject']['ProjectSettings']['InitialChannelFlowFile']= self.InitialChannelFlowFile
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['InitialChannelFlowFile'] = ""


        if self.chkStreamLayer.checkState():
            GRM._xmltodict['GRMProject']['ProjectSettings']['StreamFile'] = self.mGridStreamFPN
        else :
            GRM._xmltodict['GRMProject']['ProjectSettings']['StreamFile'] = ""

        # ChannelWidthFile

        if self.chkChannelWidthLayer.checkState() and self.chkStreamLayer.checkState():
            GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthFile'] = self.mGridChannelWidthFPN
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthFile'] = ""


        if self.chkiniSoilRatioLayer.checkState() and self.chkStreamLayer.checkState():
            GRM._xmltodict['GRMProject']['ProjectSettings']['InitialSoilSaturationRatioFile']= self.miniSoilRatio
        else :
            GRM._xmltodict['GRMProject']['ProjectSettings']['InitialSoilSaturationRatioFile'] = ""


        CellSize=GRM._xmltodict['GRMProject']['ProjectSettings']['GridCellSize']
        if CellSize == None or CellSize=="":
            name = _util.GetFilename(self.mGridWSFPN)
            for layer in QgsMapLayerRegistry.instance().mapLayers().values():
                if layer.name() == name:
                    GRM._xmltodict['GRMProject']['ProjectSettings']['GridCellSize'] = str(layer.rasterUnitsPerPixelX())

    # 프로그램 종료
    def Close_Form(self):
        self.close()



















