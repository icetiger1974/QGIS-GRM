# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Watershed_StetupDialog
                                 A QGIS plugin
 Watershed Stetup
                             -------------------
        begin                : 2017-04-05
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
import sys
from qgis.core import *
from qgis.gui import *
from qgis.gui import QgsColorButton
from PyQt4 import QtGui, uic
from PyQt4.QtGui import *
import ElementTree as ET
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import test
import Util
import GRM_Plugin
import GRM_Plugin_dockwidget
import datetime
import GRM_GetSet
import GRM_Plugin_dockwidget as GRM
from plugin.dict2xml import dict2xml
import xmltodict
import tempfile



reload(sys)
sys.setdefaultencoding('utf8')

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'SetLCST.ui'))
path = os.path.dirname(os.path.realpath(__file__))

_SelectRow=0
_util  = Util.util()

class SetLCST_StetupDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(SetLCST_StetupDialog, self).__init__(parent)
        self.setupUi(self)

        # 프로그램 대폭 수정 처리 시작 2017-06-16
        # 프로그램 대폭 수정 처리 시작 2차 2017-12-05

        # 초기 모든 변수값 셋팅
        self.SetProjectValue()

        # 초기에 각각의 컨트롤 들의 기본값을 셋팅
        self.InitControls()

        # 각각의 테이블에 데이터 값 읽어서 넣기
        # 1순위 - 프로젝트 파일 데이터
        # 2순위 - 프로젝트 파일 내에 Vat 파일 경로
        self.SetTableData()
        # 테이블 더블 클릭 이벤트(더블 클릭시 사용자가 선택 할수 있는 테이블 메시지 창이 뜨게 됨)
        self.tlbLandCover.itemDoubleClicked.connect(lambda: self.aboutApp("LandCover", self.tlbLandCover.currentRow()))
        self.tblGreenAmpt.itemDoubleClicked.connect(lambda: self.aboutApp("GreenAmpt", self.tblGreenAmpt.currentRow()))
        self.tblSoilDepth.itemDoubleClicked.connect(lambda: self.aboutApp("SoilDepth", self.tblSoilDepth.currentRow()))

# 
        #-------- 2017/10/11 CHO 여기부터----------
        self.btnCancel.clicked.connect(self.closeForm)
 
        # 확인버튼을 눌렀을 때
        self.btnOK.clicked.connect(self.OKForm)
 
 
        # Vat 선택 버튼 클릭 이벤트(서택된 파일로 테이블값이 변경 됨)
        self.btnVatLand.clicked.connect(lambda :self.SelectVat("btnVatLand",self.txtLandCover))
        self.btnVatAmpt.clicked.connect(lambda :self.SelectVat("btnVatAmpt",self.txtSoilTexture))
        self.btnVatDepth.clicked.connect(lambda :self.SelectVat("btnVatDepth",self.txtSoilDepth))
 
 
        # 콤보 박스 변경시 선택된 콤보 박스 레이어 목록으로 Table 셋팅
        self.cmbLandCover.activated.connect(lambda :self.Get_ComboBox_LayerPath(self.cmbLandCover,self.tlbLandCover,self.txtLandCover,"LandCover"))
        self.cmbSoilTexture.activated.connect(lambda :self.Get_ComboBox_LayerPath(self.cmbSoilTexture,self.tblGreenAmpt,self.txtSoilTexture,"GreenAmpt"))
        self.cmbSoilDepth.activated.connect(lambda :self.Get_ComboBox_LayerPath(self.cmbSoilDepth,self.tblSoilDepth,self.txtSoilDepth,"SoilDepth"))





    # 초기 모든 변수값 셋팅 (프로젝트 파일에서 값을 읽어서 초기 셋팅 값을 결정함)
    def SetProjectValue(self):
        self.LandCoverType = GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverDataType']
        self.SoilTextureType = GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureDataType']
        self.SoilDepthType = GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthDataType']




    # 각각의 컨트롤 들을 초기 값이나 설정을 셋팅
    def InitControls(self):
        # 콤보 박스에 레이어 목록 적용 값 셋팅
        self.SetLayerListCombobox()
        
        #이 부분이 현재 문제임.. 나중에 해결하겠음
        # 라디오 버튼 셋팅
        self.SetRadio()
        
#         # 테이블 헤더 설정
        self.SetTableHeader()
        
    # 콤보 박스에 레이어 목록 넣어 두기
    def SetLayerListCombobox(self):
        # 콤보 박스 레이어 받아 오기 설정
        layers = GRM_Plugin._iface.legendInterface().layers()
        _util.SetCommbox(layers, self.cmbLandCover, "")
        _util.SetCommbox(layers, self.cmbSoilTexture, "")
        _util.SetCommbox(layers, self.cmbSoilDepth, "")


    # ====================각각의 테이블 헤더 셋팅 ======================================================================
    def SetTableHeader(self):
        self.SetLandCoverHeader()
        
        self.SetGreenAmptHeader()
        
        self.SetSoilDepthHeader()
        
    # LandCover Table 헤더 셋팅
    def SetLandCoverHeader(self):
        # table header set(메이창 테이블 타이틀 설정)
        self.tlbLandCover.setColumnCount(7)
        self.tlbLandCover.setHorizontalHeaderLabels(
            ['GridValue', 'UserLandCover', 'GRMCode', 'LandCoverE', 'LandCoverK', 'RoughnessCoefficient',
             'ImperviousRatio'])

    # GreenAmpt Table 헤더 셋팅
    def SetGreenAmptHeader(self):
        self.tblGreenAmpt.setColumnCount(9)
        self.tblGreenAmpt.setHorizontalHeaderLabels(
            ['GridValue', 'USERSoil', 'GRMCode', 'GRMTextureE', 'GRMTextureK', 'Porosity', 'EffectivePorosity',
             'WFSoilSuctionHead', 'HydraulicConductivity'])

    # SoilDepth 테이블 헤더 셋팅
    def SetSoilDepthHeader(self):
        self.tblSoilDepth.setColumnCount(6)
        self.tblSoilDepth.setHorizontalHeaderLabels(
            ['GridValue', 'UserDepthClass', 'GRMCode', 'SoilDepthClassE', 'SoilDepthClassK', 'SoilDepth'])

    # =================================================헤더 셋팅 종료===================================================


    # =================================================라디오 버튼 셋팅 시작============================================
    # 라디오 버튼 셋팅
    def SetRadio(self):
        # Lanccover 첫번째 라디오 버튼 클릭 이벤트 처리
        self.rbtUseLCLayer.clicked.connect(self.LCLaye_CheckedChanged)
        
        # Lanccover 두번째 라디오 버튼 클릭 이벤트 처리
        self.rbtUseConstLCAtt.clicked.connect(self.ConstLCAtt_CheckedChanged)
         
        # SoilTexture 첫번째 라디오 버튼 클릭 이벤트 처리
        self.rbtUseSoilTextureLayer.clicked.connect(self.SoilTextureLayer_CheckedChanged)
         
        # SoilTexture 두번째 라디오 버튼 클릭 이벤트 처리
        self.rbtUseConstTextureAtt.clicked.connect(self.TextureAtt_CheckedChanged)
         
        # SoilDepth  첫번째 라디오 버튼 클릭 이벤트 처리
        self.rbtUseSoilDepthLayer.clicked.connect(self.SoilDepthLayer_CheckedChanged)
         
        # SoilDepth  두번째 라디오 버튼 클릭 이벤트 처리
        self.rbtUseConstDepth.clicked.connect(self.ConstDepth_CheckedChanged)
        

        # ------------------------Lndcover 라디오 버튼 셋팅 시작---------------------------------
        #2017/11/27 =====
        
        if self.LandCoverType == "File":
            
            # 라디오 버튼 클릭시 활성, 비활성 컨트롤 함수
            self.LCLaye_CheckedChanged()

            # 라디오 버튼 체크 상태로 변환
            self.rbtUseLCLayer.setChecked(True)

            # 텍스트 파일에 Vat 파일 경로를 셋팅
            self.txtLandCover.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverVATFile'])

            # 콤보 박스의 선택 레이어를 프로젝트 파일에 있는 것으로 셋팅
            LandCoverFile = GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverFile']
            if self.txtLandCover.text() != "":
                LandCoverName = self.GetFilename(LandCoverFile)
                self.Setcombobox(self.cmbLandCover, LandCoverName, LandCoverFile)
        else :
            # 2번째 라디오 버튼 클릭시 이벤트 함수
            self.ConstLCAtt_CheckedChanged()

            # 2번째 라디오 버튼 체크 상태로 변환
            self.rbtUseConstLCAtt.setChecked(True)

            # 사용자 일괄 적용 라디오 버튼 클릭시 적용 할 텍스트 박스의 값을 셋팅
            self.txtCoefficient.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantRoughnessCoeff'])
            self.txtImpervious.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantImperviousRatio'])
        # ------------------------Lndcover 라디오 버튼 셋팅 종료----------------------------------




        # ------------------------SoilTextureVATFile 라디오 버튼 셋팅 시작---------------------------------
        # SoilTextureVATFile 이벤트
        if self.SoilTextureType== "File":
            # SoilTextureVATFile 항목의 첫번째 라디오 버튼 클릭 이벤트(컨트롤 활성, 비활성 기능 연동)
            self.SoilTextureLayer_CheckedChanged()
            
            # 라디오 버튼 클릭 상태로 셋팅
            self.rbtUseSoilTextureLayer.setChecked(True)
            
            # 텍스트 박스에 VAT 파일 경로 넣기
            self.txtSoilTexture.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureVATFile'])
            
            # layer 콤보 박스 항목을 프로젝트 파일의 데이터 내용에 해당되는 콤보 박스 항목으로 셋팅
            SoilTextureFile = GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureFile']
            if self.txtSoilTexture.text() != "":
                SoilTextureName = self.GetFilename(SoilTextureFile)
                
                self.Setcombobox(self.cmbSoilTexture, SoilTextureName, SoilTextureFile)
  
        else:
            # 2번째 라디오 버튼(일괄 적용) 클릭 이벤트
            self.TextureAtt_CheckedChanged()
  
            # 라디오 버튼 클릭 상태로 설정
            self.rbtUseConstTextureAtt.setChecked(True)
            
  
            # 프로젝트 파일에서 각각 텍스트 값을 입력
            self.txtPorosity.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilPorosity'])
            self.txtEffective_porosity.setText(
                GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilEffPorosity'])
            self.txtSuction_head.setText(
                GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilWettingFrontSuctionHead'])
            self.txtConductiovity.setText(
                GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilHydraulicConductivity'])
        
  
        # ------------------------SoilTextureVATFile 라디오 버튼 셋팅 종료----------------------------------
  
  
        # ------------------------SoilDepth 라디오 버튼 셋팅 시작----------------------------------
        if self.SoilDepthType== "File":
  
            # SoilDepth 항목의 첫번째 체크 박스 선택 이벤트 함수
            self.SoilDepthLayer_CheckedChanged()
  
            # SoilDepth 항목의 첫번째 라디오 버튼 클릭 상태로 설정
            self.rbtUseSoilDepthLayer.setChecked(True)
  
            # 텍스트 박스에 VAT 파일 경로 넣기
            self.txtSoilDepth.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthVATFile'])
  
            # layer 콤보 박스 항목을 프로젝트 파일의 데이터 내용에 해당되는 콤보 박스 항목으로 셋팅
            SoilDepthFile = GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthFile']
            if self.txtSoilDepth.text() != "":
                SoilDepthName = self.GetFilename(SoilDepthFile)
                self.Setcombobox(self.cmbSoilDepth, SoilDepthName, SoilDepthFile)
        else :
  
            # SoilDepth 항목의 두번째 체크 박스 선택 이벤트 함수
            self.ConstDepth_CheckedChanged()
  
            # SoilDepth 항목의 두번째 라디오 버튼 클릭 상태로 설정
            self.rbtUseConstDepth.setChecked(True)
  
            # 프로젝트 파일에서 값읽어서 텍스트 박스에 셋팅
            self.txtSoil_depth.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilDepth'])
 
        # ------------------------SoilDepth 라디오 버튼 셋팅 종료----------------------------------

    # =================================================라디오 버튼 셋팅 종료============================================


    # LandCover 첫번째 라이디오 버튼 클릭시 이벤트 처리
    def LCLaye_CheckedChanged(self):
        self.btnVatLand.setEnabled(True)
        self.txtLandCover.setEnabled(True)
        self.cmbLandCover.setEnabled(True)
        self.tlbLandCover.setEnabled(True)
        self.txtCoefficient.setEnabled(False)
        self.txtImpervious.setEnabled(False)

    # LandCover 두번째 라이디오 버튼 클릭시 이벤트 처리
    def ConstLCAtt_CheckedChanged(self):
        self.btnVatLand.setEnabled(False)
        self.txtLandCover.setEnabled(False)
        self.cmbLandCover.setEnabled(False)
        self.tlbLandCover.setEnabled(False)
        self.txtCoefficient.setEnabled(True)
        self.txtImpervious.setEnabled(True)


    # =========================================================
    # SoilTexture 첫번째 라디오 버튼 클릭 이벤트 처리
    def SoilTextureLayer_CheckedChanged(self):
        self.cmbSoilTexture.setEnabled(True)
        self.txtSoilTexture.setEnabled(True)
        self.btnVatAmpt.setEnabled(True)
        self.tblGreenAmpt.setEnabled(True)
        self.txtPorosity.setEnabled(False)
        self.txtEffective_porosity.setEnabled(False)
        self.txtSuction_head.setEnabled(False)
        self.txtConductiovity.setEnabled(False)

    # SoilTexture 두번째 라디오 버튼 클릭 이벤트 처리
    def TextureAtt_CheckedChanged(self):
        self.cmbSoilTexture.setEnabled(False)
        self.txtSoilTexture.setEnabled(False)
        self.btnVatAmpt.setEnabled(False)
        self.tblGreenAmpt.setEnabled(False)
        self.txtPorosity.setEnabled(True)
        self.txtEffective_porosity.setEnabled(True)
        self.txtSuction_head.setEnabled(True)
        self.txtConductiovity.setEnabled(True)


    # =========================================================
    # SoilDepth  첫번째 라디오 버튼 클릭 이벤트 처리
    def SoilDepthLayer_CheckedChanged(self):
        self.cmbSoilDepth.setEnabled(True)
        self.txtSoilDepth.setEnabled(True)
        self.btnVatDepth.setEnabled(True)
        self.tblSoilDepth.setEnabled(True)
        self.txtSoil_depth.setEnabled(False)
    # SoilDepth  두번째 라디오 버튼 클릭 이벤트 처리
    def ConstDepth_CheckedChanged(self):
        self.cmbSoilDepth.setEnabled(False)
        self.txtSoilDepth.setEnabled(False)
        self.btnVatDepth.setEnabled(False)
        self.tblSoilDepth.setEnabled(False)
        self.txtSoil_depth.setEnabled(True)



    # 테이블에 데이터 값 넣기
    def SetTableData(self):
        # 1순위 프로젝트 파일내 데이터 값
        # 2순위 Vat 파일 셋팅
        
        #2017/11/27 =====
        
        if self.LandCoverType =="File" and GRM._LandCoverCount!= 0:
            self.SetLandCoverTalbe()
        if self.SoilTextureType=="File" and GRM._GreenAmptCount!=0:
            self.SetGreenAmptTalbe()
        if self.SoilDepthType=="File" and GRM._SoilDepthCount!= 0:
            self.SetSoilDepthTalbe()


    def SetLandCoverTalbe(self):
        try:
            # 프로젝트 파일에서 불러온 데이터 테이블에 셋팅
            if GRM._LandCoverCount >1:
                row = 0
                for artikel in GRM._xmltodict['GRMProject']['LandCover']:
                    self.tlbLandCover.insertRow(row)

                    item1 = QtGui.QTableWidgetItem(artikel['GridValue'])
                    item1.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tlbLandCover.setItem(row, 0, QTableWidgetItem(item1))

                    item2 = QtGui.QTableWidgetItem(artikel['UserLandCover'])
                    item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tlbLandCover.setItem(row, 1, QTableWidgetItem(item2))

                    item3 = QtGui.QTableWidgetItem(artikel['GRMCode'])
                    item3.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tlbLandCover.setItem(row, 2, QTableWidgetItem(item3))

                    item4 = QtGui.QTableWidgetItem(artikel['GRMLandCoverE'])
                    item4.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tlbLandCover.setItem(row, 3, QTableWidgetItem(item4))

                    item5 = QtGui.QTableWidgetItem(artikel['GRMLandCoverK'])
                    item5.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tlbLandCover.setItem(row, 4, QTableWidgetItem(item5))

                    self.tlbLandCover.setItem(row, 5, QTableWidgetItem(artikel['RoughnessCoefficient']))
                    self.tlbLandCover.setItem(row, 6, QTableWidgetItem(artikel['ImperviousRatio']))
                    row = row + 1
            elif GRM._LandCoverCount ==1:
                    self.tlbLandCover.insertRow(0)

                    item1 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['LandCover']['GridValue'])
                    item1.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tlbLandCover.setItem(row, 0, QTableWidgetItem(item1))

                    item2 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['LandCover']['UserLandCover'])
                    item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tlbLandCover.setItem(row, 1, QTableWidgetItem(item2))

                    item3 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['LandCover']['GRMCode'])
                    item3.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tlbLandCover.setItem(row, 2, QTableWidgetItem(item3))

                    item4 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['LandCover']['GRMLandCoverE'])
                    item4.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tlbLandCover.setItem(row, 3, QTableWidgetItem(item4))

                    item5 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['LandCover']['GRMLandCoverK'])
                    item5.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tlbLandCover.setItem(row, 4, QTableWidgetItem(item5))

                    self.tlbLandCover.setItem(row, 5, QTableWidgetItem(GRM._xmltodict['GRMProject']['LandCover']['RoughnessCoefficient']))
                    self.tlbLandCover.setItem(row, 6, QTableWidgetItem(GRM._xmltodict['GRMProject']['LandCover']['ImperviousRatio']))

        except KeyError:
#             _util.MessageboxShowError("except False","False")
            self.Get_ComboBox_LayerPath(self.cmbLandCover, self.tlbLandCover, self.txtLandCover, "LandCover")
#         else:
#             _util.MessageboxShowError("else False", "False")


    def SetGreenAmptTalbe(self):
        try:
            # 프로젝트 파일에서 불러온 데이터 테이블에 셋팅
            if GRM._GreenAmptCount >1:
                row = 0
                for artikel in GRM._xmltodict['GRMProject']['GreenAmptParameter']:
                    self.tblGreenAmpt.insertRow(row)

                    item1 = QtGui.QTableWidgetItem(artikel['GridValue'])
                    item1.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblGreenAmpt.setItem(row, 0, QTableWidgetItem(item1))

                    item2 = QtGui.QTableWidgetItem(artikel['USERSoil'])
                    item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblGreenAmpt.setItem(row, 1, QTableWidgetItem(item2))

                    item3 = QtGui.QTableWidgetItem(artikel['GRMCode'])
                    item3.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblGreenAmpt.setItem(row, 2, QTableWidgetItem(item3))

                    item4 = QtGui.QTableWidgetItem(artikel['GRMTextureE'])
                    item4.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblGreenAmpt.setItem(row, 3, QTableWidgetItem(item4))

                    item5 = QtGui.QTableWidgetItem(artikel['GRMTextureK'])
                    item5.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblGreenAmpt.setItem(row, 4, QTableWidgetItem(item4))

                    self.tblGreenAmpt.setItem(row, 5, QTableWidgetItem(artikel['Porosity']))
                    self.tblGreenAmpt.setItem(row, 6, QTableWidgetItem(artikel['EffectivePorosity']))
                    self.tblGreenAmpt.setItem(row, 7, QTableWidgetItem(artikel['WFSoilSuctionHead']))
                    self.tblGreenAmpt.setItem(row, 8, QTableWidgetItem(artikel['HydraulicConductivity']))
                    row = row + 1
            elif GRM._GreenAmptCount ==1:
                    self.tblGreenAmpt.insertRow(0)

                    item1 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['GreenAmptParameter']['GridValue'])
                    item1.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblGreenAmpt.setItem(row, 0, QTableWidgetItem(item1))

                    item2 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['GreenAmptParameter']['USERSoil'])
                    item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblGreenAmpt.setItem(row, 1, QTableWidgetItem(item2))

                    item3 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['GreenAmptParameter']['GRMCode'])
                    item3.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblGreenAmpt.setItem(row, 2, QTableWidgetItem(item3))

                    item4 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['GreenAmptParameter']['GRMTextureE'])
                    item4.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblGreenAmpt.setItem(row, 3, QTableWidgetItem(item4))

                    item5 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['GreenAmptParameter']['GRMTextureK'])
                    item5.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblGreenAmpt.setItem(row, 4, QTableWidgetItem(item5))

                    self.tblGreenAmpt.setItem(row, 5, QTableWidgetItem(GRM._xmltodict['GRMProject']['GreenAmptParameter']['Porosity']))
                    self.tblGreenAmpt.setItem(row, 6, QTableWidgetItem(GRM._xmltodict['GRMProject']['GreenAmptParameter']['EffectivePorosity']))
                    self.tblGreenAmpt.setItem(row, 7, QTableWidgetItem(GRM._xmltodict['GRMProject']['GreenAmptParameter']['WFSoilSuctionHead']))
                    self.tblGreenAmpt.setItem(row, 8, QTableWidgetItem(GRM._xmltodict['GRMProject']['GreenAmptParameter']['HydraulicConductivity']))

        except KeyError:
#             _util.MessageboxShowError("except False", "False")
            self.Get_ComboBox_LayerPath(self.cmbSoilTexture, self.tblGreenAmpt, self.txtSoilTexture,"GreenAmpt")
#         else:
#             _util.MessageboxShowError("else False", "False")


    def SetSoilDepthTalbe(self):
        try:

            # 프로젝트 파일에서 불러온 데이터 테이블에 셋팅
            if GRM._SoilDepthCount > 1:
                row = 0
                for artikel in GRM._xmltodict['GRMProject']['SoilDepth']:
                    self.tblSoilDepth.insertRow(row)

                    item1 = QtGui.QTableWidgetItem(artikel['GridValue'])
                    item1.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblSoilDepth.setItem(row, 0, QTableWidgetItem(item1))

                    item2 = QtGui.QTableWidgetItem(artikel['UserDepthClass'])
                    item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblSoilDepth.setItem(row, 1, QTableWidgetItem(item2))

                    item3 = QtGui.QTableWidgetItem(artikel['GRMCode'])
                    item3.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblSoilDepth.setItem(row, 2, QTableWidgetItem(item3))

                    item4 = QtGui.QTableWidgetItem(artikel['SoilDepthClassE'])
                    item4.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblSoilDepth.setItem(row, 3, QTableWidgetItem(item4))

                    item5 = QtGui.QTableWidgetItem(artikel['SoilDepthClassK'])
                    item5.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblSoilDepth.setItem(row, 4, QTableWidgetItem(item5))

                    self.tblSoilDepth.setItem(row, 5, QTableWidgetItem(artikel['SoilDepth']))
                    row = row + 1
            elif  GRM._SoilDepthCount == 1:
                    self.tblSoilDepth.insertRow(0)

                    item1 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['SoilDepth']['GridValue'])
                    item1.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblSoilDepth.setItem(row, 0, QTableWidgetItem(item1))

                    item2 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['SoilDepth']['UserDepthClass'])
                    item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblSoilDepth.setItem(row, 1, QTableWidgetItem(item2))

                    item3 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['SoilDepth']['GRMCode'])
                    item3.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblSoilDepth.setItem(row, 2, QTableWidgetItem(item3))

                    item4 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['SoilDepth']['SoilDepthClassE'])
                    item4.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblSoilDepth.setItem(row, 3, QTableWidgetItem(item4))

                    item5 = QtGui.QTableWidgetItem(GRM._xmltodict['GRMProject']['SoilDepth']['SoilDepthClassK'])
                    item5.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tblSoilDepth.setItem(row, 4, QTableWidgetItem(item5))

                    self.tblSoilDepth.setItem(row, 5, QTableWidgetItem(GRM._xmltodict['GRMProject']['SoilDepth']['SoilDepth']))

        except KeyError:
#             _util.MessageboxShowError("except False", "False")
            self.Get_ComboBox_LayerPath(self.cmbSoilDepth, self.tblSoilDepth, self.txtSoilDepth, "SoilDepth")
#         else:
#             _util.MessageboxShowError("else False", "False")







    #
    #
    #
    # def InitControl(self):
    #
    #
    #
    #
    #     # # 파일 형식이 파일이면 레이어 목록중 한개의 파일(LandCoverVATFile)
    #     # if self.LandCoverType == "Layer":
    #     #     # 라디오 버튼 초기 설정
    #     #     self.LCLaye_CheckedChanged()
    #     #     self.rbtUseLCLayer.setChecked(True)
    #     #     self.txtLandCover.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverVATFile'])
    #     #
    #     #     # layer 콤보 박스 항목을 프로젝트 파일의 데이터 내용에 해당되는 콤보 박스 항목으로 셋팅
    #     #     LandCoverFile = GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverFile']
    #     #     if self.txtLandCover.text() != "":
    #     #         LandCoverName = self.GetFilename(LandCoverFile)
    #     #         self.Setcombobox(self.cmbLandCover, LandCoverName, LandCoverFile)
    #     #         # 테이블에 VAT 파일 내용을 셋팅
    #     #         self.SetVATValue(self.txtLandCover.text(), self.tlbLandCover, "LandCover")
    #     # elif self.LandCoverType == "Constant":
    #     #     self.rbtUseConstLCAtt.setChecked(True)
    #     #     self.ConstLCAtt_CheckedChanged()
    #     #     self.txtCoefficient.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantRoughnessCoeff'])
    #     #     self.txtImpervious.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantImperviousRatio'])
    #     # else:
    #     #     self.rbtUseConstLCAtt.setChecked(True)
    #     #     self.ConstLCAtt_CheckedChanged()
    #     #
    #     # # 파일 형식이 파일이면 레이어 목록중 한개의 파일(SoilTextureVATFile)
    #     # if self.SoilTextureType == "Layer":
    #     #     self.rbtUseSoilTextureLayer.setChecked(True)
    #     #     self.SoilTextureLayer_CheckedChanged()
    #     #     # 텍스트 박스에 VAT 파일 경로 넣기
    #     #     self.txtSoilTexture.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureVATFile'])
    #     #
    #     #     # layer 콤보 박스 항목을 프로젝트 파일의 데이터 내용에 해당되는 콤보 박스 항목으로 셋팅
    #     #     SoilTextureFile = GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureFile']
    #     #     if SoilTextureFile != "":
    #     #         SoilTextureName = self.GetFilename(SoilTextureFile)
    #     #         self.Setcombobox(self.cmbSoilTexture, SoilTextureName, SoilTextureFile)
    #     #         # 테이블에 VAT 파일 내용을 셋팅
    #     #         self.SetVATValue(self.txtSoilTexture.text(), self.tblGreenAmpt, "GreenAmpt")
    #     #
    #     # elif self.LandCoverType == "Constant":
    #     #     self.rbtUseConstTextureAtt.setChecked(True)
    #     #     self.TextureAtt_CheckedChanged()
    #     #     self.txtPorosity.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilPorosity'])
    #     #     self.txtEffective_porosity.setText(
    #     #         GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilEffPorosity'])
    #     #     self.txtSuction_head.setText(
    #     #         GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilWettingFrontSuctionHead'])
    #     #     self.txtConductiovity.setText(
    #     #         GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilHydraulicConductivity'])
    #     # else:
    #     #     self.rbtUseConstTextureAtt.setChecked(True)
    #     #     self.TextureAtt_CheckedChanged()
    #     #
    #     # # 파일 형식이 파일이면 레이어 목록중 한개의 파일(SoilDepthVATFile)
    #     # if self.SoilDepthType == "Layer":
    #     #     self.rbtUseSoilDepthLayer.setChecked(True)
    #     #     self.SoilDepthLayer_CheckedChanged()
    #     #     # 텍스트 박스에 VAT 파일 경로 넣기
    #     #     self.txtSoilDepth.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthVATFile'])
    #     #
    #     #     # layer 콤보 박스 항목을 프로젝트 파일의 데이터 내용에 해당되는 콤보 박스 항목으로 셋팅
    #     #     SoilDepthFile = GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthFile']
    #     #     if SoilDepthFile != "":
    #     #         SoilDepthName = self.GetFilename(SoilDepthFile)
    #     #         self.Setcombobox(self.cmbSoilDepth, SoilDepthName, SoilDepthFile)
    #     #         # 테이블에 VAT 파일 내용을 셋팅
    #     #         self.SetVATValue(self.txtSoilDepth.text(), self.tblSoilDepth, "SoilDepth")
    #     # elif self.LandCoverType == "Constant":
    #     #     self.rbtUseConstDepth.setChecked(True)
    #     #     self.ConstDepth_CheckedChanged()
    #     #     self.txtSoil_depth.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilDepth'])
    #     # else:
    #     #     self.rbtUseConstDepth.setChecked(True)
    #     #     self.ConstDepth_CheckedChanged()
    #
    #     # table header set(메이창 테이블 타이틀 설정)
    #     self.tlbLandCover.setColumnCount(7)
    #     self.tlbLandCover.setHorizontalHeaderLabels(
    #         ['GridValue', 'UserLandCover', 'GRMCode', 'LandCoverE', 'LandCoverK', 'RoughnessCoefficient',
    #          'ImperviousRatio'])
    #
    #     self.tblGreenAmpt.setColumnCount(9)
    #     self.tblGreenAmpt.setHorizontalHeaderLabels(
    #         ['GridValue', 'USERSoil', 'GRMCode', 'GRMTextureE', 'GRMTextureK', 'Porosity', 'EffectivePorosity',
    #          'WFSoilSuctionHead', 'HydraulicConductivity'])
    #
    #     self.tblSoilDepth.setColumnCount(6)
    #     self.tblSoilDepth.setHorizontalHeaderLabels(
    #         ['GridValue', 'UserDepthClass', 'GRMDepthCode', 'SoilDepthClassE', 'SoilDepthClassK', 'SoilDepth'])



    # 콤보 박스에서 선택한 레이어의 경로 받아오기, 받아온 경로에 한글이 있으면 메시지 창 출력
    def Get_ComboBox_LayerPath(self,combox,table,txt,type):
        if combox.currentIndex() != 0:
            self.layerPath = _util.GetcomboSelectedLayerPath(combox).replace(".asc", ".vat").replace(".tif", ".vat")

        # 선택된 레이어 한글 경로 있는지 확인
        if _util.CheckKorea(self.layerPath):
            combox.setCurrentIndex(0)
            _util.MessageboxShowInfo("Land Cover / Soil", "\n The selected layer contains Korean paths. \n")

        if _util.CheckFile(self.layerPath):
            txt.setText(str(self.layerPath))
            
            self.SetVATValue(self.layerPath, table, type)
    #
    #
    #
    #
    #
    #
    #
    #
    #     #
    #     #
    #     # # 프로그래 구동에 시간이 걸리므로 마우스 커서 변경
    #     # QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
    #     #
    #     # # 컨트롤들 모두 초기 셋팅(각각의 테이블 타이틀 및 값 셋팅) , 콤보 박스 레이어 목록 올리기
    #     # self.InitControl()
    #     #
    #     # # 콤보 박스에 프로젝트 파일에 적용된 레이어 목록이 선택 되어 시작 되도록 셋팅
    #     # self.SetProjectToCombox()
    #     #
    #     #
    #     # # 프로그램 실행시 프로젝트 파일에 적용된 VAT 파일로 테이블 채우기
    #     # self.SetVatFile()
    #     #
    #
    #     # # 모든 작업 완료후 마우스 커서 본래로 변경
    #     # QApplication.setOverrideCursor(QCursor(QtCore.Qt.ArrowCursor))
    #     #
    #
    #
    #
    def closeForm(self):
        self.close()  # 폼 종료

    def OKForm(self):



        # 라디오 버튼이 전부 왼쪽으로 눌려 있을 때
        # if self.rbtUseLCLayer.isChecked() and self.rbtUseSoilTextureLayer.isChecked() and self.rbtUseSoilDepthLayer.isChecked():
        #     _util.MessageboxShowInfo("GRM", "Land covers and soil attributes setup are completed.")
        #

        # 1. 라디오 rbtUseConstLCAtt
        if self.rbtUseConstLCAtt.isChecked():
            if True:
                if self.Checktxtbox(self.txtCoefficient):
                    if float(self.txtCoefficient.text()) < 0.0015 or 1.5 < float(self.txtCoefficient.text()):
                        _util.MessageboxShowError("GRM", "{0}\n{1}".format(
                            "[Land cover roughness coefficient] is invalid.",
                            "0.0015<=Land cover roughness coefficient<=to1.5"))
                        self.txtCoefficient.setFocus()
                        return
                else:
                    _util.MessageboxShowError("GRM", "{0}\n{1}".format(
                        "[Land cover roughness coefficient] is invalid.",
                        "0.0015<=Land cover roughness coefficient<=to1.5"))
                    self.txtCoefficient.setFocus()
                    return

                if self.Checktxtbox(self.txtImpervious):
                    if float(self.txtImpervious.text()) < 0 or 1 < float(self.txtImpervious.text()):
                        _util.MessageboxShowError("GRM", "[Impervious ratio] is invalid. \n0<=Impervious ration<=1")
                        self.txtImpervious.setFocus()
                        return
                else:
                    _util.MessageboxShowError("GRM", "[Impervious ratio] is invalid. \n0<=Impervious ration<=1")
                    self.txtImpervious.setFocus()
                    return

        # 2. rbtUseConstTextureAtt 선택 시,
        if self.rbtUseConstTextureAtt.isChecked():
            #             if self.txtPorosity.text().isnumeric() and self.txtPorosity.text() !="" :
            if True:
                if self.Checktxtbox(self.txtPorosity):
                    if float(self.txtPorosity.text()) < 0 or 1 < float(self.txtPorosity.text()):
                        _util.MessageboxShowError("GRM", "[Porosity] is invalid. \n0<=Porosity<=1")
                        self.txtPorosity.setFocus()
                        return
                else:
                    _util.MessageboxShowError("GRM", "[Porosity] is invalid. \n0<=Porosity<=1")
                    self.txtPorosity.setFocus()
                    return

                if (self.Checktxtbox(self.txtEffective_porosity)):
                    if float(self.txtEffective_porosity.text()) < 0 or 1 < float(self.txtEffective_porosity.text()):
                        _util.MessageboxShowError("GRM",
                                                  '[Effective poropsity] is invalid. \n0<=Effective porosity<=1')
                        self.txtEffective_porosity.setFocus()
                        return
                else:
                    _util.MessageboxShowError("GRM", '[Effective poropsity] is invalid. \n0<=Effective porosity<=1')
                    return

                if (self.Checktxtbox(self.txtSuction_head)):
                    if float(self.txtSuction_head.text()) < 0 or 9999 < float(self.txtSuction_head.text()):
                        _util.MessageboxShowError("GRM",
                                                  '[Wetting front suction head] is invalid. \n0<=Wetting front suction head<=9999')
                        self.txtSuction_head.setFocus()
                        return
                else:
                    _util.MessageboxShowError("GRM",
                                              '[Wetting front suction head] is invalid. \n0<=Wetting front suction head<=9999')
                    self.txtSuction_head.setFocus()
                    return

                if (self.Checktxtbox(self.txtConductiovity)):
                    if float(self.txtConductiovity.text()) < 0 or 1 < float(self.txtConductiovity.text()):
                        _util.MessageboxShowError("GRM",'[Hydraulic conductivity] is invalid. \n0<=Hydraulic conductivity<=1')
                        self.txtConductiovity.setFocus()
                        return
                else:
                    _util.MessageboxShowError("GRM",'[Hydraulic conductivity] is invalid. \n0<=Hydraulic conductivity<=1')
                    self.txtConductiovity.setFocus()
                    # 문제되는 곳에 focus
                    return

        # 3.rbtUseConstDepth 체크
        if self.rbtUseConstDepth.isChecked():
            if True:
                if self.Checktxtbox(self.txtSoil_depth):
                    if float(self.txtSoil_depth.text()) < 0 or 9999 < float(self.txtSoil_depth.text()):
                        _util.MessageboxShowError("GRM", "[Soil Depth] is invalid.\n0<=Soil Depth<=9999")
                        self.txtSoil_depth.setFocus()
                        return
                else:
                    _util.MessageboxShowError("GRM", "[Soil Depth] is invalid.\n0<=Soil Depth<=9999")
                    self.txtSoil_depth.setFocus()
                    return
        # GMP 파일에 Lanccover,depth.. xml 생성
        self.DataSave()
        # _util.MessageboxShowInfo("Land cover / soil", "Land covers and soil attributes setup are completed.")

        quit_msg = " Land covers and soil attributes setup are completed.   "
        reply = QtGui.QMessageBox.information(self, 'Land cover / soil', quit_msg, QtGui.QMessageBox.Ok)
        if reply == QtGui.QMessageBox.Ok:
            self.close()

    # QlineEdit 값 체크
    def Checktxtbox(self, textbox):
        if textbox.text() != "" and textbox.text().isnumeric():
            return textbox.text()
        else:
            return False
    # 2017/10/11 CHO 여기까지----






    def DataSave(self):
        #  타입 설정
        if self.rbtUseSoilTextureLayer.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverDataType'] ="File"
            LandCoverLayerPath = _util.GetcomboSelectedLayerPath(self.cmbLandCover)
            GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverFile'] =LandCoverLayerPath
            GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverVATFile'] = self.txtLandCover.text()
            # Landcover table 데이터 저장
            self.dataSeve_Landcover()
        else :
            GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverDataType'] = "Constant"
            GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantRoughnessCoeff'] = self.txtCoefficient.text()
            GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantImperviousRatio'] = self.txtImpervious.text()


        #  타입 설정
        if self.rbtUseSoilTextureLayer.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureDataType'] ="File"
            SoilTextureLayerPath = _util.GetcomboSelectedLayerPath(self.cmbSoilTexture)
            GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureFile'] =SoilTextureLayerPath
            GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureVATFile']=self.txtSoilTexture.text()
            self.dataSeve_SoilTexture()
        else :
            GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureDataType'] = "Constant"
            GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilPorosity'] = self.txtPorosity.text()
            GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilEffPorosity'] = self.txtEffective_porosity.text()
            GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilWettingFrontSuctionHead'] = self.txtSuction_head.text()
            GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilHydraulicConductivity'] = self.txtConductiovity.text()

        #  타입 설정
        if self.rbtUseSoilDepthLayer.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthDataType'] ="File"
            SoilDepthLayerPath = _util.GetcomboSelectedLayerPath(self.cmbSoilDepth)
            GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthFile']  = SoilDepthLayerPath
            GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthVATFile'] = self.txtSoilDepth.text()
            self.dataSeve_SoilDepth()
        else :
            GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthDataType'] = "Constant"
            GRM._xmltodict['GRMProject']['ProjectSettings']['ConstantSoilDepth'] = self.txtSoil_depth.text()


    def dataSeve_Landcover(self):
        try:
            # dictionary 에서 LandCover 항목을 모두 제거
            check = GRM._xmltodict['GRMProject']['LandCover']
            if check is not None:
                del GRM._xmltodict['GRMProject']['LandCover']
        except:
            pass


        # dictionary 에서 엘레먼트 생성이 안되서 dic===> XML (element 생성 ) ===> dictionary 변환
        DictoXml = xmltodict.unparse(GRM._xmltodict)
        ET.register_namespace('', "http://tempuri.org/GRMProject.xsd")
        xmltree = ET.ElementTree(ET.fromstring(DictoXml))
        root = xmltree.getroot()
        count =self.tlbLandCover.rowCount()
        GRM._LandCoverCount = count

        for row in range(0, count):
            child = ET.Element("LandCover")
            root.append(child)

            GridValue = ET.Element("GridValue")
            GridValue.text = self.tlbLandCover.item(row, 0).text()
            child.append(GridValue)

            UserLandCover = ET.Element("UserLandCover")
            UserLandCover.text = self.tlbLandCover.item(row, 1).text()
            child.append(UserLandCover)

#             GRMLandCoverCode = ET.Element("GRMLandCoverCode")
            GRMLandCoverCode = ET.Element("GRMCode")
            GRMLandCoverCode.text = self.tlbLandCover.item(row, 2).text()
            child.append(GRMLandCoverCode)

            GRMLandCoverE = ET.Element("GRMLandCoverE")
            GRMLandCoverE.text = self.tlbLandCover.item(row, 3).text()
            child.append(GRMLandCoverE)

            GRMLandCoverK = ET.Element("GRMLandCoverK")
            GRMLandCoverK.text = self.tlbLandCover.item(row, 4).text()
            child.append(GRMLandCoverK)

            RoughnessCoefficient = ET.Element("RoughnessCoefficient")
            RoughnessCoefficient.text = self.tlbLandCover.item(row, 5).text()
            child.append(RoughnessCoefficient)

            ImperviousRatio = ET.Element("ImperviousRatio")
            ImperviousRatio.text = self.tlbLandCover.item(row, 6).text()
            child.append(ImperviousRatio)


        filepath = tempfile.mktemp()
        xmltree.write(filepath)

        # Dictionary 초기화
        GRM._xmltodict.clear()

        # 파일 읽어 오기
        Projectfile = open(filepath, 'r')
        data = Projectfile.read()
        Projectfile.close()
        # 읽어온 파일 내용(XML)을 dictionary 로 변경
        docs = dict(xmltodict.parse(data))
        GRM._xmltodict.update(docs)



    def dataSeve_SoilTexture(self):
        # dictionary 에서 GreenAmptParameter 항목을 모두 제거
        try:
            # dictionary 에서 LandCover 항목을 모두 제거
            check = GRM._xmltodict['GRMProject']['GreenAmptParameter']
            if check is not None:
                del GRM._xmltodict['GRMProject']['GreenAmptParameter']
        except:
            pass

        # dictionary 에서 엘레먼트 생성이 안되서 dic===> XML (element 생성 ) ===> dictionary 변환
        DictoXml = xmltodict.unparse(GRM._xmltodict)
        ET.register_namespace('', "http://tempuri.org/GRMProject.xsd")
        xmltree = ET.ElementTree(ET.fromstring(DictoXml))
        root = xmltree.getroot()
        count = self.tblGreenAmpt.rowCount()
        GRM._GreenAmptCount = count
        for row in range(0, count):
            child = ET.Element("GreenAmptParameter")
            root.append(child)

            GridValue = ET.Element("GridValue")
            GridValue.text = self.tblGreenAmpt.item(row, 0).text()
            child.append(GridValue)

            USERSoil = ET.Element("USERSoil")
            USERSoil.text = self.tblGreenAmpt.item(row, 1).text()
            child.append(USERSoil)

            GRMCode = ET.Element("GRMCode")
            GRMCode.text = self.tblGreenAmpt.item(row, 2).text()
            child.append(GRMCode)

            GRMTextureE = ET.Element("GRMTextureE")
            GRMTextureE.text = self.tblGreenAmpt.item(row, 3).text()
            child.append(GRMTextureE)

            GRMTextureK = ET.Element("GRMTextureK")
            GRMTextureK.text = self.tblGreenAmpt.item(row, 4).text()
            child.append(GRMTextureK)

            Porosity = ET.Element("Porosity")
            Porosity.text = self.tblGreenAmpt.item(row, 5).text()
            child.append(Porosity)

            EffectivePorosity = ET.Element("EffectivePorosity")
            EffectivePorosity.text = self.tblGreenAmpt.item(row, 6).text()
            child.append(EffectivePorosity)

            WFSoilSuctionHead = ET.Element("WFSoilSuctionHead")
            WFSoilSuctionHead.text = self.tblGreenAmpt.item(row, 7).text()
            child.append(WFSoilSuctionHead)

            HydraulicConductivity = ET.Element("HydraulicConductivity")
            HydraulicConductivity.text = self.tblGreenAmpt.item(row, 8).text()
            child.append(HydraulicConductivity)

        # xmltree.write("C:\Users\hermesys\Desktop\Sct2.gmp")
        filepath = tempfile.mktemp()
        xmltree.write(filepath)

        # Dictionary 초기화
        GRM._xmltodict.clear()

        # 파일 읽어 오기
        Projectfile = open(filepath, 'r')
        data = Projectfile.read()
        Projectfile.close()
        # 읽어온 파일 내용(XML)을 dictionary 로 변경
        docs = dict(xmltodict.parse(data))
        GRM._xmltodict.update(docs)


    def dataSeve_SoilDepth(self):
        # dictionary 에서 GreenAmptParameter 항목을 모두 제거
        try:
            check = GRM._xmltodict['GRMProject']['SoilDepth']
            if check is not None:
                del GRM._xmltodict['GRMProject']['SoilDepth']
        except:
            pass

        # dictionary 에서 엘레먼트 생성이 안되서 dic===> XML (element 생성 ) ===> dictionary 변환
        DictoXml = xmltodict.unparse(GRM._xmltodict)
        ET.register_namespace('', "http://tempuri.org/GRMProject.xsd")
        xmltree = ET.ElementTree(ET.fromstring(DictoXml))
        root = xmltree.getroot()
        count = self.tblSoilDepth.rowCount()
        GRM._SoilDepthCount = count
        for row in range(0, count):
            child = ET.Element("SoilDepth")
            root.append(child)

            GridValue = ET.Element("GridValue")
            GridValue.text = self.tblSoilDepth.item(row, 0).text()
            child.append(GridValue)

            UserDepthClass = ET.Element("UserDepthClass")
            UserDepthClass.text = self.tblSoilDepth.item(row, 1).text()
            child.append(UserDepthClass)

            GRMDepthCode = ET.Element("GRMCode")
            GRMDepthCode.text = self.tblSoilDepth.item(row, 2).text()
            child.append(GRMDepthCode)

            SoilDepthClassE = ET.Element("SoilDepthClassE")
            SoilDepthClassE.text = self.tblSoilDepth.item(row, 3).text()
            child.append(SoilDepthClassE)

            SoilDepthClassK = ET.Element("SoilDepthClassK")
            SoilDepthClassK.text = self.tblSoilDepth.item(row, 4).text()
            child.append(SoilDepthClassK)

            SoilDepth = ET.Element("SoilDepth")
            SoilDepth.text = self.tblSoilDepth.item(row, 5).text()
            child.append(SoilDepth)

        # xmltree.write("C:\Users\hermesys\Desktop\Sct2.gmp")
        filepath = tempfile.mktemp()
        xmltree.write(filepath)

        # Dictionary 초기화
        GRM._xmltodict.clear()

        # 파일 읽어 오기
        Projectfile = open(filepath, 'r')
        data = Projectfile.read()
        Projectfile.close()
        # 읽어온 파일 내용(XML)을 dictionary 로 변경
        docs = dict(xmltodict.parse(data))
        GRM._xmltodict.update(docs)





            # def SetProjectToCombox(self):
    #     LandCoverFile = GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverFile']
    #     SoilTextureFile = GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureFile']
    #     SoilDepthFile = GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthFile']
    #
    #     if LandCoverFile != "":
    #         LandCoverName = self.GetFilename(LandCoverFile)
    #         self.Setcombobox(self.cmbLandCover, LandCoverName, LandCoverFile)
    #
    #     # 프로젝트 파일에 문제가 있는건지 잘 되지 않음 추후에 확인 의심이 많이감
    #     if SoilTextureFile != "":
    #         SoilTextureName = self.GetFilename(SoilTextureFile)
    #         self.Setcombobox(self.cmbSoilTexture, SoilTextureName, SoilTextureFile)
    #
    #
    #     if SoilDepthFile != "":
    #         SoilDepthName = self.GetFilename(SoilDepthFile)
    #         self.Setcombobox(self.cmbSoilDepth, SoilDepthName, SoilDepthFile)


    # 콤보 박스에 있는 목록중에 프로젝트 상에 있는 레이어 비교 하여 있으면 콤보박스에 선택
    def Setcombobox(self,commboxs,layername,filepath):
        index = commboxs.findText(str(layername))
        if _util.GetTxtToLayerPath(layername) == filepath :
            if index >= 0:
                commboxs.setCurrentIndex(index)


    # 파일 경로 중에 파일명만 받아 오기
    def GetFilename(self, filename):
        s = os.path.splitext(filename)
        s = os.path.split(s[0])
        return s[1]


    # 사용자가 VAT 파일 바꿀때 테이블 값도 바뀌어서 적용
    def SelectVat(self,button,txtbox):
        dir = os.path.dirname(txtbox.text())
        filename = QFileDialog.getOpenFileName(self, "select output file ", dir, "*.vat")
        txtbox.clear()
        txtbox.setText(filename)
        if button=="btnVatLand":
            self.SetVATValue(self.txtLandCover.text(), self.tlbLandCover,"LandCover")
        elif button=="btnVatAmpt":
            self.SetVATValue(self.txtSoilTexture.text(), self.tblGreenAmpt,"GreenAmpt")
        elif button == "btnVatDepth":
            self.SetVATValue(self.txtSoilDepth.text(), self.tblSoilDepth,"SoilDepth")


    # 프로그램 실행시 프로젝트 파일에 적용된 VAT 파일로 테이블 채우기
    def SetVatFile(self):
        self.txtLandCover.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverVATFile'])
        self.txtSoilTexture.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureVATFile'])
        self.txtSoilDepth.setText(GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthVATFile'])

        if self.LandCoverType !=""  and self.LandCoverType == "Layer":
            self.SetVATValue(self.txtLandCover.text(), self.tlbLandCover,"LandCover")

        if self.SoilTextureType != "" and self.SoilTextureType == "Layer":
            self.SetVATValue(self.txtSoilTexture.text(),self.tblGreenAmpt,"GreenAmpt")

        if self.SoilDepthType != "" and self.SoilDepthType=="Layer":
            self.SetVATValue(self.txtSoilDepth.text(),self.tblSoilDepth,"SoilDepth")

    # Vat 파일에서 읽어 와서 테이블에 값셋팅 하기
    def SetVATValue(self,path,table,type):
        with open(path) as fp:
            lines = fp.read().split("\n")
            
        # 테이블 초기화
        table.clear()
        if type == "LandCover":
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(['GridValue', 'UserLandCover', 'GRMCode', 'LandCoverE', 'LandCoverK', 'RoughnessCoefficient','ImperviousRatio'])
        elif type == "GreenAmpt":
            table.setColumnCount(9)
            table.setHorizontalHeaderLabels(['GridValue', 'USERSoil', 'GRMCode', 'GRMTextureE', 'GRMTextureK', 'Porosity', 'EffectivePorosity','WFSoilSuctionHead', 'HydraulicConductivity'])
        elif type == "SoilDepth":
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(['GridValue', 'UserDepthClass', 'GRMCode', 'SoilDepthClassE', 'SoilDepthClassK', 'SoilDepth'])
#
        table.setRowCount(int(lines[0]))
        
        try:
            # Table에 데이터 값 대입
            for i in range(1, len(lines)):
                splitsdata = lines[i].split(",")
                table.setItem(i - 1, 0, QTableWidgetItem(splitsdata[0].decode('cp949')))
                table.setItem(i - 1, 1, QTableWidgetItem(splitsdata[1].decode('cp949')))
                
                #이 함수가 문제가 있음.. 2017/11/28
                #From 박 : staticDB는 임시로 넣어서 사용
                #VAT 파일 안에 띄어쓰기가 있는 경우 값을 완전 다른 값으로 받아들여서 strip()으로 띄어쓰기 제거함
                self.SetMainTableValue(splitsdata[1].decode('cp949').strip(),table,(i-1),type)
        except:
#             _util.MessageboxShowError("No GRM Static DB","No GRM Static DB")

            for i in range(1, len(lines)):
                splitsdata = lines[i].split(",")
                table.setItem(i - 1, 0, QTableWidgetItem(splitsdata[0].decode('cp949')))
                table.setItem(i - 1, 1, QTableWidgetItem(splitsdata[1].decode('cp949')))
            

    # 메인창 Land cover tablewidget 테이블에 데이터 셋팅 (3~ 이후 컬럼의 데이터 값을 StaticDB 셋팅)
    def SetMainTableValue(self, value, widget, row, type):
        path = _util.StaticDB

        # _util.MessageboxShowError("path",path)
        doc = ET.parse(path)
        root = doc.getroot()
        if type == "LandCover":
            for element in root.findall("{http://tempuri.org/DataSet1.xsd}LandCoverParameter"):
                if element.findtext("{http://tempuri.org/DataSet1.xsd}LandCoverK") == value :
                    widget.setItem(row, 2, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}LandCoverCode")))
                    widget.setItem(row, 3, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}LandCoverE")))
                    widget.setItem(row, 4, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}LandCoverK")))
                    widget.setItem(row, 5, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}RoughnessCoefficient")))
                    widget.setItem(row, 6, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}ImperviousRatio")))
                    break                    

        elif type == "GreenAmpt":
            for element in root.findall("{http://tempuri.org/DataSet1.xsd}GreenAmptSoilParameter"):
                if element.findtext("{http://tempuri.org/DataSet1.xsd}SoilTextureK") == value :
                    widget.setItem(row, 2, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}SoilTextureCode")))
                    widget.setItem(row, 3, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}SoilTextureE")))
                    widget.setItem(row, 4, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}SoilTextureK")))
                    widget.setItem(row, 5, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}PorosityDefault")))
                    widget.setItem(row, 6, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}EffectivePorosityDefault")))
                    widget.setItem(row, 7, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}WFSoilSuctionHeadDefault")))
                    widget.setItem(row, 8, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}HydraulicConductivity")))
                    break
        elif type == "SoilDepth":
            for element in root.findall("{http://tempuri.org/DataSet1.xsd}SoilDepthParameter"):
                if element.findtext("{http://tempuri.org/DataSet1.xsd}SoilDepthClassK") == value :
                    widget.setItem(row, 2,
                                   QTableWidgetItem(element.findtext("{http://tempuri.org/DataSet1.xsd}GRMCode")))
                    widget.setItem(row, 3, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}SoilDepthClassE")))
                    widget.setItem(row, 4, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}SoilDepthClassK")))
                    widget.setItem(row, 5, QTableWidgetItem(
                        element.findtext("{http://tempuri.org/DataSet1.xsd}SoilDepthDefault")))
                    break

    # # Qdilog 창에 Qtablewidget 셋팅
    def aboutApp(self, type,row):
        global _SelectRow
        _SelectRow= row
        website = "http://code.google.com/p/comictagger"
        email = "comictagger@gmail.com"
        license_link = "http://www.apache.org/licenses/LICENSE-2.0"
        license_name = "Apache License 2.0"
        Project = "test"
        msgBox = QtGui.QMessageBox()

        msgBox.setWindowTitle(self.tr("Select Attribute"))

        msgBox.setTextFormat(QtCore.Qt.RichText)

        msgBox.setIconPixmap(QtGui.QPixmap(Project))

        msgBox.setText("<br><br><br><br><br><br><br><br><br><br><br>" +
                       "<font color=white>" +
                       "{0},{1},{2}</font>".format(website, email, license_name))

        # msgBox.setText("<br><br><br>" + "test" +
        #                " v" +
        #                "1.1" +
        #                "&copy;2014 Anthony Beville" +
        #                "<a href='{0}'>{0}</a>".format(website) +
        #                "<a href='mailto:{0}'>{0}</a>".format(email) + "License: <a href='{0}'>{1}</a>".format(
        #     license_link, license_name) +
        #                "<a href='mailto:{0}'>{0}</a>".format(email) + "License: <a href='{0}'>{1}</a>".format(
        #     license_link, license_name) +
        #                "test" +
        #                " v" +
        #                "1.1" +
        #                "&copy;2014 Anthony Beville" +
        #                "<a href='{0}'>{0}</a>".format(website) +
        #                "<a href='mailto:{0}'>{0}</a>".format(email) +
        #                "License: <a href='{0}'>{1}</a>".format(license_link, license_name)
        #                )
        self.addTableWidget(msgBox,type)
        msgBox.exec_()


    #Create TableWidget
    def addTableWidget (self, parentItem,type) :
        self.tableWidget = QtGui.QTableWidget(parentItem)
        self.tableWidget.setGeometry(QtCore.QRect(0, 0, 500, 250))
        self.tableWidget.setObjectName ('tableWidget')
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.paranet = parentItem
        if type =="LandCover":
            self.SetLandcoverTable(self.tableWidget)
        if type =="GreenAmpt":
            self.SetGreenAmptTable(self.tableWidget)
        if type=="SoilDepth" :
            self.SetSoilDepth(self.tableWidget)



    # 더블 클릭시 Qdialog 에 테이블 셋팅 하기
    def SetLandcoverTable(self,tableWidget):
        # 프로젝트 파일 로드
#         projectFile = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
#         doc = ET.parse(projectFile)
        #project파일이 아닌 stativDB.xml 을 읽어서 파싱해야함
#         #xml 경로 얻기
        staticdb = _util.StaticDB
        doc = ET.parse(staticdb)
        root = doc.getroot()
        list = []
        for element in root.findall('{http://tempuri.org/DataSet1.xsd}LandCoverParameter'):
            # list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}GridValue"))
            # list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}UserLandCover"))

            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}LandCoverE"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}LandCoverK"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}LandCoverCode"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}RoughnessCoefficient"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}ImperviousRatio"))
 
        # table에 값 셋팅
        tableWidget.verticalHeader().hide()
        tableWidget.setColumnCount(5)
        tableWidget.setRowCount(len(list) / 5)
        tableWidget.setHorizontalHeaderLabels(
            [  'LandCoverE', 'LandCoverK','GRMCode','RoughnessCoefficient','ImperviousRatio'])
 
        tableWidget.resizeColumnsToContents()
        tableWidget.resizeRowsToContents()
        tableWidget.itemDoubleClicked.connect(lambda: self.SelectCellValue(tableWidget, "LandCover"))
        # 각각의 컬럼에 갑셋팅(xml 상에 'ObTSId', 'ObTSLegend', 'ObTSMissingCount' 항목의 값이 없음
        for i in range(0, len(list) / 5):
            for j in range(0, 5):
                self.tableWidget.setItem(i, j, QTableWidgetItem(list[5 * i + j]))

    def SetGreenAmptTable(self,tableWidget):
        # 프로젝트 파일 로드
#         projectFile = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
#         doc = ET.parse(projectFile)

        staticdb = _util.StaticDB
        doc = ET.parse(staticdb)

        root = doc.getroot()
        list = []
        for element in root.findall("{http://tempuri.org/DataSet1.xsd}GreenAmptSoilParameter"):
            
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}SoilTextureE"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}SoilTextureK"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}SoilTextureCode"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}PorosityMin"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}PorosityMax"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}PorosityDefault"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}EffectivePorosityMin"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}EffectivePorosityMax"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}EffectivePorosityDefault"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}ResidualMoistureContent"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}WFSoilSuctionHeadMin"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}WFSoilSuctionHeadMax"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}WFSoilSuctionHeadDefault"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}HydraulicConductivity"))
            

        # table에 값 셋팅
        tableWidget.verticalHeader().hide()
        tableWidget.setColumnCount(14)
        tableWidget.setRowCount(len(list) / 14)
        tableWidget.setHorizontalHeaderLabels(
            ['SoilTextureE', 'SoilTextureK', 'SoilTextureCode', 'PorosityMin', 'PorosityMax', 'PorosityDefault', 'EffectivePorosityMin',
             'EffectivePorosityMax', 'EffectivePorosityDefault','ResidualMoistureContent','WFSoilSuctionHeadMin',
             'WFSoilSuctionHeadMax','WFSoilSuctionHeadDefault','HydraulicConductivity'])
 
        tableWidget.resizeColumnsToContents()
        tableWidget.resizeRowsToContents()
        tableWidget.itemDoubleClicked.connect(lambda : self.SelectCellValue(tableWidget,"GreenAmpt"))

        # 각각의 컬럼에 갑셋팅(xml 상에 'ObTSId', 'ObTSLegend', 'ObTSMissingCount' 항목의 값이 없음
        for i in range(0, len(list) / 14):
            for j in range(0, 14):
                self.tableWidget.setItem(i, j, QTableWidgetItem(list[14 * i + j]))


    def SetSoilDepth(self, tableWidget):
        # 프로젝트 파일 로드
#         projectFile = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
#         doc = ET.parse(projectFile)
        staticdb =_util.StaticDB
        doc = ET.parse(staticdb)

        root = doc.getroot()
        list = []
        for element in root.findall("{http://tempuri.org/DataSet1.xsd}SoilDepthParameter"):
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}GRMCode"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}SoilDepthClassE"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}SoilDepthClassK"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}SoilDepthMin"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}SoilDepthMax"))
            list.append(element.findtext("{http://tempuri.org/DataSet1.xsd}SoilDepthDefault"))

        # table에 값 셋팅
        tableWidget.verticalHeader().hide()
        tableWidget.setColumnCount(6)
        tableWidget.setRowCount(len(list) / 6)
        tableWidget.setHorizontalHeaderLabels(
            ['GRMCode', 'SoilDepthClassE', 'SoilDepthClassK', 'SoilDepthMin','SoilDepthMax','SoilDepth'])

        tableWidget.resizeColumnsToContents()
        tableWidget.resizeRowsToContents()
        tableWidget.itemDoubleClicked.connect(lambda: self.SelectCellValue(tableWidget, "SoilDepth"))
        # 각각의 컬럼에 갑셋팅(xml 상에 'ObTSId', 'ObTSLegend', 'ObTSMissingCount' 항목의 값이 없음
        for i in range(0, len(list) / 6):
            for j in range(0, 6):
                self.tableWidget.setItem(i, j, QTableWidgetItem(list[6 * i + j]))


    # 작은 창 테이블 클릭시 큰 테이블에 선택값 셋팅(집중이 안되서 노가다함 ㅠㅠ)
    def SelectCellValue(self, tableWidget,type):
        row = tableWidget.currentRow()
        if type=="LandCover":
            item2 = tableWidget.item(row, 0)
            item3 = tableWidget.item(row, 1)
            item4 = tableWidget.item(row, 2)
            item5 = tableWidget.item(row, 3)
            item6 = tableWidget.item(row, 4)
            
            self.tlbLandCover.item(_SelectRow, 3).setText(item2.text())
            self.tlbLandCover.item(_SelectRow, 4).setText(item3.text())
            self.tlbLandCover.item(_SelectRow, 2).setText(item4.text())
            self.tlbLandCover.item(_SelectRow, 5).setText(item5.text())
            self.tlbLandCover.item(_SelectRow, 6).setText(item6.text())
            # 메시지 박스 종료
            self.paranet.done(1)

        elif type=="GreenAmpt":
            item2 = tableWidget.item(row, 0)
            item3 = tableWidget.item(row, 1)
            item4 = tableWidget.item(row, 2)
            item5 = tableWidget.item(row, 5)
            item6 = tableWidget.item(row, 8)
            item7 = tableWidget.item(row, 12)
            item8 = tableWidget.item(row, 13)

            self.tblGreenAmpt.item(_SelectRow, 3).setText(item2.text())
            self.tblGreenAmpt.item(_SelectRow, 4).setText(item3.text())
            self.tblGreenAmpt.item(_SelectRow, 2).setText(item4.text())
            self.tblGreenAmpt.item(_SelectRow, 5).setText(item5.text())
            self.tblGreenAmpt.item(_SelectRow, 6).setText(item6.text())
            self.tblGreenAmpt.item(_SelectRow, 7).setText(item7.text())
            self.tblGreenAmpt.item(_SelectRow, 8).setText(item8.text())
            # 메시지 박스 종료
            self.paranet.done(1)

        elif type == "SoilDepth":
            item2 = tableWidget.item(row, 0)
            item3 = tableWidget.item(row, 1)
            item4 = tableWidget.item(row, 2)
            item5 = tableWidget.item(row, 5)

            self.tblSoilDepth.item(_SelectRow, 2).setText(item2.text())
            self.tblSoilDepth.item(_SelectRow, 3).setText(item3.text())
            self.tblSoilDepth.item(_SelectRow, 4).setText(item4.text())
            self.tblSoilDepth.item(_SelectRow, 5).setText(item5.text())
            # 메시지 박스 종료
            self.paranet.done(1)


