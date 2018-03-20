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
from qgis.core import *
from qgis.gui import *
from PyQt4 import QtGui, uic
import ElementTree as ET
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import test
import Util
import GRM_Plugin as GP
import GRM_Plugin_dockwidget as GRM
from plugin.grid_layer import get_point_layer
from plugin.flow_layer import get_flow_layer
from plugin.gmp_file import GMPFILE
from qgis.utils import *
import xmltodict
from plugin.dict2xml import dict2xml
from AddFlowControl_dialog import AddFlowControl
# import math
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# from plugin.collections import Counter


# Core DLL 을 이용해서 watch Point x 좌표와 y 좌표 값의 반환에 사용
# 경로는 하드 코딩이 아닌 추후에 경로 변경
import clr
DllPath = os.path.dirname(os.path.realpath(__file__)) + "\DLL\GRMCore.dll"
clr.AddReference(DllPath)
import GRMCore
from GRMCore import cGetWatershedInfo
from GRMCore import GRMProject


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Watershed_Stetup_dialog_base.ui'))

_util  = Util.util()
_projectFile =""
_extent = {}
_ymax = {}
_ymin = {}
_xmin = {}
_xmax = {}
_xsize = {}
_ysize = {}
_width = {}
_height = {}
_Cnavas_Click_X=0
_Cnavas_Click_Y =0
_layer={}
_CVID =0
_YROW =0
_XCOL =0
_Flowcontrolgrid_xmlCount=0
_wsinfo = {}


_FYROW =0
_FXCOL =0
_ClickX=""
_ClickY=""
_AddFlowcontrolFilePath =""
_AddFlowcontrolType=""
_AddFlowcontrolTimeInterval = ""
_AddFlowcontrolName = ""
_AddFlowcontrol_Edit_or_Insert_type=""

_Flowcontrolgrid_flag = False
_Flowcontrolgrid_flag_Insert = False


class Watershed_StetupDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(Watershed_StetupDialog, self).__init__(parent)
        self.setupUi(self)

        # 프로젝트 파일의 내용 및 Default 값을 설정
        self.Set_ProjectDataInit()

        # 캔버스 상위 버튼 아이콘 설정(Zoom , Pan.....)
        self.Set_Canvas_btn_icon()

        # 캔버스 툴 셋팅
        self.Set_Cavas_tool_btn()

        # 캔버스에 레이어 올리기
        self.Set_Canvas_Layer_default()

        # 시뮬레이션 탭 기능 기본값 셋팅
        self.Set_simulation_tab_default()
        # ---------------위치 이동 할 목록 -------------------
        # default 설정이지만 프로그램 흐름상 나중에 처리 해야 하는 목록
        # Watchpoint 체크박스 선택 상태로 처리
        self.chkWatch_Point.setChecked(True)
        # 무슨 기능인지 모르지만 기본 체크 상태
        self.chkFlowContorGird.setChecked(True)
        # ----------------위치 이동 할 목록 끝--------------------


        # WatchPoint 탭 기능 기본값 셋팅
        # 프로젝트 파일을 읽고 테이블에 셋팅(watch point)
        self.Set_Wathpoint_tab_default()

        # Channel CS 탭 기능 기본값 셋팅
        self.Set_ChannelCS_tab_default()

        # Watershed 탭 기능 기본값 셋팅
        self.Set_Watershed_Parameter_tab_default()

        # Flow Control 탭 기능 기본값 셋팅
        self.Set_FlowControl_tab_default()

        # # color picker 이벤트 연동
        # self.Set_ColorPicker_event()
        #
        # 프로그램 종료
        self.btnClose.clicked.connect(self.Close_Form)


        # # 시뮬레이션 버튼 이벤트  임시위치
        # self.btnStart_Simulation.clicked.connect(self.Click_StartSimulation)
        #
        # # 시뮬레이션 시행 종료 기능 비활성화 처리
        # self.btnStop_simulation.setEnabled(False)
        #_util에서 self.lblColRow 라벨
        _util.GlobalLabel(self.lblColRow,type="colrow")



        # Cell info Flow 텍스트 박스에 값 셋팅에 사용 하기 위해 유틸에 텍스트 박스 넘김
        _util.GlobalControl(self.txtCelltype,self.txtStreamValue,self.txtFD,self.txtFA,self.txtSlope)

        # Cell info Land cover
        _util.GlobalControl_Landcover(self.txtLandGridValue, self.txtLandType, self.txtRoughness, self.txtratio)

        # Cell info Depth
        _util.GlobalControl_Depth(self.txtDepthValue,self.txtSoilDepthClass, self.txtSoilDepth)


        # Cell info Texture
        _util.GlobalControl_texture(self.txtTextureGridValue, self.txtSoilTexture, self.txtPorosity, self.txtEffectivePorosity, self.txtSuctionhead,self.txtcondcutivity)

        #_util.GlobalEdit(self.txtChannel_width, "cw")
        # Discharge 파일 열기 이벤트
        self.btnViewResult.clicked.connect(self.Open_ViewResult)

        #self.btnView_WS_Pars.clicked.connect(self.View_WS_Pars_click)

        # 임시 처리
        self.RubberBand = []

    def Set_ProjectDataInit(self):


        # 그리드 라인 에 사용될 변수
        # 글로벌 변수로 지정 해서 사용 하면 화면을 닫았다가 다시 켜면 값이 남아 있어서 그리드 라인이 안그려짐
        self.grid_line = {}

        # direction 그리때 사용 변수
        # 글로벌 변수로 지정 해서 사용 하면 화면을 닫았다가 다시 켜면 값이 남아 있어서 디렉션이 안그려짐
        self.flow_direction = {}

        # 프로젝트 파일 경로 변수 셋팅
        self.ProjectFile = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']

        # watershed Layer file 경로 변수
        self.LayerPath = GRM._xmltodict['GRMProject']['ProjectSettings']['WatershedFile']

        # simulation Tab 변수
        self.RainfallInterval = GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallInterval']

        self.GridCellSize = GRM._xmltodict['GRMProject']['ProjectSettings']['GridCellSize']

        self.ComputationalTimeStep = GRM._xmltodict['GRMProject']['ProjectSettings']['ComputationalTimeStep']
        self.SimulationDuration = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulationDuration']
        self.OutputTimeStep = GRM._xmltodict['GRMProject']['ProjectSettings']['OutputTimeStep']
        self.SimulateInfiltration = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateInfiltration']
        self.SimulateSubsurfaceFlow = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateSubsurfaceFlow']
        self.SimulateBaseFlow = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateBaseFlow']
        self.SimulateFlowControl = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateFlowControl']

        self.SimulStartingTime = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulStartingTime']

        self.WatershedFile = GRM._xmltodict['GRMProject']['ProjectSettings']['WatershedFile']
        self.SlopeFile = GRM._xmltodict['GRMProject']['ProjectSettings']['SlopeFile']
        self.FlowDirectionFile = GRM._xmltodict['GRMProject']['ProjectSettings']['FlowDirectionFile']
        self.FlowAccumFile = GRM._xmltodict['GRMProject']['ProjectSettings']['FlowAccumFile']
        self.StreamFile = GRM._xmltodict['GRMProject']['ProjectSettings']['StreamFile']
        self.ChannelWidthFile = GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthFile']
        self.LandCoverFile = GRM._xmltodict['GRMProject']['ProjectSettings']['LandCoverFile']
        self.SoilTextureFile = GRM._xmltodict['GRMProject']['ProjectSettings']['SoilTextureFile']

        self.SoilDepthFile = GRM._xmltodict['GRMProject']['ProjectSettings']['SoilDepthFile']

        self.InitialChannelFlowFile = GRM._xmltodict['GRMProject']['ProjectSettings']['InitialChannelFlowFile']
        self.InitialSoilSaturationRatioFile = GRM._xmltodict['GRMProject']['ProjectSettings'][
            'InitialSoilSaturationRatioFile']

        if self.InitialChannelFlowFile == None:
            self.InitialChannelFlowFile = ""
        if self.InitialSoilSaturationRatioFile == None:
            self.InitialSoilSaturationRatioFile = ""
        if self.ChannelWidthFile == None:
            self.ChannelWidthFile=""
        # Core DLL 연동 작업 선행 처리

        global _wsinfo
        _wsinfo = cGetWatershedInfo(self.WatershedFile, self.SlopeFile, self.FlowDirectionFile, self.FlowAccumFile,
                                    self.StreamFile, self.LandCoverFile, self.SoilTextureFile, self.SoilDepthFile,
                                    self.InitialSoilSaturationRatioFile, self.InitialChannelFlowFile)
        # WatchPoint Tab table에 데이터만 채워 넣는 방식으로 변수로 값을 받을 필요가 없음 대신 전역 변수로 값 받읍
        # _util.MessageboxShowInfo("object","in")
        # result=str(_wsinfo.msoilTextureFPN())
        # Texture_Result = _wsinfo.STextureValue(99, 52)
        # _util.MessageboxShowInfo("Texture_Result", (Texture_Result)

        # _util.MessageboxShowInfo("texture",result)
        self.Set_Wathpoint_default_value()

        # ChannelWidth tab 변수
        self.ChannelWidthEQc = GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQc']
        self.ChannelWidthEQd = GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQd']
        self.ChannelWidthEQe = GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQe']
        self.ChannelWidthMostDownStream= GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthMostDownStream']
        self.LowerRegionHeight = GRM._xmltodict['GRMProject']['ProjectSettings']['LowerRegionHeight']
        self.LowerRegionBaseWidth = GRM._xmltodict['GRMProject']['ProjectSettings']['LowerRegionBaseWidth']
        self.UpperRegionBaseWidth = GRM._xmltodict['GRMProject']['ProjectSettings']['UpperRegionBaseWidth']
        self.CompoundCSChannelWidthLimit = GRM._xmltodict['GRMProject']['ProjectSettings']['CompoundCSChannelWidthLimit']
        self.BankSideSlopeRight = GRM._xmltodict['GRMProject']['ProjectSettings']['BankSideSlopeRight']
        self.BankSideSlopeLeft = GRM._xmltodict['GRMProject']['ProjectSettings']['BankSideSlopeLeft']

        if self.ChannelWidthEQc == None :
            self.ChannelWidthEQc = "1.698"
            GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQc'] = "1.698"

        if self.ChannelWidthEQd == None :
            self.ChannelWidthEQd = "0.318"
            GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQd'] = "0.318"

        if self.ChannelWidthEQe == None :
            self.ChannelWidthEQe = "0.5"
            GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQe'] = "0.5"

        if self.BankSideSlopeRight == None :
            self.BankSideSlopeRight = "1.5"
            GRM._xmltodict['GRMProject']['ProjectSettings']['BankSideSlopeRight'] = "1.5"

        if self.BankSideSlopeLeft == None :
            self.BankSideSlopeLeft = "1.5"
            GRM._xmltodict['GRMProject']['ProjectSettings']['BankSideSlopeLeft'] = "1.5"


    # 레이어 기본 값을 Global 로 지정해서 정의
    def Set_Global_CanvaseValue(self):
        global _width,_height,_xsize,_ysize,_extent,_ymax,_ymin,_xmax,_xmin
        _width = self.layer.width()
        _height = self.layer.height()
        _xsize = self.layer.rasterUnitsPerPixelX()
        _ysize = self.layer.rasterUnitsPerPixelY()
        _extent = self.layer.extent()
        _ymax = _extent.yMaximum()
        _ymin = _extent.yMinimum()
        _xmax = _extent.xMaximum()
        _xmin = _extent.xMinimum()

     # def 연동 함수
    def Open_ViewResult(self):
        _disCharge = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
        disCharge_path = os.path.splitext(os.path.basename(_disCharge))[0]
        _disCharge = _disCharge.replace(disCharge_path+".gmp",disCharge_path+"Discharge.out")
        _util.Opewn_ViewFile(_disCharge)
#
#     def View_WS_Pars_click(self):
#         website = "http://code.google.com/p/comictagger"
#         email = "comictagger@gmail.com"
#         license_link = "http://www.apache.org/licenses/LICENSE-2.0"
#         license_name = "Apache License 2.0"
#         Project = "test"
#         msgBox = QtGui.QMessageBox()
#         # msgBox.addButton(QtGui.QMessageBox.Yes)
#         # msgBox.addButton(QtGui.QMessageBox.No)
#         msgBox.setWindowTitle(self.tr("Project information"))
#
#         msgBox.setTextFormat(QtCore.Qt.RichText)
#
#         msgBox.setIconPixmap(QtGui.QPixmap(Project))
#
#         msgBox.setText("<br><br><br><br><br><br><br><br><br><br><br>"+
#             "<font color=white>" +
#             "{0},{1},{2}</font>".format(website, email,license_name))
#
#         self.addTableWidget(msgBox)
#         ret = msgBox.exec_()
#         # -----------------------------2017/10/30---------------
#         # if ret == QtGui.QMessageBox.Yes:
#         #     self.msg_test()
#         #
#         # else:
#         #     pass
#
#
#
#
#     # Create TableWidget
#     def addTableWidget(self, parentItem):
#         tableWidgets = QtGui.QTableWidget(parentItem)
#         tableWidgets.setGeometry(QtCore.QRect(0, 0, 500, 250))
#         tableWidgets.setObjectName('tableWidget')
#         self.Set_ViewWSPars(tableWidgets)
#
#     def Set_ViewWSPars(self, tableWidget):
#         tableWidget.verticalHeader().hide()
#         tableWidget.setColumnCount(14)
#         tableWidget.setHorizontalHeaderLabels(['ID', 'IniSaturation', 'MinSlopeOF', 'MinSlopeChBed', 'MinChBaseWidth', 'ChRoughness', 'DryStreamOrder','IniFlow', 'CalCoefLCRoughness', 'CalCoefPorosity', 'CalCoefWFSuctionHead', 'CalCoefHydraulicK','CalCoefSoilDepth', 'UserSet'])
#
#         projectFile = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
#         doc = ET.parse(projectFile)
#         root = doc.getroot()
#         row = 0
#         for element in root.findall('{http://tempuri.org/GRMProject.xsd}SubWatershedSettings'):
#             tableWidget.insertRow(row)
#             tableWidget.setItem(row, 0, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}ID")))
#             tableWidget.setItem(row, 1, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}IniSaturation")))
#             tableWidget.setItem(row, 2, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}MinSlopeOF")))
#             tableWidget.setItem(row, 3, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}MinSlopeChBed")))
#             tableWidget.setItem(row, 4, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}MinChBaseWidth")))
#             tableWidget.setItem(row, 5, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}ChRoughness")))
#             tableWidget.setItem(row, 6, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}DryStreamOrder")))
#             tableWidget.setItem(row, 7, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}IniFlow")))
#             tableWidget.setItem(row, 8, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}CalCoefLCRoughness")))
#             tableWidget.setItem(row, 9, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}CalCoefPorosity")))
#             tableWidget.setItem(row, 10, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}CalCoefWFSuctionHead")))
#             tableWidget.setItem(row, 11, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}CalCoefHydraulicK")))
#             tableWidget.setItem(row, 12, QTableWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}CalCoefSoilDepth")))
#
#             userSet = element.findtext("{http://tempuri.org/GRMProject.xsd}UserSet")
#
#             checkcheck = QTableWidgetItem()
#             checkcheck.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
#
#             if userSet.upper() == "TRUE":
#                 checkcheck.setCheckState(QtCore.Qt.Checked)
#             else:
#                 checkcheck.setCheckState(QtCore.Qt.Unchecked)
#
#             tableWidget.setItem(row, 13, checkcheck)
#
#         # item = tableWidget.item(13,0)
#         # tableWidget.scrollToItem(item,QtGui.QAbstractItemView.PositionAtTop)
#         # tableWidget.selectRow(13)
#         # _util.MessageboxShowInfo("test",str(item))
#
#         row= row+1
#         tableWidget.resizeColumnsToContents()
#         tableWidget.resizeRowsToContents()
#
#
#
#
#
#
#
    # canvas 버튼 아이콘 이미지 설정
    def Set_Canvas_btn_icon(self):
        ZoomExtent = os.path.dirname(os.path.abspath(__file__)) + "\image\ZoomExtent.png"
        Zoomin = os.path.dirname(os.path.abspath(__file__)) + "\image\ZoomIn.png"
        ZoomOut = os.path.dirname(os.path.abspath(__file__)) + "\image\ZoomOut.png"
        Pan = os.path.dirname(os.path.abspath(__file__)) + "\image\Pan.png"
        Zoomnext = os.path.dirname(os.path.abspath(__file__)) + "\image\Zoomnext.png"
        ZoomPrevious = os.path.dirname(os.path.abspath(__file__)) + "\image\ZoomPrevious.png"
        SelectGrid = os.path.dirname(os.path.abspath(__file__)) + "\image\SelectGrid.png"
        MoveTo = os.path.dirname(os.path.abspath(__file__)) + "\image\MoveTo.png"

        self.btnZoomExtent.setIcon(QtGui.QIcon(ZoomExtent))
        self.btnZoomIn.setIcon(QtGui.QIcon(Zoomin))
        self.btnZoomOut.setIcon(QtGui.QIcon(ZoomOut))
        self.btnPan.setIcon(QtGui.QIcon(Pan))
        self.btnZoomnext.setIcon(QtGui.QIcon(Zoomnext))
        self.btnZoomprevious.setIcon(QtGui.QIcon(ZoomPrevious))
        self.btnSelectgrid.setIcon(QtGui.QIcon(SelectGrid))
        self.btnMoveto.setIcon(QtGui.QIcon(MoveTo))

    # 캔버스 툴 기능 연동
    def Set_Cavas_tool_btn(self):

        self.tool = CanvasTool(self.mapcanvas)

        # ZoomExtent
        self.btnZoomExtent.clicked.connect(self.tool.ZoomtoExtent)

        # Zoom Next
        self.btnZoomnext.clicked.connect(self.tool.ZoomtoNextExtent)

        # Zoom Previous
        self.btnZoomprevious.clicked.connect(self.tool.ZoomtoPrevious)

        # Zoom In
        self.btnZoomIn.clicked.connect(self.tool.canvas_zoomIn)

        # Zoom Out
        self.btnZoomOut.clicked.connect(self.tool.canvas_zoomOut)

        # Pan
        self.btnPan.clicked.connect(self.tool.canvas_pan)

        #2017 12 06 박: 프로그램 점검 중 임시 주석
        # Moveto
        self.btnMoveto.clicked.connect(self.aboutApp)

         # Selectgrid
        self.btnSelectgrid.clicked.connect(self.identify)

        # Watch_Point 기본 설정은 체크
        self.chkWatch_Point.stateChanged.connect(self.watchpoint)

        # chkFC 추후 구현
        self.chkFlowContorGird.stateChanged.connect(self.click_FlowContorGird)

        # 체크 박스 눌렀을때 캔버스에 그리드 라인 추가 함수
        self.show_grid_line.clicked.connect(self.show_hide_grid_line)

        # 캔버스에 Flow direction
        self.show_flow_direction.clicked.connect(self.show_hide_flow_direction)



    # 캔버스에 레이어 올리기
    def Set_Canvas_Layer_default(self):
        # canvase 레이어 올리기
        if self.LayerPath is not None:
            global _layer
            self.layer = QgsRasterLayer(self.LayerPath, "FA", "gdal")
            # 캔버스의 기본 정보를 Global에 대입 다른 클래스에서 사용
            _layer = self.layer
            self.Set_Global_CanvaseValue()

            """#2017.11..1 원 :
                문제1. 상기 ASC가 투영 좌표계 레이어인데. 경위도로 오인 지정되어 있었슴. 이는 PRJ 파일 만듧면 해결됨.
                문제2 .그리고 canvas 는 직접 setDestinationCrs 해야 좌표계가 지정됨. https://issues.qgis.org/issues/9772 """

            self.mapcanvas.setDestinationCrs(self.layer.crs())
            QgsMapLayerRegistry.instance().addMapLayer(self.layer, False)
            self.mapcanvas.setExtent(self.layer.extent())
            self.mapcanvas.setLayerSet([QgsMapCanvasLayer(self.layer)])


    # ----------------- 2017-10-24_오전 박 simulation 탭 텍스트 박스 셋팅 -----------------------------
    def Set_simulation_tab_default(self):

        if self.SimulStartingTime =="0" :
            now = QtCore.QDateTime.currentDateTime()
            self.dateTimeEdit.setDateTime(now)
            self.chkStartingTime.setChecked(False)
            self.dateTimeEdit.setEnabled(False)
        else:
            self.chkStartingTime.setChecked(True)
            self.dateTimeEdit.setEnabled(True)
            dateTime = QDateTime.fromString(self.SimulStartingTime,"yyyy-MM-dd hh:mm")
            # StartDate = QtCore.QDateTime(2011, 4, 22, 16, 33, 15)
            self.dateTimeEdit.setDateTime(dateTime)

        if self.SimulationDuration is not None:
            self.txtRainfall_Duration.setText(self.SimulationDuration)
        else:
            count=_util.RainfallCount()
            if count>0:
                hour = float(count)/60
                strhour = "%.2f" % hour
                self.txtRainfall_Duration.setText(strhour)
            else:
                self.txtRainfall_Duration.setText("0")


        # 만약에 Cell size 값이 없으면 레이어에서 값을 받음
        if self.GridCellSize is not None :
            self.txtGrid_Size.setText(self.GridCellSize)
        else :
            self.GridCellSize = str(_xsize)
            if self.GridCellSize is not None :
                GRM._xmltodict['GRMProject']['ProjectSettings']['GridCellSize'] = str(_xsize)
                self.txtGrid_Size.setText(self.GridCellSize)

        if self.ComputationalTimeStep is not None :
            intvalue = int(self.ComputationalTimeStep)
            self.spTimeStep_min.setValue(intvalue)
        else:
            if _xsize<=200:
                value =3
            elif _xsize>200:
                value = 5
            self.spTimeStep_min.setValue(value)

        if self.RainfallInterval is not None:
            self.txtRainfall_intval.setText(str(self.RainfallInterval))

        if self.OutputTimeStep is not None:
            self.txtOutput_time_step.setText(str(self.OutputTimeStep))
        else:
            self.txtOutput_time_step.setText(str(self.RainfallInterval))

        Allcount=_wsinfo.grmPrj.CVCount
        if Allcount is not None:
            self.txtCellCount.setText(str(Allcount))



        # 기본 사양은 비활성화
        self.txtGrid_Size.setDisabled(True)
        self.txtCellCount.setDisabled(True)
        self.txtRainfall_intval.setDisabled(True)
        self.txtRainfall_Duration.setDisabled(True)

        # # 프로젝트 파일에서 기본 셋팅 분을 받아 옴
        # if self.ComputationalTimeStep is not None:
        #     Time_step_s = float(self.ComputationalTimeStep) * 60
        #     # 타임스텝 (분)
        #     self.txtTimeStep_min.setText(self.ComputationalTimeStep)
        #     # 타임스텝 (초)
        #     # self.txtTimeStep_sec.setText(str(Time_step_s))

        if self.SimulationDuration is not None:
            self.txtSimulation_duration.setText(SimulationDuration)
        else:
            simulationDuration=self.txtRainfall_Duration.text()
            if float(simulationDuration)>0:
                convert = float(simulationDuration)
                # result=math.ceil(convert)
                result=9
                self.txtSimulation_duration.setText(str(result))


        if self.OutputTimeStep is not None:
            self.txtOutput_time_step.setText(self.OutputTimeStep)
        # 체크 박스 셋팅 (프로젝트 파일에서 체크 값 받아서 셋팅)
        if self.SimulateInfiltration is not None:
            if self.SimulateInfiltration.upper() == "TRUE":
                self.chkInfiltration.setChecked(True)
        elif self.SimulateInfiltration is None:
            # 데이터 값이 없으면 기본 설정은 체크
            self.chkInfiltration.setChecked(True)

        if self.SimulateSubsurfaceFlow  is not None:
            if self.SimulateSubsurfaceFlow .upper() == "TRUE" :
                self.chkSubsurfaceFlow.setChecked(True)
        elif self.SimulateSubsurfaceFlow is None:
            # 데이터 값이 없으면 기본 설정은 체크
            self.chkSubsurfaceFlow.setChecked(True)

        if self.SimulateBaseFlow is not None:
            if self.SimulateBaseFlow.upper() == "TRUE" :
                self.chkBaseFlow.setChecked(True)
        elif self.SimulateBaseFlow is None:
            # 데이터 값이 없으면 기본 설정은 체크
            self.chkBaseFlow.setChecked(True)


        if self.SimulateFlowControl is not None:
            if self.SimulateFlowControl.upper() == "TRUE":
                self.chkFlowControl.setChecked(True)
        self.btnShowanalyzer.setEnabled(False)
        self.chkanalyze.stateChanged.connect(self.alyzerEnable)
        self.chkStartingTime.stateChanged.connect(self.Check_StartingTime)
        self.chkanalyze.setEnabled(False)

    def alyzerEnable(self):
        if self.chkanalyze.isChecked():
            self.btnShowanalyzer.setEnabled(True)
        else :
            self.btnShowanalyzer.setEnabled(False)

    def Check_StartingTime(self):
        if self.chkStartingTime.isChecked():
            self.dateTimeEdit.setEnabled(True)
        else:
            self.dateTimeEdit.setEnabled(False)




    # ======================================simulation 탭 종료=================================


    # ======================WatchPoint Tab Table Setting and btn event =========================
    def Set_Wathpoint_tab_default(self):

        # 테이블 상에 선택된 열을 위로 올림
        self.btnMoveup.clicked.connect(self.MoveUp)

        # 테이블 상에 선택된 열을 아래로 내림
        self.btnMovedown.clicked.connect(self.MoveDown)

        # 테이블 상에 선택된 열을 삭제
        self.btnRemove.clicked.connect(self.ReMove)

        # 테이블 셀값을 변경 불가능 하게 설정
        self.tbList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        # color picker 이벤트
        self.btnColorPicker.clicked.connect(lambda: self.color_picker(self.btnColorPicker, "watchpoint"))
        #2017/11/22-------------------
        #테이블 셀 값 선택한 값의 위치로 view 이동
        self.btnGrid.clicked.connect(self.GoToGrid)

        # 테이블 셀값을 변경 가능하게 설정 ----> 색상값 변경임 잘못된 구현 변경 해야함
        self.btnEdit.clicked.connect(self.Edit)

        self.btnAddSelectCell.clicked.connect(self.Add_Selected_Cell)

        # 각각의 컬럼에 갑셋팅(xml 상에 'ObTSId', 'ObTSLegend', 'ObTSMissingCount' 항목의 값이 없음
        self.Watchpoint_TableCreate(len(self.Name))
        self.Watchpoint_Table_Insert()


    def Watchpoint_Table_Insert(self):
        if len(self.Name) >0:
            for i in range(0, len(self.Name)):
                # 사용자에게 CVID 표출 안함
                # self.tbList.setItem(i, 0, QTableWidgetItem(self.CVID[i]))
                self.tbList.setItem(i, 0, QTableWidgetItem(self.Name[i]))
                #self.tbList.setItem(i, 1, QTableWidgetItem(self.FlowAccumulation[i]))
                #self.tbList.setItem(i, 2, QTableWidgetItem(self.CellType[i]))
                self.tbList.setItem(i, 1, QTableWidgetItem(self.ColX[i]))
                self.tbList.setItem(i, 2, QTableWidgetItem(self.RowY[i]))
                #self.tbList.setItem(i, 3, QTableWidgetItem(self.Fixed[i]))

    # watchpoint datault 값을 변수에 저장
    def Set_Wathpoint_default_value(self):
        self.CVID =[]
        self.Name = []
        self.FlowAccumulation = []
        self.CellType = []
        self.ColX = []
        self.RowY = []
        self.Fixed = []


        doc = ET.parse(self.ProjectFile)
        root = doc.getroot()
        for element in root.findall("{http://tempuri.org/GRMProject.xsd}WatchPoints"):
            #self.CVID.append(element.findtext("{http://tempuri.org/GRMProject.xsd}CVID"))
            self.Name.append(element.findtext("{http://tempuri.org/GRMProject.xsd}Name"))
            #self.FlowAccumulation.append(element.findtext("{http://tempuri.org/GRMProject.xsd}FlowAccumulation"))
            #self.CellType.append(element.findtext("{http://tempuri.org/GRMProject.xsd}CellType"))
            self.ColX.append(element.findtext("{http://tempuri.org/GRMProject.xsd}ColX"))
            self.RowY.append(element.findtext("{http://tempuri.org/GRMProject.xsd}RowY"))

        if len(self.Name) ==0:
            # global _wsinfo
            # _wsinfo = cGetWatershedInfo(self.WatershedFile, self.SlopeFile, self.FlowDirectionFile, self.FlowAccumFile,
            #                             self.StreamFile, self.LandCoverFile, self.SoilTextureFile, self.SoilDepthFile,
            #                             self.InitialSoilSaturationRatioFile, self.InitialChannelFlowFile)

            # _wsinfo = cGetWatershedInfo(self.WatershedFile, self.SlopeFile, self.FlowDirectionFile, self.FlowAccumFile,
            #                             self.StreamFile, "","","","","")

            # _util.MessageboxShowError("WatershedFile",self.WatershedFile)
            # _util.MessageboxShowError("SlopeFile", self.SlopeFile)
            # _util.MessageboxShowError("FlowDirectionFile",self.FlowDirectionFile)
            # _util.MessageboxShowError("FlowAccumFile",self.FlowAccumFile)
            # _util.MessageboxShowError("StreamFile",self.StreamFile)
            # _util.MessageboxShowError("LandCoverFile",self.LandCoverFile)
            # _util.MessageboxShowError("SoilTextureFile",self.SoilTextureFile)
            # _util.MessageboxShowError("SoilDepthFile",self.SoilDepthFile)
            # _util.MessageboxShowError("InitialSoilSaturationRatioFile",self.InitialSoilSaturationRatioFile)
            # _util.MessageboxShowError("InitialChannelFlowFile",self.InitialChannelFlowFile)

            # WSFPN = "C:\GRM\Sample\Data\Watershed.asc"
            # SlopeFPN = "C:\GRM\Sample\Data\Wi_Slope_ST.asc"
            # FdirFPN = "C:\GRM\Sample\Data\WiFDir.asc"
            # FacFPN = "C:\GRM\Sample\Data\WiFAc.asc"
            # streamFPN = "C:\GRM\Sample\Data\WiStream6.asc"
            # lcFPN = "C:\GRM\Sample\Data\wilc200.asc"
            # stFPN = "C:\GRM\Sample\Data\wistext200.asc"
            # sdFPN = "C:\GRM\Sample\Data\wisdepth200.asc"
            # _wsinfo = cGetWatershedInfo(WSFPN, SlopeFPN, FdirFPN, FacFPN, streamFPN, lcFPN, stFPN, sdFPN, "", "")


            x = _wsinfo.mostDownStreamCellArrayXColPosition()
            y = _wsinfo.mostDownStreamCellArrayYRowPosition()

            # _util.MessageboxShowError("x", str(x))

            proname = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
            names = _util.GetFilename(proname)
            self.Name.append(names)
            self.ColX.append(str(x))
            self.RowY.append(str(y))

    # ======================WatchPoint Tab Table Setting 종료=======================================


    # ----------------- Channel CS 탭 텍스트 박스 셋팅 -----------------------------
    def Set_ChannelCS_tab_default(self):
        self.txt_c.setText(self.ChannelWidthEQc)
        self.txt_d.setText(self.ChannelWidthEQd)
        self.txt_e.setText(self.ChannelWidthEQe)
        self.txt_douwnstream.setText(self.ChannelWidthMostDownStream)
        self.txtLower_Region_Height.setText(self.LowerRegionHeight)
        self.txtLower_Region_Base_Width.setText(self.LowerRegionBaseWidth)
        self.txtUpper_Region_Base_Width.setText(self.UpperRegionBaseWidth)
        self.txtCompound_CSChannel_Width_Limit.setText(self.CompoundCSChannelWidthLimit)
        self.txtRight_bank.setText(self.BankSideSlopeRight)
        self.txtLeft_bank.setText(self.BankSideSlopeLeft)
        self.rdo_single.setChecked(True)
        self.groupBox_6.setDisabled(True)
        self.rdo_useCh.setChecked(True)
        self.txt_douwnstream.setDisabled(True)
        self.rdo_single.clicked.connect(self.ChannelCS_rdo_able)
        self.rdo_compound.clicked.connect(self.ChannelCS_rdo_able)
        self.rdo_useCh.clicked.connect(self.ChannelCS_rdo_able)
        self.rdo_generateCh.clicked.connect(self.ChannelCS_rdo_able)

        # 사용 안함
        # # 사용자가 마우스 클릭 부분의 셀 색을 변경 하는 기능  (2017-11-16 박)
        # self.btnChage.clicked.connect(self.btnChage_click)
        # 사용자가 마우스 클릭 부분의 셀 색을 변경 하는 기능  (2017-11-17 박)
        # self.btInitilalize.clicked.connect(self.btInitilalize_click)
        # 모든 루버 밴드를 지울때 Watch point 부분이 지워지지 않도록 처리 해야 할듯  (2017-11-17 박)
        # self.btInitilalize_All.clicked.connect(self.btInitilalize_All_click)
    # ============================ Channel CS 탭 종료 =================================================

    # ============================ Flow Control 탭 시작 ===============================================
    def Set_FlowControl_tab_default(self):
        # 테이블 셀값을 변경 불가능 하게 설정
        self.tlbFlowControl.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        # 테이블에 초기 셋팅
        self.FlowControlTableSetting()
        # 테이블에 값 셋팅후 화면에 점 표시
        self.FlowContorGird_paint()

        self.btnFlowControl_AddCell.clicked.connect(self.FlowControlAddCell)
        self.btnFWCEdit.clicked.connect(self.FlowControlEdit)
        self.tlbFlowControl.itemClicked.connect(self.tlbFlowControl_clik_enent)
        self.btnFlowRemove.clicked.connect(self.RemoveTalbeRow)

    # Flow control 테이블 셋팅
    # 프로젝트 파일에서 데이터 값이 있으면 테이블에 값을 셋팅
    def FlowControlTableSetting(self):
        global  _Flowcontrolgrid_xmlCount
        self.tlbFlowControl.setColumnCount(12)
        self.tlbFlowControl.setHorizontalHeaderLabels(['ColX', 'RowY', 'Name', 'DT', 'ControlType', 'FlowDataFile','IniStorage','MaxStorage','MaxStorageR','ROType','ROConstQ','ROConstQDuration'])
        self.tlbFlowControl.verticalHeader().hide()

        if _Flowcontrolgrid_flag == False:
            _Flowcontrolgrid_xmlCount = _util.FlowControlGrid_XmlCount()

        if _Flowcontrolgrid_xmlCount == 1:
            self.tlbFlowControl.insertRow(0)
            self.tlbFlowControl.setItem(0, 0, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['ColX']))
            self.tlbFlowControl.setItem(0, 1, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['RowY']))
            self.tlbFlowControl.setItem(0, 2, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['Name']))
            self.tlbFlowControl.setItem(0, 3, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['DT']))
            self.tlbFlowControl.setItem(0, 4, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['ControlType']))
            self.tlbFlowControl.setItem(0, 5, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['FlowDataFile']))

            if 'ROType' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                self.tlbFlowControl.setItem(0, 9, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['ROType']))
            else:
                self.tlbFlowControl.setItem(0, 9, QTableWidgetItem(""))

            if 'ROConstQ' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                self.tlbFlowControl.setItem(0, 10, QTableWidgetItem(
                    GRM._xmltodict['GRMProject']['FlowControlGrid']['ROConstQ']))
            else:
                self.tlbFlowControl.setItem(0, 10, QTableWidgetItem(""))

            if 'ROConstQDuration' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                self.tlbFlowControl.setItem(0, 11, QTableWidgetItem(
                    GRM._xmltodict['GRMProject']['FlowControlGrid']['ROConstQDuration']))
            else:
                self.tlbFlowControl.setItem(0, 11, QTableWidgetItem(""))

            if GRM._xmltodict['GRMProject']['FlowControlGrid']['ControlType'] =="ReservoirOperation":
                if 'IniStorage' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                    self.tlbFlowControl.setItem(0, 6, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['IniStorage']))
                else:
                    self.tlbFlowControl.setItem(0, 6, QTableWidgetItem(""))

                if 'MaxStorage' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                    self.tlbFlowControl.setItem(0, 7, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['MaxStorage']))
                else:
                    self.tlbFlowControl.setItem(0, 7, QTableWidgetItem(""))

                if 'MaxStorageR' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                    self.tlbFlowControl.setItem(0, 8, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['MaxStorageR']))
                else:
                    self.tlbFlowControl.setItem(0, 8, QTableWidgetItem(""))

        elif _Flowcontrolgrid_xmlCount > 1:
            row =0
            for flowitem in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                self.tlbFlowControl.insertRow(row)
                self.tlbFlowControl.setItem(row, 0, QTableWidgetItem(str(flowitem['ColX'])))
                self.tlbFlowControl.setItem(row, 1, QTableWidgetItem(str(flowitem['RowY'])))
                self.tlbFlowControl.setItem(row, 2, QTableWidgetItem(flowitem['Name']))
                self.tlbFlowControl.setItem(row, 3, QTableWidgetItem(str(flowitem['DT'])))
                self.tlbFlowControl.setItem(row, 4, QTableWidgetItem(flowitem['ControlType']))
                self.tlbFlowControl.setItem(row, 5, QTableWidgetItem(flowitem['FlowDataFile']))

                if flowitem['ControlType'] == "ReservoirOperation":
                    if 'IniStorage' in flowitem:
                        self.tlbFlowControl.setItem(row, 6, QTableWidgetItem(flowitem['IniStorage']))
                    else:
                        self.tlbFlowControl.setItem(row, 6, QTableWidgetItem(""))
                    if 'MaxStorage' in flowitem:
                        self.tlbFlowControl.setItem(row, 7, QTableWidgetItem(flowitem['MaxStorage']))
                    else:
                        self.tlbFlowControl.setItem(row, 7, QTableWidgetItem(""))

                    if 'MaxStorageR' in flowitem:
                        self.tlbFlowControl.setItem(row, 8, QTableWidgetItem(flowitem['MaxStorageR']))
                    else:
                        self.tlbFlowControl.setItem(row, 8, QTableWidgetItem(""))
                else:
                    self.tlbFlowControl.setItem(row, 6, QTableWidgetItem(""))
                    self.tlbFlowControl.setItem(row, 7, QTableWidgetItem(""))
                    self.tlbFlowControl.setItem(row, 8, QTableWidgetItem(""))



                if 'ROType' in flowitem:
                    self.tlbFlowControl.setItem(row, 9, QTableWidgetItem(flowitem['ROType']))
                else:
                    self.tlbFlowControl.setItem(row, 9, QTableWidgetItem(""))

                if 'ROConstQ' in flowitem:
                    self.tlbFlowControl.setItem(row, 10, QTableWidgetItem(flowitem['ROConstQ']))
                else:
                    self.tlbFlowControl.setItem(row, 10, QTableWidgetItem(""))

                if 'ROConstQDuration' in  flowitem:
                    self.tlbFlowControl.setItem(row, 11, QTableWidgetItem(flowitem['ROConstQDuration']))
                else:
                    self.tlbFlowControl.setItem(row, 11, QTableWidgetItem(""))
                row = row+1

    # 사용자 추가 입력창 화면
    def FlowControlAddCell(self):
        global _AddFlowcontrol_Edit_or_Insert_type,_Flowcontrolgrid_flag_Insert
        if _FXCOL==0 and _FYROW==0 :
            mb = QtGui.QMessageBox( "Flow Control Grid"," No cells selected. ", QtGui.QMessageBox.Information, QtGui.QMessageBox.Ok,0, 0)
            mb.exec_()
        else:
            _AddFlowcontrol_Edit_or_Insert_type = "Insert"
            results = AddFlowControl()
            results.exec_()
            if _Flowcontrolgrid_flag_Insert :
                self.ADDFlowData()
                _Flowcontrolgrid_flag_Insert = False

            global _AddFlowcontrolFilePath ,_AddFlowcontrolName ,_AddFlowcontrolType ,_AddFlowcontrolTimeInterval
            _AddFlowcontrolFilePath = ""
            _AddFlowcontrolType = ""
            _AddFlowcontrolTimeInterval = ""
            _AddFlowcontrolName = ""
            _AddFlowcontrol_Edit_or_Insert_type = ""

    def ADDFlowData(self):
        if _AddFlowcontrolFilePath=="" :
            pass
        if _AddFlowcontrolType=="":
            pass
        counts=self.tlbFlowControl.rowCount()
        if _FXCOL !=0 and _FYROW!=0:
            global _FXCOL , _FYROW
            self.tlbFlowControl.insertRow(counts)
            self.tlbFlowControl.setItem(counts, 0, QTableWidgetItem(str(_YROW)))
            self.tlbFlowControl.setItem(counts,1, QTableWidgetItem(str(_XCOL)))

            _FXCOL=0
            _FYROW=0
            self.tlbFlowControl.setItem(counts,2, QTableWidgetItem(_AddFlowcontrolName))
            self.tlbFlowControl.setItem(counts,3, QTableWidgetItem(_AddFlowcontrolTimeInterval))
            self.tlbFlowControl.setItem(counts,4, QTableWidgetItem(_AddFlowcontrolType))
            self.tlbFlowControl.setItem(counts,5, QTableWidgetItem(_AddFlowcontrolFilePath))
            self.tlbFlowControl.setItem(counts,6, QTableWidgetItem(""))
            self.tlbFlowControl.setItem(counts,7, QTableWidgetItem(""))
            self.tlbFlowControl.setItem(counts,8, QTableWidgetItem(""))
            self.tlbFlowControl.setItem(counts,9, QTableWidgetItem(""))
            self.tlbFlowControl.setItem(counts,10, QTableWidgetItem(""))
            self.tlbFlowControl.setItem(counts,11, QTableWidgetItem(""))

        # 나중에 함수로 빼야 할 부분 시간 없어서 그냥 사용함
        global _Flowcontrolgrid_xmlCount, _Flowcontrolgrid_flag
        _Flowcontrolgrid_flag = True
        # 딕셔너리 삭제

        if _Flowcontrolgrid_xmlCount>0:
            del GRM._xmltodict['GRMProject']['FlowControlGrid']
        DictoXml = xmltodict.unparse(GRM._xmltodict)
        ET.register_namespace('', "http://tempuri.org/GRMProject.xsd")
        xmltree = ET.ElementTree(ET.fromstring(DictoXml))
        root = xmltree.getroot()

        count = self.tlbFlowControl.rowCount()
        _Flowcontrolgrid_xmlCount = count
        for row in range(0, _Flowcontrolgrid_xmlCount):
            child = ET.Element("FlowControlGrid")
            root.append(child)

            GridValue = ET.Element("ColX")
            GridValue.text = self.tlbFlowControl.item(row, 0).text()
            child.append(GridValue)

            UserLandCover = ET.Element("RowY")
            UserLandCover.text = self.tlbFlowControl.item(row, 1).text()
            child.append(UserLandCover)

            GRMLandCoverCode = ET.Element("Name")
            GRMLandCoverCode.text = self.tlbFlowControl.item(row, 2).text()
            child.append(GRMLandCoverCode)

            DT = ET.Element("DT")
            DT.text = self.tlbFlowControl.item(row, 3).text()
            child.append(DT)

            ControlType = ET.Element("ControlType")
            ControlType.text = self.tlbFlowControl.item(row, 4).text()
            child.append(ControlType)

            FlowDataFile = ET.Element("FlowDataFile")
            FlowDataFile.text = self.tlbFlowControl.item(row, 5).text()
            child.append(FlowDataFile)

            IniStorage = ET.Element("IniStorage")
            if self.tlbFlowControl.item(row, 6).text() != "":
                IniStorage.text = self.tlbFlowControl.item(row, 6).text()
            else:
                IniStorage.text = ""
            child.append(IniStorage)

            MaxStorage = ET.Element("MaxStorage")
            if self.tlbFlowControl.item(row, 7).text() != "":
                MaxStorage.text = self.tlbFlowControl.item(row, 7).text()
            else:
                MaxStorage.text = ""
            child.append(MaxStorage)

            MaxStorageR = ET.Element("MaxStorageR")
            if self.tlbFlowControl.item(row, 8).text() != "":
                MaxStorageR.text = self.tlbFlowControl.item(row, 8).text()
            else:
                MaxStorageR.text = ""
            child.append(MaxStorageR)

            ROType = ET.Element("ROType")
            if self.tlbFlowControl.item(row, 9).text() != "":
                ROType.text = self.tlbFlowControl.item(row, 9).text()
            else:
                ROType.text = ""
            child.append(ROType)

            ROConstQ = ET.Element("ROConstQ")
            if self.tlbFlowControl.item(row, 10).text() != "":
                ROConstQ.text = self.tlbFlowControl.item(row, 10).text()
            else:
                ROConstQ.text = ""
            child.append(ROConstQ)

            ROConstQDuration = ET.Element("ROConstQDuration")
            if self.tlbFlowControl.item(row, 11).text() != "":
                ROConstQDuration.text = self.tlbFlowControl.item(row, 11).text()
            else:
                ROConstQDuration.text = ""
            child.append(ROConstQDuration)
        xmltree_string = ET.tostring(xmltree.getroot())
        docs = dict(xmltodict.parse(xmltree_string))
        GRM._xmltodict.clear()
        GRM._xmltodict.update(docs)


        # 테이블에 값 셋팅후 화면에 점 표시
        self.FlowContorGird_paint()

    def FlowControlEdit(self):
        global _AddFlowcontrol_Edit_or_Insert_type,_Flowcontrolgrid_xmlCount
        row = self.tlbFlowControl.currentRow()
        if row>-1:
            _AddFlowcontrol_Edit_or_Insert_type = "Edit"
            _Flowcontrolgrid_xmlCount=_util.FlowControlGrid_XmlCount()
            results = AddFlowControl()
            results.exec_()






    def tlbFlowControl_clik_enent(self):
        global _ClickX,_ClickY
        row=self.tlbFlowControl.currentRow()
        _ClickX = self.tlbFlowControl.item(row,0).text()
        _ClickY = self.tlbFlowControl.item(row, 1).text()

    def RemoveTalbeRow(self):
        global _Flowcontrolgrid_xmlCount , _Flowcontrolgrid_flag
        row = self.tlbFlowControl.currentIndex().row()
        # 선택된 Row 가 있을때
        if row > -1:
            mess = "Are you sure you want to delete the selected items?"
            result = QMessageBox.question(None, "Flow Control Grid", mess, QMessageBox.Yes, QMessageBox.No)
            if result == QMessageBox.Yes:
                # 사용자가 한번이라도 수정한 사항이 있으면 플래그값 True 로 변경하여 사용자 수정
                _Flowcontrolgrid_flag =True
                self.tlbFlowControl.removeRow(row)
    
                # 딕셔너리 삭제
                del GRM._xmltodict['GRMProject']['FlowControlGrid']
                DictoXml = xmltodict.unparse(GRM._xmltodict)
                ET.register_namespace('', "http://tempuri.org/GRMProject.xsd")
                xmltree = ET.ElementTree(ET.fromstring(DictoXml))
                root = xmltree.getroot()
                count = self.tlbFlowControl.rowCount()
                _Flowcontrolgrid_xmlCount = count
    
                for row in range(0, count):
                    child = ET.Element("FlowControlGrid")
                    root.append(child)
    
                    GridValue = ET.Element("ColX")
                    GridValue.text = self.tlbFlowControl.item(row, 0).text()
                    child.append(GridValue)
    
                    UserLandCover = ET.Element("RowY")
                    UserLandCover.text = self.tlbFlowControl.item(row, 1).text()
                    child.append(UserLandCover)
    
                    GRMLandCoverCode = ET.Element("Name")
                    GRMLandCoverCode.text = self.tlbFlowControl.item(row, 2).text()
                    child.append(GRMLandCoverCode)
    
                    DT = ET.Element("DT")
                    DT.text = self.tlbFlowControl.item(row, 3).text()
                    child.append(DT)
    
                    ControlType = ET.Element("ControlType")
                    ControlType.text = self.tlbFlowControl.item(row, 4).text()
                    child.append(ControlType)
    
                    FlowDataFile = ET.Element("FlowDataFile")
                    FlowDataFile.text = self.tlbFlowControl.item(row, 5).text()
                    child.append(FlowDataFile)
    
                    IniStorage = ET.Element("IniStorage")
                    if self.tlbFlowControl.item(row, 6).text() != "":
                        IniStorage.text = self.tlbFlowControl.item(row, 6).text()
                    else :
                        IniStorage.text=""
                    child.append(IniStorage)
    
                    MaxStorage = ET.Element("MaxStorage")
                    if self.tlbFlowControl.item(row, 7).text() != "":
                        MaxStorage.text = self.tlbFlowControl.item(row, 7).text()
                    else:
                        MaxStorage.text = ""
                    child.append(MaxStorage)
    
                    MaxStorageR = ET.Element("MaxStorageR")
                    if self.tlbFlowControl.item(row, 8).text() != "":
                        MaxStorageR.text = self.tlbFlowControl.item(row, 8).text()
                    else:
                        MaxStorageR.text=""
                    child.append(MaxStorageR)
    
                    ROType = ET.Element("ROType")
                    if self.tlbFlowControl.item(row, 9).text() != "":
                        ROType.text = self.tlbFlowControl.item(row, 9).text()
                    else:
                        ROType.text = ""
                    child.append(ROType)
    
                    ROConstQ = ET.Element("ROConstQ")
                    if self.tlbFlowControl.item(row, 10).text() != "":
                        ROConstQ.text = self.tlbFlowControl.item(row, 10).text()
                    else:
                        ROConstQ.text =""
                    child.append(ROConstQ)
    
                    ROConstQDuration = ET.Element("ROConstQDuration")
                    if self.tlbFlowControl.item(row, 11).text() != "":
                        ROConstQDuration.text = self.tlbFlowControl.item(row, 11).text()
                    else:
                        ROConstQDuration.text = ""
                    child.append(ROConstQDuration)
    
                xmltree_string = ET.tostring(xmltree.getroot())
                docs = dict(xmltodict.parse(xmltree_string))
                GRM._xmltodict.clear()
                GRM._xmltodict.update(docs)

                # 테이블에 값 셋팅후 화면에 점 표시

                self.post_grid_remove2()
                self.FlowContorGird_paint()
                if self.chkWatch_Point.isChecked():
                    self.watchpoint_paint()



    #     child = ET.Element("LandCover")
    #     root.append(child)
    #
    #     GridValue = ET.Element("GridValue")
    #     GridValue.text = self.tlbLandCover.item(row, 0).text()
    #     child.append(GridValue)
    #
    #     UserLandCover = ET.Element("UserLandCover")
    #     UserLandCover.text = self.tlbLandCover.item(row, 1).text()
    #     child.append(UserLandCover)
    #
    #     #             GRMLandCoverCode = ET.Element("GRMLandCoverCode")
    #     GRMLandCoverCode = ET.Element("GRMCode")
    #     GRMLandCoverCode.text = self.tlbLandCover.item(row, 2).text()
    #     child.append(GRMLandCoverCode)
    #
    #     GRMLandCoverE = ET.Element("GRMLandCoverE")
    #     GRMLandCoverE.text = self.tlbLandCover.item(row, 3).text()
    #     child.append(GRMLandCoverE)
    #
    #     GRMLandCoverK = ET.Element("GRMLandCoverK")
    #     GRMLandCoverK.text = self.tlbLandCover.item(row, 4).text()
    #     child.append(GRMLandCoverK)
    #
    #     RoughnessCoefficient = ET.Element("RoughnessCoefficient")
    #     RoughnessCoefficient.text = self.tlbLandCover.item(row, 5).text()
    #     child.append(RoughnessCoefficient)
    #
    #     ImperviousRatio = ET.Element("ImperviousRatio")
    #     ImperviousRatio.text = self.tlbLandCover.item(row, 6).text()
    #     child.append(ImperviousRatio)
    #
    # filepath = tempfile.mktemp()
    # xmltree.write(filepath)
    #
    # # Dictionary 초기화
    # GRM._xmltodict.clear()
    #
    # # 파일 읽어 오기
    # Projectfile = open(filepath, 'r')
    # data = Projectfile.read()
    # Projectfile.close()
    # # 읽어온 파일 내용(XML)을 dictionary 로 변경
    # docs = dict(xmltodict.parse(data))
    # GRM._xmltodict.update(docs)

    # ============================ Flow Control 탭 종료 ===============================================
#
#
    # ----------------- 2017-10-24_오전 박 Watershed Parmeters 탭 텍스트 박스 셋팅 -----------------------------
    def Set_Watershed_Parameter_tab_default(self):

        # Select watershed 콥보 박스 셋팅
        self.Set_Watershed_combo()

        self.SelectWsCombobox()
        self.cb_selectws.currentIndexChanged.connect(self.SelectWsCombobox)



    # 콤보 박스에 유역 설정 하기
    def Set_Watershed_combo(self):
        WS_list = []
        wscount=_wsinfo.WScount()
        AllItem=_wsinfo.WSIDsAll()

        for i in range(wscount):
            WS_list.append(str(AllItem[i]))

        self.cb_selectws.clear()
        self.cb_selectws.addItems(WS_list)







    # 콤보박스 선택시 하류 유역과 상류 유역의 콤보박스에 값 셋팅
    def SelectWsCombobox(self):

        # 2018-01-29 박: Watershed parmeter 함수 호출
        '''
        첫번째로 OpenProject 할때 처리 영역
        콤보 박스 셋팅 하기 전에 DLL에 선행 처리 해야 할 부분
            <ID>1</ID>
            <IniSaturation>1</IniSaturation>
            <MinSlopeOF>0.0001</MinSlopeOF>
            <MinSlopeChBed>0.0002</MinSlopeChBed>
            <MinChBaseWidth>50</MinChBaseWidth>
            <ChRoughness>0.055</ChRoughness>
            <DryStreamOrder>0</DryStreamOrder>
            <IniFlow>350</IniFlow>
            <CalCoefLCRoughness>1</CalCoefLCRoughness>
            <CalCoefPorosity>1</CalCoefPorosity>
            <CalCoefWFSuctionHead>1</CalCoefWFSuctionHead>
            <CalCoefHydraulicK>2</CalCoefHydraulicK>
            <CalCoefSoilDepth>1</CalCoefSoilDepth>
            <UserSet>true</UserSet>
        '''






        # 하류 유역 정보 셋팅
        selectWS=self.cb_selectws.currentText()
        DownSW = []
        Dllresult_Down=_wsinfo.downStreamWSIDs(int(selectWS))
        DownSW.extend(Dllresult_Down)
        if len(DownSW)>0:
            self.lisw_DownWS.clear()
            for i in range(len(DownSW)):
                item = QListWidgetItem(str(DownSW[i]))
                self.lisw_DownWS.addItem(item)

        # 상류 유역 정보 셋팅
        UPSW = []
        Dllresult_UP = _wsinfo.upStreamWSIDs(int(selectWS))
        UPSW.extend(Dllresult_UP)
        if len(UPSW)>0:
            self.lisw_UpWS.clear()
            for s in range(len(UPSW)):
                item1 = QListWidgetItem(str(UPSW[s]))
                self.lisw_UpWS.addItem(item1)

        self.ID = []; self.IniSaturation=[];self.MinSlopeOF=[];self.MinSlopeChBed=[]
        self.MinChBaseWidth=[]; self.ChRoughness=[]; self.DryStreamOrder=[]; self.IniFlow=[]
        self.CalCoefLCRoughness=[]; self.CalCoefPorosity=[]; self.CalCoefWFSuctionHead=[]; self.CalCoefHydraulicK=[]
        self.CalCoefSoilDepth=[];self.UserSet =[]


        doc = ET.parse(self.ProjectFile)
        root = doc.getroot()

        # 최하류 유역 Id 값
        StreamWSID = _wsinfo.mostDownStreamWSID()

        for element in root.findall('{http://tempuri.org/GRMProject.xsd}SubWatershedSettings'):
            self.ID.append(element.findtext("{http://tempuri.org/GRMProject.xsd}ID"))
            self.IniSaturation.append(element.findtext("{http://tempuri.org/GRMProject.xsd}IniSaturation"))
            self.MinSlopeOF.append(element.findtext("{http://tempuri.org/GRMProject.xsd}MinSlopeOF"))
            self.MinSlopeChBed.append(element.findtext("{http://tempuri.org/GRMProject.xsd}MinSlopeChBed"))
            self.MinChBaseWidth.append(element.findtext("{http://tempuri.org/GRMProject.xsd}MinChBaseWidth"))
            self.ChRoughness.append(element.findtext("{http://tempuri.org/GRMProject.xsd}ChRoughness"))
            self.DryStreamOrder.append(element.findtext("{http://tempuri.org/GRMProject.xsd}DryStreamOrder"))
            self.IniFlow.append(element.findtext("{http://tempuri.org/GRMProject.xsd}IniFlow"))
            self.CalCoefLCRoughness.append(element.findtext("{http://tempuri.org/GRMProject.xsd}CalCoefLCRoughness"))
            self.CalCoefPorosity.append(element.findtext("{http://tempuri.org/GRMProject.xsd}CalCoefPorosity"))
            self.CalCoefWFSuctionHead.append(element.findtext("{http://tempuri.org/GRMProject.xsd}CalCoefWFSuctionHead"))
            self.CalCoefHydraulicK.append(element.findtext("{http://tempuri.org/GRMProject.xsd}CalCoefHydraulicK"))
            self.CalCoefSoilDepth.append(element.findtext("{http://tempuri.org/GRMProject.xsd}CalCoefSoilDepth"))
            usersetString =element.findtext("{http://tempuri.org/GRMProject.xsd}UserSet")
            self.UserSet.append(usersetString)
            idsss = element.findtext("{http://tempuri.org/GRMProject.xsd}ID")
            if len(self.ID)>0:
                if usersetString.upper() == "TRUE" or str(StreamWSID) == idsss:
                    item1 = QListWidgetItem(element.findtext("{http://tempuri.org/GRMProject.xsd}ID"))
                    self.lisw_UserSet.addItem(item1)
        for i in range(len(self.ID)):
            if float(self.IniFlow[i])>0:
                flowFlage = True
            else:
                flowFlage = False

        # # 2018-01-30
        #     # wsid As Integer , iniSat As Single , minSlopeLandSurface As Single
        #     # , minSlopeChannel As Single , minChannelBaseWidth As Single , roughnessChannel As Single
        #     # , dryStreamOrder As Integer , ccLCRoughness As Single , ccSoilDepth As Single
        #     # , ccPorosity As Single , ccWFSuctionHead As Single , ccSoilHydraulicCond As Single
        #     # , applyIniFlow As Boolean , Optional iniFlow As Single = 0
        #     # 사용자가 Apply 버튼 눌렀을때 적용 하는거


            # _xml.ProjectLoad()
            # count=_xml.SubWatershedSettings_Count
            # if count>0:
                #  # 매개 변수 방식
                # _wsinfo.SetOneSWSParametersAndUpdateAllSWSUsingNetwork(int(self.ID[i]),float(self.IniSaturation[i]),float(self.MinSlopeOF[i])
                #                                                                  ,float(self.MinSlopeChBed[i]),float(self.MinChBaseWidth[i]),float(self.ChRoughness[i])
                #                                                                  ,int(self.DryStreamOrder[i]),float(self.CalCoefLCRoughness[i]),float(self.CalCoefSoilDepth[i])
                #                                                                  ,float(self.CalCoefPorosity[i]),float(self.CalCoefWFSuctionHead[i]),float(self.CalCoefHydraulicK[i])
                #                                                                  ,flowFlage,float(self.IniFlow[i]))
        _new_wsinfo = cGetWatershedInfo("C:/GRM/Sample/SampleProject.gmp")
        iniSaturation = str(_new_wsinfo.subwatershedPars(StreamWSID).iniSaturation)
        minSlopeChBed = str(_new_wsinfo.subwatershedPars(StreamWSID).minSlopeChBed)
        minSlopeOF = str(_new_wsinfo.subwatershedPars(StreamWSID).minSlopeOF)
        minChBaseWidth = str(_new_wsinfo.subwatershedPars(StreamWSID).minChBaseWidth)
        chRoughness = str(_new_wsinfo.subwatershedPars(StreamWSID).chRoughness)
        dryStreamOrder = str(_new_wsinfo.subwatershedPars(StreamWSID).dryStreamOrder)
        ccLCRoughness = str(_new_wsinfo.subwatershedPars(StreamWSID).ccLCRoughness)
        ccSoilDepth = str(_new_wsinfo.subwatershedPars(StreamWSID).ccSoilDepth)
        ccPorosity = str(_new_wsinfo.subwatershedPars(StreamWSID).ccPorosity)
        ccWFSuctionHead = str(_new_wsinfo.subwatershedPars(StreamWSID).ccWFSuctionHead)
        ccHydraulicK = str(_new_wsinfo.subwatershedPars(StreamWSID).ccHydraulicK)
        iniFlow = str(_new_wsinfo.subwatershedPars(StreamWSID).iniFlow)

        self.txtIniSaturation.setText(iniSaturation)
        self.txtMinSlopeOF.setText(minSlopeOF)
        self.txtMinSlopeChBed.setText(minSlopeChBed)
        # Allsize=self.txtGrid_Size.text()
        # intAll = float(Allsize)
        # cal_MinChBaseWidth = intAll/10
        self.txtMinChBaseWidth.setText(str(minChBaseWidth))
        self.txtIniFlow.setText(iniFlow)
        self.txtChRoughness.setText(chRoughness)
        self.txtDryStreamOrder.setText(dryStreamOrder)
        self.txtCalCoefLCRoughness.setText(ccLCRoughness)
        self.txtCalCoefSoilDepth.setText(ccSoilDepth)
        self.txtCalCoefPorosity.setText(ccPorosity)
        self.txtCalCoefWFSuctionHead.setText(ccWFSuctionHead)
        self.txtCalCoefHydraulicK.setText(ccHydraulicK)

        if float(iniFlow)>0:
            self.chkStream_flow.setChecked(True)
        else:
            self.chkStream_flow.setChecked(False)




            #
            # self.txtIniSaturation.setText("1")
            # self.txtMinSlopeOF.setText("0.001")
            # self.txtMinSlopeChBed.setText("0.001")
            # Allsize=self.txtGrid_Size.text()
            # intAll = float(Allsize)
            # cal_MinChBaseWidth = intAll/10
            # self.txtMinChBaseWidth.setText(str(cal_MinChBaseWidth))
            # self.txtIniFlow.setText("0")
            # self.txtChRoughness.setText("0.045")
            #
            #
            # self.txtDryStreamOrder.setText("0")
            # self.txtCalCoefLCRoughness.setText("1")
            # self.txtCalCoefSoilDepth.setText("1")
            # self.txtCalCoefPorosity.setText("1")
            # self.txtCalCoefWFSuctionHead.setText("1")
            # self.txtCalCoefHydraulicK.setText("1")


        # if len(self.ID) > 0:
        #     for i in rang(len(self.ID)):
        #         if usersetString.upper() == "TRUE":
        #             self.ID[i]
        #             self.IniSaturation
        #             self.MinSlopeOF
        #             self.MinSlopeChBed
        #             self.MinChBaseWidth
        #             self.ChRoughness
        #             self.DryStreamOrder
        #             self.IniFlow
        #             self.CalCoefLCRoughness
        #             self.CalCoefPorosity
        #             self.CalCoefWFSuctionHead
        #             self.CalCoefHydraulicK
        #             self.CalCoefSoilDepth
        #             self.UserSet


















    # ============================ Watershed Parmeters 탭 종료 =================================================
#
#     # 컬러 피커 이벤트 연결
#     def Set_ColorPicker_event(self):
#         # 색상변경 버튼-- colorPicker
#         self.btnColorPicker.clicked.connect(lambda:self.color_picker(self.btnColorPicker,"watchpoint"))
#         #qt 에서 배경색 미리 지정해 두었음.
#         self.btnColorPicker_2.clicked.connect(lambda:self.color_picker(self.btnColorPicker_2,"channel"))
#         self.btnColorPicker_3.clicked.connect(lambda:self.color_picker(self.btnColorPicker_3,"flow"))
#
#
    # 색상 변경 Picker -- 2017/09/07  조가 주석달음
    def color_picker(self, bttom, type):
        color = QtGui.QColorDialog.getColor()
        bttom.setStyleSheet("background-color:" + str(color.name()) + ";");

        if type == "watchpoint":
            #중복되서 생성하지 못하게 기존의 루버밴드를 제거하고 새로 생성
            self.post_grid_remove2()
            self.watchpoint()
            # 나중에 기능 추가 할 예정임
            # elif type == "channel":
            #
            # elif type == "flow":

    # 폼 종료
    def Close_Form(self):
        self.close()

    def closeEvent(self, ev):
        QtGui.QDialog.closeEvent(self, ev)
        global _FXCOL, _FYROW
        _FXCOL = 0
        _FYROW = 0

#
#     def Click_StartSimulation(self):
#         # simulation 탭=====================================================
#         GRM._xmltodict['GRMProject']['ProjectSettings']['GridCellSize']=self.txtGrid_Size.text()
#         # self.txtCellCount.setText("test")
#         GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallInterval']= self.txtRainfall_intval.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['ComputationalTimeStep'] = self.txtTimeStep_1.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['SimulationDuration'] = self.txtSimulation_duration.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['OutputTimeStep'] = self.txtOutput_time_step.text()
#
#         if self.chkInfiltration.isChecked():
#             GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateInfiltration'] = 'true'
#         else:
#             GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateInfiltration'] = 'false'
#
#         if self.chkSubsurfaceFlow.isChecked():
#             GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateSubsurfaceFlow'] = 'true'
#         else:
#             GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateSubsurfaceFlow'] = 'false'
#
#         if self.chkBaseFlow.isChecked():
#             GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateBaseFlow'] = 'true'
#         else:
#             GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateBaseFlow'] = 'false'
#
#         if self.chkFlowControl.isChecked():
#             GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateFlowControl'] = 'true'
#         else:
#             GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateFlowControl'] = 'false'
#
#
#         # chanel CS tab==============================================================================
#         GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQc'] = self.txt_c.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQd'] = self.txt_d.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQe'] = self.txt_e.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthMostDownStream'] = self.txt_douwnstream.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['LowerRegionHeight'] = self.txtLower_Region_Height.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['LowerRegionBaseWidth'] = self.txtLower_Region_Base_Width.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['UpperRegionBaseWidth'] = self.txtUpper_Region_Base_Width.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['CompoundCSChannelWidthLimit'] = self.txtCompound_CSChannel_Width_Limit.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['BankSideSlopeRight'] = self.txtRight_bank.text()
#         GRM._xmltodict['GRMProject']['ProjectSettings']['BankSideSlopeLeft'] = self.txtLeft_bank.text()
#
#         # Watershed Parmeters 탭
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['IniSaturation'] = self.txtIniSaturation.text()
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinSlopeOF']=self.txtMinSlopeOF.text()
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinSlopeChBed']=self.txtMinSlopeChBed.text()
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinChBaseWidth']=self.txtMinChBaseWidth.text()
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['ChRoughness']=self.txtChRoughness.text()
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['DryStreamOrder']=self.txtDryStreamOrder.text()
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['IniFlow']=self.txtIniFlow.text()
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefLCRoughness']=self.txtCalCoefLCRoughness.text()
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefSoilDepth']=self.txtCalCoefSoilDepth.text()
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefPorosity']=self.txtCalCoefPorosity.text()
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefWFSuctionHead']=self.txtCalCoefWFSuctionHead.text()
#         GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefHydraulicK']=self.txtCalCoefHydraulicK.text()
#         # ====================== 20171102 박: 시뮬레이션 시작 버튼 이벤트 처리 종료================================
#         self.SaveProjectFile()
#         Projectfile = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
#         exeFile = os.path.dirname(os.path.abspath(__file__)) + "\GRM.exe"
#         arg = '"' + exeFile + '"' + " " + '"' + Projectfile + '"'
#         _util.Execute(arg)
#         _util.MessageboxShowInfo("FIN","FIN")
#
#
#     def SaveProjectFile(self):
#         # 현재 변경된 XML 자료를 파일에 덮어 씌우는 부분
#         Projectfile = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
#         DictoXml = xmltodict.unparse(GRM._xmltodict)
#         fw = open(Projectfile, 'w+')
#         fw.write(DictoXml)
#         fw.close()
#
#     def chkStream_state(self,b):
#         if b.isChecked() == True:
#             self.txtIniFlow.setDisabled(True)
#         else:
#             self.txtIniFlow.setDisabled(False)
#
    def identify(self):
         # 캔버스 휠까지 처리 됨
         self.tool.scale_changed()
         self.mapcanvas.setMapTool(self.tool)

    def watchpoint(self):
        if self.chkWatch_Point.isChecked():
            self.watchpoint_paint()
        else:
            # 지우기
            self.post_grid_remove2()
            if self.chkFlowContorGird.isChecked():
                self.FlowContorGird_paint()

    def click_FlowContorGird(self):
        if self.chkFlowContorGird.isChecked():
            self.FlowContorGird_paint()
        else:
            # 지우기
            self.post_grid_remove2()
            if self.chkWatch_Point.isChecked():
                self.watchpoint_paint()

    # 그리드 라인 함수
    def show_hide_grid_line(self):
        if self.show_grid_line.isChecked():
            self.add_grid_layer()
        else:
            self.remove_grid_layer()

    def add_grid_layer(self):
        # if _grid_line !={}:
        if self.grid_line is None:
            self.grid_line.setLayerTransparency(0)
            self.mapcanvas.refresh()
            if self.flow_direction_layer:
                self.mapcanvas.setLayerSet([QgsMapCanvasLayer(self.flow_direction_layer),QgsMapCanvasLayer(self.grid_line), QgsMapCanvasLayer(self.layer)])
        else:
            # global _grid_line
            # _grid_line = get_point_layer(self.layer, self.mapcanvas)
            self.grid_line = get_point_layer(self.layer, self.mapcanvas)
            QgsMapLayerRegistry.instance().addMapLayer(self.grid_line, False)
            self.layer.extent().combineExtentWith(self.grid_line.extent())
            self.mapcanvas.setExtent(self.mapcanvas.extent())

            # ========= 2017/11/10 : 기본적으로 Grid line 단일 체크시 Grid line 만 표현,flow direction 체크 시 flow direction 함께 표시
            self.mapcanvas.setLayerSet([QgsMapCanvasLayer(self.grid_line), QgsMapCanvasLayer(self.layer)])

            if self.flow_direction:
                self.mapcanvas.setLayerSet([QgsMapCanvasLayer(self.flow_direction),QgsMapCanvasLayer(self.grid_line), QgsMapCanvasLayer(self.layer)])
            # ========= 2017/11/10 : 기본적으로 Grid line 단일 체크시 Grid line 만 표현,flow direction 체크 시 flow direction 함께 표시

            # # 여기는 처음 시작 했을때
            # self.point_layer = get_point_layer(self.layer, self.mapcanvas)
            # global _grid_line
            # _grid_line = self.point_layer
            # QgsMapLayerRegistry.instance().addMapLayer(self.point_layer, False)
            # self.layer.extent().combineExtentWith(self.point_layer.extent())
            # self.mapcanvas.setExtent(self.mapcanvas.extent())
            #
            # # ========= 2017/11/10 : 기본적으로 Grid line 단일 체크시 Grid line 만 표현,flow direction 체크 시 flow direction 함께 표시
            # self.mapcanvas.setLayerSet([QgsMapCanvasLayer(self.point_layer), QgsMapCanvasLayer(self.layer)])
            #
            # if self.flow_direction_layer:
            #     self.mapcanvas.setLayerSet([QgsMapCanvasLayer(self.flow_direction_layer),QgsMapCanvasLayer(self.point_layer), QgsMapCanvasLayer(self.layer)])
            # # ========= 2017/11/10 : 기본적으로 Grid line 단일 체크시 Grid line 만 표현,flow direction 체크 시 flow direction 함께 표시


    def remove_grid_layer(self):

        # 기존 레이어 삭제 소스는 flow direction 까지 지워버리는 바람에 신규 레이어 삭제 소스로 Grid line만 삭제하도록 함
        #신규 레이어 삭제 소스
        self.grid_line.setLayerTransparency(100)
        self.mapcanvas.refresh()


    # 플로우 디렉션
    def show_hide_flow_direction(self):
        if self.show_flow_direction.isChecked():
            self.show_flow_directions()
        else:
            self.hide_flow_direction()

    def show_flow_directions(self):
        if self.flow_direction is None:
            self.flow_direction.setLayerTransparency(0)
            self.mapcanvas.refresh()
        else:
            # global _flow_direction
            FD = GRM._xmltodict['GRMProject']['ProjectSettings']['FlowDirectionFile']
            ST = GRM._xmltodict['GRMProject']['ProjectSettings']['StreamFile']
            self.layer2 = QgsRasterLayer(FD, "FD", "gdal")
            self.layer3 = QgsRasterLayer(ST, "ST", "gdal")

            self.flow_direction = get_flow_layer(self.layer2, self.mapcanvas, self.layer3)

            #  신규 소스
    #         self.flow_direction_layer = get_flow_layer(self.layer2, self.mapcanvas, self.layer3)
            QgsMapLayerRegistry.instance().addMapLayer(self.flow_direction, False)

            # 기존 소스
            QgsMapLayerRegistry.instance().addMapLayer(self.flow_direction, False)
            self.layer.extent().combineExtentWith(self.flow_direction.extent())

            # ========= 2017/11/10 : 기본적으로 flow direction 단일 체크시 다음 flow direction 만 표현,Grid line 체크 시 grid line 함께 표시
            self.mapcanvas.setLayerSet([QgsMapCanvasLayer(self.flow_direction), QgsMapCanvasLayer(self.layer)])
            if self.grid_line:
                self.mapcanvas.setLayerSet([QgsMapCanvasLayer(self.grid_line),QgsMapCanvasLayer(self.flow_direction),QgsMapCanvasLayer(self.layer)])
            # ========= 2017/11/10 : 기본적으로 flow direction 단일 체크시 다음 flow direction 만 표현,Grid line 체크 시 grid line 함께 표시


    def hide_flow_direction(self):
        self.flow_direction.setLayerTransparency(100)
        self.mapcanvas.refresh()

    def ReMove(self):
            row = self.tbList.currentIndex().row()
            mess="Are you sure you want to delete the selected items?"
            result=QMessageBox.question(None, "Watershed Setup",mess,QMessageBox.Yes, QMessageBox.No)
            if result == QMessageBox.Yes:
                self.tbList.removeRow(row)

    def MoveUp(self):
        fixcount=len(self.Fixed)
        row = self.tbList.currentRow()
        column = self.tbList.currentColumn()
        if row > 0:
            if row-1 > fixcount-1:
                self.tbList.insertRow(row - 1)
                for i in range(self.tbList.columnCount()):
                    self.tbList.setItem(row - 1, i, self.tbList.takeItem(row + 1, i))
                    self.tbList.setCurrentCell(row - 1, column)
                self.tbList.removeRow(row + 1)

    def MoveDown(self):
        fixcount=len(self.Fixed)
        row = self.tbList.currentRow()
        column = self.tbList.currentColumn()
        if row < self.tbList.rowCount() - 1:
            if row > fixcount-1:
                self.tbList.insertRow(row + 2)
                for i in range(self.tbList.columnCount()):
                    self.tbList.setItem(row + 2, i, self.tbList.takeItem(row, i))
                    self.tbList.setCurrentCell(row + 2, column)
                self.tbList.removeRow(row)

    #2017 -12-15 박: 추가 버튼 눌렀을때 Watchpoint table 에 데이터 추가 하기 
    def Add_Selected_Cell(self):
        if _XCOL !=0 and _YROW!=0:
            rowCount = self.tbList.rowCount()
            if rowCount >0:
                self.tbList.insertRow(rowCount)
                #박 :2017 - 12 -21  1. name , 2. ColX , 3. RowY
                text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter name:',QLineEdit.Normal,"")
                self.tbList.setItem(rowCount, 0, QTableWidgetItem(text))
                self.tbList.setItem(rowCount, 1, QTableWidgetItem(str(_XCOL)))
                self.tbList.setItem(rowCount, 2, QTableWidgetItem(str(_YROW)))

            else:

                self.tbList.insertRow(0)
                text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter name:',QLineEdit.Normal,"")
                self.tbList.setItem(rowCount, 0, QTableWidgetItem(text))
                self.tbList.setItem(0, 1, QTableWidgetItem(str(_XCOL)))
                self.tbList.setItem(0, 2, QTableWidgetItem(str(_YROW)))

    # 에디트 클릭시에 선택된 Row 의 name 변경
    def Edit(self):
        # 현재 선택된 Row
        row=self.tbList.currentRow()
        cell = self.tbList.item(row, 1).text()
        # 다이얼 로그 출력하여 사용자가 셀값 제정의
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter name:',QLineEdit.Normal,cell)
        if ok:
            item = QTableWidgetItem(str(text))  # create a new Item
            self.tbList.setItem(row, 1, item)

#
#     # 2017/11/22 -----------------------------임시.. 불완전
#
    #테이블의 Row cols의 위치로 view 이동
    def GoToGrid(self):
        row = self.tbList.currentRow()
        ColX = self.tbList.item(row, 4).text()
        RowY = self.tbList.item(row, 5).text()

        self.row_cols_grid(self.layer,ColX,RowY,None)
        self.scale_changed_mapcanvas()
        # self.row_cols_grid(self.layer, self.txt_xColyRowNo_1.text(), self.txt_xColyRowNo_2.text(), None)

#     # 2017/11/22 -----------------------------임시.. 불완전
#
#
#     def reset(self):
#         self.startPoint = self.endPoint = None
#         self.isEmittingPoint = False
#         self.rubberBand.reset(QGis.Polygon)
#
#

    def FlowContorGird_paint(self):
        counts = self.tlbFlowControl.rowCount()
        for i in range(0,counts):
            xvalue = _xmin + _xsize / 2 + _xsize * (int(self.tlbFlowControl.item(i, 0).text()))
            yvalue = _ymax - _ysize / 2 - _ysize * (int(self.tlbFlowControl.item(i, 1).text()))
            self.draw_grid2(xvalue,yvalue,self.btnColorPicker_3)

    def watchpoint_paint(self):
        if len(self.ColX)>0 and len(self.RowY)>0:
            for i in range(0,len(self.ColX)):
                self.row_cols_grid(self.ColX[i],self.RowY[i],"watchpoint")


    def Watchpoint_TableCreate(self,Row):
        self.tbList.setColumnCount(3)
        self.tbList.setRowCount(Row)
        self.tbList.setHorizontalHeaderLabels( ['Name','ColX', 'RowY'])
        #테이블 넓이 에 맞게 Name 항목 넓이 지정 
        self.tbList.setColumnWidth(0,176)
        
        
    # Channel CS  --2017/09/08 조
    # 라디오 버튼 클릭 시 활성/비활성 함수
    def ChannelCS_rdo_able(self):
        # 활성 상태

        if self.rdo_single.isChecked():
            # Compound Cross Section 비활성 상태
#             self.rdo_compound.setDisabled(True)
            self.groupBox_6.setDisabled(True)
            self.groupBox_2.setDisabled(False)

            # Use channel width equation 활성 상태인 경우
            if self.rdo_useCh.isChecked():
#                 self.rdo_generateCh.setDisabled(True)
                self.txt_douwnstream.setDisabled(True)
                self.txt_c.setDisabled(False)
                self.txt_d.setDisabled(False)
                self.txt_e.setDisabled(False)

            # Use channel width equation 비활성 상태인 경우
            elif self.rdo_generateCh.isChecked():
#                 self.rdo_generateCh.setDisabled(False)
                self.txt_douwnstream.setDisabled(False)
                self.txt_c.setDisabled(True)
                self.txt_d.setDisabled(True)
                self.txt_e.setDisabled(True)

        # single cross section 라디오 버튼이 비활성 상태 일 때
        elif self.rdo_compound.isChecked():
            self.rdo_compound.setDisabled(False)
            self.groupBox_6.setDisabled(False)
            self.groupBox_2.setDisabled(True)


    # channal width
    # def btnChage_click(self):
    #     self.draw_grid2( _Cnavas_Click_X, _Cnavas_Click_Y,self.btnColorPicker_2)

    # # channal CS 마지막 사각형 지우기
    # def btInitilalize_click(self):
    #     ru = []
    #     for v in self.mapcanvas.scene().items():
    #         if type(v) == QgsRubberBand:
    #             ru.append(v)
    #     self.mapcanvas.scene().removeItem(ru[0])


    def btInitilalize_All_click(self):
        for key in self.rbDict.keys():
            self.mapcanvas.scene().removeItem(self.rbDict[key])
            del self.rbDict[key]


    # Qdilog 창에 Qtablewidget 셋팅
    def aboutApp(self):
#         global _SelectRow
#         _SelectRow= row
        website = "http://code.google.com/p/comictagger"
        email = "comictagger@gmail.com"
        # license_link = "http://www.apache.org/licenses/LICENSE-2.0"
        # license_name = "Apache License 2.0"
        Project = "test"
        msgBox = QtGui.QMessageBox()
        msgBox.addButton("OK",QtGui.QMessageBox.AcceptRole)
        msgBox.addButton("Cancel",QtGui.QMessageBox.RejectRole)
        msgBox.setWindowTitle(self.tr("Move to grid"))
        msgBox.setTextFormat(QtCore.Qt.RichText)
        msgBox.setIconPixmap(QtGui.QPixmap(Project))
        #msgBox.setText("<br><br><br><br><br><br><br><font color=white>"+"{0},{1}</font><br><br>".format(website,email))
        msgBox.setText("<br><br><br><br><br><br><pre>                                                   </pre>")
        self.addGroupWidget(msgBox)

        ret=msgBox.exec_()
        #-----------------------------2017/10/30---------------
        if ret == QtGui.QMessageBox.AcceptRole:
            self.post_grid_remove()
            self.rdo_selection()
            self.mapcanvas.refresh()
            self.scale_changed_mapcanvas()
            self.tool.scale_changed_disconnect()
            # self.tool = CanvasTool(self.mapcanvas).scale_changed_disconnect()
            # self.mapcanvas.setMapTool(tool)

        else:
            pass

    #Create TableWidget
    def addGroupWidget (self, parentItem) :
        self.groupWidget = QtGui.QGroupBox(parentItem)
#         self.groupWidget.setTitle("groupWidget") #그룹 박스 타이틀, 쓰지 않음
        self.groupWidget.setGeometry (QtCore.QRect(20, 30, 360, 115)) #사이즈
        self.groupWidget.setObjectName ('groupWidget')

        #라디오 버튼, move to grid, xCol No, yRow No
        self.rdo_xColyRowNo = QtGui.QRadioButton("xCol No, yRow No", self.groupWidget)
        # 사용자에게 보여 주지 않음
        # self.rdo_CVID = QtGui.QRadioButton("CVID", self.groupWidget)
        self.rdo_xy = QtGui.QRadioButton("x, y", self.groupWidget)

        #텍스트 박스
        self.txt_xColyRowNo_1 = QtGui.QLineEdit(self.groupWidget)
        self.txt_xColyRowNo_2 = QtGui.QLineEdit(self.groupWidget)
        # self.txt_CVID=QtGui.QLineEdit(self.groupWidget)
        self.txt_xy1 = QtGui.QLineEdit(self.groupWidget)
        self.txt_xy2 = QtGui.QLineEdit(self.groupWidget)


        #위치 정의 setGeometry(x,y,w,h)
        self.rdo_xColyRowNo.setGeometry(30,20,150,30)
        self.rdo_xy.setGeometry(30,60,150,30)
        self.txt_xColyRowNo_1.setGeometry(170,25,75,20)
        self.txt_xColyRowNo_2.setGeometry(255,25,75,20)
        self.txt_xy1.setGeometry(170,65,75,20)
        self.txt_xy2.setGeometry(255,65,75,20)
#         self.btn_OK.setGeometry(180,150,80,25)
#         self.btn_Cancel.setGeometry(265,150,80,25)

        #버튼별 이벤트
        #1. rdo_xColyRowNo가 체크 시 그 외 비활성화
        self.rdo_xColyRowNo.setChecked(True)
        # self.rdo_CVID.setChecked(False)
        self.rdo_xy.setChecked(False)
        # self.txt_CVID.setDisabled(True)
        self.txt_xy1.setDisabled(True)
        self.txt_xy2.setDisabled(True)
        #라디오 버튼 이벤트, 함수는 나중에 수정 바람... 2017/10/19 Cho
        self.rdo_xColyRowNo.clicked.connect(self.disableFunction)
        # self.rdo_CVID.clicked.connect(self.disableFunction)
        self.rdo_xy.clicked.connect(self.disableFunction)

    def disableFunction(self):
        if self.rdo_xColyRowNo.isChecked()==True:
            self.txt_xColyRowNo_1.setDisabled(False)
            self.txt_xColyRowNo_2.setDisabled(False)
            # self.txt_CVID.setDisabled(True)
            self.txt_xy1.setDisabled(True)
            self.txt_xy2.setDisabled(True)

        # elif self.rdo_CVID.isChecked():
        #     # self.txt_CVID.setDisabled(False)
        #     self.txt_xColyRowNo_1.setDisabled(True)
        #     self.txt_xColyRowNo_2.setDisabled(True)
        #     self.txt_xy1.setDisabled(True)
        #     self.txt_xy2.setDisabled(True)

        elif self.rdo_xy.isChecked():
            self.txt_xColyRowNo_1.setDisabled(True)
            self.txt_xColyRowNo_2.setDisabled(True)
            # self.txt_CVID.setDisabled(True)
            self.txt_xy1.setDisabled(False)
            self.txt_xy2.setDisabled(False)

    def rdo_selection(self):
        #col, row 입력
        if self.rdo_xColyRowNo.isChecked():
            gird=self.row_cols_grid(self.txt_xColyRowNo_1.text(),self.txt_xColyRowNo_2.text(),None)
            # srtCvid=self.MgetCVID(self.txt_xColyRowNo_1.text(), self.txt_xColyRowNo_2.text(),"xColyRowNo")
            # self.lblCvid.setText("Cvid :" +str(srtCvid))

        #xy 입력
        elif self.rdo_xy.isChecked():
            self.xy_grid(self.layer,self.txt_xy1.text(),self.txt_xy2.text())
            x = self.txt_xy1.text()
            y =self.txt_xy2.text()
            # srtCvid = self.MgetCVID(float(x),float(y), "xy")
            # self.lblCvid.setText("Cvid :" +str(srtCvid))

        # elif self.rdo_CVID.isChecked():
        #     self.lblCvid.setText("Cvid :" + str(self.txt_CVID.text()))
        #     # list=self.outpoint(self.txt_CVID.text())
        #     self.xy_grid(self.layer,list[0],list[1])

    #1. row/cols로 마커
    def row_cols_grid(self,row,column,type):
        row = int(row)
        column=int(column)
        if row < 0 or column < 0 or _height<=column or _width <= row :
            row = "out of extent"
            column="out of extent"
            _util.MessageboxShowInfo("row","{0}, {1}".format(str(row),str(column)))
        else:
            if type == "watchpoint":
                Cell_X_Center2 = _xmin + _xsize/2 + _xsize * (row)
                Cell_Y_Center2 =  _ymax -  _ysize/2 -  _ysize * (column)
                if Cell_X_Center2<= _xmax or _xmin<=Cell_X_Center2 or Cell_Y_Center2<=_ymax or _ymin<=Cell_Y_Center2:
                    self.draw_grid2(Cell_X_Center2, Cell_Y_Center2,self.btnColorPicker)
            else:
                self.lblColRow.setText("xCol, yRow:" + str(row) + " , " + str(column))
                Cell_X_Center1 = _xmin+ _xsize/2 + _xsize * (row)
                Cell_Y_Center1 =  _ymax -  _ysize/2 -  _ysize * (column)

                # _util.MessageboxShowInfo("point x,y ", "{0} : {1} ".format(str(Cell_X_Center1), str(Cell_Y_Center1)))

                if Cell_X_Center1<= _xmax or xmin<=Cell_X_Center1 or Cell_Y_Center1<=_ymax or _ymin<=Cell_Y_Center1:
                    oldExtent = self.mapcanvas.extent()

                    x1n = Cell_X_Center1 - oldExtent.width()/2.0
                    x2n = Cell_X_Center1 + oldExtent.width()/2.0
                    y1n = Cell_Y_Center1 - oldExtent.height()/2.0
                    y2n = Cell_Y_Center1 + oldExtent.height()/2.0

                    self.mapcanvas.setExtent(QgsRectangle(x1n, y2n, x2n, y1n))

                    # for v in self.mapcanvas.scene().items():
                    #     if issubclass(type(v), QgsVertexMarker) == True:
                    #         self.mapcanvas.scene().removeItem(v)

                    # if self.mapcanvas.scene().items()

                    self.draw_grid(Cell_X_Center1, Cell_Y_Center1)

                    # return
                    #
                    # global Cell_X_Center1,Cell_Y_Center1
                    # #2017/11/22 ----------------------------
                    # # 여기서 해당 위치로 view 이동이 되어야 함
                    # #이동은 되는데 Scale에 맞춰서 크기 조절은 안되고 있음
                    # x1= Cell_X_Center1- _xsize ; x2 = Cell_X_Center1+ _xsize ; y1 = Cell_Y_Center1 + _ysize; y2 = Cell_Y_Center1 - _ysize
                    # scale = self.mapcanvas.scale()
                    # xln= Cell_X_Center1 -(x2 - x1) /2.0
                    # xrn= Cell_X_Center1 +(x2 - x1) /2.0
                    # yln= Cell_Y_Center1 -(y2 - y1) /2.0
                    # yrn= Cell_Y_Center1 +(y2 - y1) /2.0
                    #
                    # # xln = Cell_X_Center1 - (x2 - x1) / scale
                    # # xrn = Cell_X_Center1 + (x2 - x1) / scale
                    # # yln = Cell_Y_Center1 - (y2 - y1) / scale
                    # # yrn = Cell_Y_Center1 + (y2 - y1) / scale
                    # # _util.MessageboxShowInfo("QGsRectangle","{0} , {1}, {2}, {3}".format(str(xln), str(yln), str(xrn), str(yrn)))
                    # # _util.MessageboxShowInfo("QGsRectangle","{0} , {1}, {2}, {3}".format(str(x1), str(y1), str(x2), str(y2)))
                    #
                    # self.mapcanvas.setExtent(QgsRectangle(xln, yln, xrn, yrn))
                    # # 2017/11/22 ---------------------------- 아직 완벽하지 않음







    #2. xy좌표로
    def xy_grid(self,layer,xcoord,ycoord):
         # _util.MessageboxShowInfo("xcoord, ycoord","{0} : {1}".format(str(xcoord),str(ycoord)))
        xcoord=float(xcoord); ycoord=float(ycoord)

        row = int(((_ymax - ycoord) / _ysize))
        column = int(((xcoord - _xmin) / _xsize))
        self.lblColRow.setText("xCol, yRow:" + str(column) + " , " + str(row))

        #============= 2017/11/02 조 : row, cols 식 변경 되어 조건문 변경
        if row < 0 or column < 0 or _height<=column or _width <= row :
        #============= 2017/11/02 조 : row, cols 식 변경 되어 조건문 변경
            row = "out of extent"
            column="out of extent"
            _util.MessageboxShowInfo("Out of Range", "{0}, {1}".format(str(column), str(row)))
        else:
            global Cell_X_Center1,Cell_Y_Center1
            Cell_X_Center1 = _xmin + _xsize/2 + _xsize * (column)
            Cell_Y_Center1 =  _ymax -  _ysize/2 -  _ysize * (row) #(extent.yMinimum())
            if Cell_X_Center1<= _xmax or _xmin<=Cell_X_Center1 or Cell_Y_Center1<=_ymax or _ymin<=Cell_Y_Center1:
                self.draw_grid(Cell_X_Center1,Cell_Y_Center1)

     #이전 grid 지우기
    def post_grid_remove(self):
        for v in self.mapcanvas.scene().items():
            if issubclass(type(v), QgsVertexMarker) == True:
                self.mapcanvas.scene().removeItem(v)


    # watchpoint RubberBand 제거
    def post_grid_remove2(self):
        for v in self.mapcanvas.scene().items():
            if issubclass(type(v), QgsRubberBand) == True:
                self.mapcanvas.scene().removeItem(v)

         #grid 그리기
    def draw_grid(self,x,y):
        marker = QgsVertexMarker(self.mapcanvas)
        marker.setCenter(QgsPoint(float(x),float(y)))

        marker.setColor(QColor(255,0,0))
        scale = self.mapcanvas.scale()
         #사이즈 조절함. 가능한 맞게 조정함
        size = 750000.0 / scale
        marker.setIconSize(size)
        marker.setIconType(QgsVertexMarker.ICON_BOX)
        marker.setPenWidth(1)
        return marker

     # Watch point 그림을 Rubberbanc로 처리 함
    def draw_grid2(self,x,y,btn):
        r = QgsRubberBand(self.mapcanvas, True)
        points = [[QgsPoint(x - 100, y + 100), QgsPoint(x - 100, y - 100), QgsPoint(x + 100, y - 100),
                   QgsPoint(x + 100, y + 100)]]
        r.setToGeometry(QgsGeometry.fromPolygon(points), None)
        r.setColor(QColor(btn.palette().button().color()))
        r.setWidth(2)


     # ================== 2017/11/6 조
     #scale에 따라 Marker 크기 변화 --  Canvastool class 별개 함수
    def scale_changed_mapcanvas(self):
        self.mapcanvas.scaleChanged.connect(self.scale_change_vertexMarker)

    def scale_change_vertexMarker(self):
        global Cell_X_Center1,Cell_Y_Center1
        self.post_grid_remove()
        self.draw_grid(Cell_X_Center1,Cell_Y_Center1)
     # ================== 2017/11/6 조

    def outpoint(self, id):
       cvid_v = 0
       for c in range(_width):
           for r in range(_height):
               xxx = r * _xsize + _xmin
               yyy = _ymax - c * _ysize
               ident = self.layer.dataProvider().identify(QgsPoint(xxx, yyy), QgsRaster.IdentifyFormatValue)

               if ident.results()[1] > 0:
                   cvid_v = (cvid_v + 1)
               if int(id) == cvid_v:
                   return xxx, yyy

    def MgetCVID(self, R, C,type):
        cvid_v = 0
        if(type== "xColyRowNo"):
            Rt = int(R) ; Ct= int(C)
        elif (type == "xy"):
            Rt,Ct = self.Point_To_RowColumn(R,C)

         # _util.MessageboxShowInfo("Rt,Ct",str(Rt) + " : " + str(Ct))
        for c in range(_width):
            for r in range(Ct):
                xxx = c * _xsize + _xmin
                yyy = _ymax - r * _ysize
                ident = _layer.dataProvider().identify(QgsPoint(xxx, yyy), QgsRaster.IdentifyFormatValue)
                if ident.results().values()[0] > 0:
                    cvid_v = (cvid_v + 1)
        cvid = 0
        for cs in range(Rt + 1):
            for rs in range(Ct, Ct + 1):
                xxx = cs * _xsize + _xmin
                yyy = _ymax - rs * _ysize
                ident = _layer.dataProvider().identify(QgsPoint(xxx, yyy), QgsRaster.IdentifyFormatValue)
                if ident.results().values()[0] > 0:
                    cvid = (cvid + 1)
        return cvid_v + cvid

    def Point_To_RowColumn(self,x,y):
        column = int(((_ymax - y) / _ysize))
        row = int(((x - _xmin) / _xsize))
        return row,column


class CanvasTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas

    def scale_changed(self):
        self.canvas.scaleChanged.connect(self.scale_change_marker)

    def scale_changed_disconnect(self):
        self.canvas.scaleChanged.disconnect(self.scale_change_marker)

     #canvas scale이 변화할 때  marker를 새로 그림
    def scale_change_marker(self):
        global Cell_X_Center,Cell_Y_Center
        self.post_vertex_remove()
        self.create_vertex(Cell_X_Center,Cell_Y_Center)

     #이전에 생성한 vertexMaker제거 함
    def post_vertex_remove(self):
        for v in self.canvas.scene().items():
            if issubclass(type(v), QgsVertexMarker):
                self.canvas.scene().removeItem(v)

    def create_vertex(self,x,y):
        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(QgsPoint(x,y))
        marker.setColor(QColor(255,0,0))
        scale = self.canvas.scale()
        size = 750000.0 / scale
        marker.setIconSize(size)
        marker.setIconType(QgsVertexMarker.ICON_BOX)
        marker.setPenWidth(1)


    def getCVID(self, Rt, Ct):
        cvid_v = 0

        for c in range(_width):
            for r in range(Ct):
                xxx = c * _xsize + _xmin
                yyy = _ymax - r * _ysize
                ident = _layer.dataProvider().identify(QgsPoint(xxx, yyy), QgsRaster.IdentifyFormatValue)
                if ident.results().values()[0] >0:
                    cvid_v = ( cvid_v+1 )
        cvid = 0
        for cs in range(Rt+ 1):
            for rs in range(Ct,Ct+1):
                xxx = cs * _xsize + _xmin
                yyy = _ymax - rs * _ysize
                ident = _layer.dataProvider().identify(QgsPoint(xxx, yyy), QgsRaster.IdentifyFormatValue)
                if ident.results().values()[0] > 0:
                    cvid = (cvid + 1)
        return cvid_v + cvid

     # 캔버스 클릭 이벤트 좌표 출력
    def canvasPressEvent(self, event):
        xx = event.pos().x()
        yy = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(xx,yy)
        if _layer is not None:
            global _CVID , _XCOL , _YROW , _FYROW , _FXCOL
            row ,column  = self.Point_To_RowColumn(point)
            _CVID = "Cvid: " + str(self.getCVID(row, column))
            _XCOL =  column
            _YROW = row

            _FYROW =_YROW
            _FXCOL= _XCOL
            text = "xCol, yRow: " + str(row) + " , " + str(column)
            _util.GlobalLabel_SetText(text,"colrow")
            # _util.MessageboxShowInfo("1","1")
            self.Input_Cell_Value(row, column)
            # _util.MessageboxShowInfo("1","2")
            if row < 0 or column < 0 or _height<=column or _width <= row :
                row = "out of extent"
                column="out of extent"

            else:
                # _util.MessageboxShowInfo("1", "3")
                global Cell_X_Center,Cell_Y_Center
                Cell_X_Center = _extent.xMinimum()+ _xsize/2 + _xsize * (row)
                Cell_Y_Center =  _ymax -  _ysize/2 -  _ysize * (column)


                FAc_ident = _layer.dataProvider().identify(QgsPoint(Cell_X_Center, Cell_Y_Center), QgsRaster.IdentifyFormatValue)
                cw_text = self.channel_width_cal(FAc_ident.results().values()[0])


                #_util.GlobalEdit_SetText(cw_text, "cw")

                global _Cnavas_Click_X, _Cnavas_Click_Y
                _Cnavas_Click_X =Cell_X_Center; _Cnavas_Click_Y =Cell_Y_Center
                if Cell_X_Center<= _xmax or _xmin<=Cell_X_Center or Cell_Y_Center<=_ymax or _ymin<=Cell_Y_Center:
                    self.post_vertex_remove()
                    self.create_vertex(Cell_X_Center,Cell_Y_Center)

        else:
            row = "no raster"
            column = "no raster"
            _util.MessageboxShowInfo("row","{0}, {1}".format(str(row),str(column)))



    def Input_Cell_Value(self,x,y):
        # Cell Info Flow 그룹 박스 데이터 내용
        CellType_Result=_wsinfo.cellFlowType(x,y)
        Stream_Result = _wsinfo.streamValue(x,y)
        FD_Result = _wsinfo.flowDirection(x, y)
        FA_Result = _wsinfo.flowAccumulation(x,y)
        Slop_Result = _wsinfo.slope(x,y)
        _util.GlobalControl_SetValue(CellType_Result,str(Stream_Result), FD_Result, str(FA_Result), str(Slop_Result))

        # _util.MessageboxShowInfo("x : Y", "x " + str(x) + " : " + str(y) )
        # _util.MessageboxShowInfo("texture File" ,str(self.SoilTextureFile) )
        # _util.MessageboxShowInfo("Depth File", str(self.SoilDepthFile))

        # Cell Info Texture 그룹 박스 테이터 내용
        # inOut = _wsinfo.IsInWatershedArea(99,52)
        # _util.MessageboxShowInfo("in Out" ,str(inOut))
        #
        # Texture_Result=_wsinfo.STextureValue(99,52)
        #
        # # _util.MessageboxShowInfo("1", "7")
        # # Texture_Result=_wsinfo.grmPrj.WSCells(99, 52).SoilTextureValue()
        # _util.MessageboxShowInfo("1", "6")
        # # #
        # # # Cell Info Depth 그룹 박스 테이터 내용
        # Depth_Result = _wsinfo.soilDepthValue(x,y)
        # _util.MessageboxShowInfo("1", "7")


        # # Cell Info Landcover 그룹 박스 테이터 내용
        Landcover_Result = _wsinfo.landCoverValue(x,y)
        # _util.MessageboxShowInfo("1", "8")
        # _util.MessageboxShowInfo("land value", str(Landcover_Result))


        projectFile = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
        doc = ET.parse(projectFile)
        root = doc.getroot()
        # 메모리에서 불러오는 것으로 변경 해야함 우선은 진행

        for element in root.findall('{http://tempuri.org/GRMProject.xsd}GreenAmptParameter'):
            GridValue = element.findtext("{http://tempuri.org/GRMProject.xsd}GridValue")
            if str(Texture_Result) == GridValue:
                GRMCode = element.findtext("{http://tempuri.org/GRMProject.xsd}GRMCode")
                Porosity = element.findtext("{http://tempuri.org/GRMProject.xsd}Porosity")
                EffectivePorosity = element.findtext("{http://tempuri.org/GRMProject.xsd}EffectivePorosity")
                WFSoilSuctionHead = element.findtext("{http://tempuri.org/GRMProject.xsd}WFSoilSuctionHead")
                HydraulicConductivity = element.findtext("{http://tempuri.org/GRMProject.xsd}HydraulicConductivity")

                _util.GlobalControl_texture_SetValue(GridValue,GRMCode, Porosity, EffectivePorosity,WFSoilSuctionHead,HydraulicConductivity)
                break
            elif Texture_Result is None or Texture_Result=="":
                break
        #
        #
        # for element in root.findall('{http://tempuri.org/GRMProject.xsd}SoilDepth'):
        #     GridValue=element.findtext("{http://tempuri.org/GRMProject.xsd}GridValue")
        #     if str(Depth_Result)==GridValue:
        #         UserDepthClass=element.findtext("{http://tempuri.org/GRMProject.xsd}GRMCode")
        #         SoilDepth=element.findtext("{http://tempuri.org/GRMProject.xsd}SoilDepth")
        #         _util.GlobalControl_Depth_SetValue(GridValue, UserDepthClass, SoilDepth)
        #         break
        #     elif Depth_Result is None or Depth_Result=="":
        #         break

        _util.MessageboxShowInfo("land","1")
        for element in root.findall('{http://tempuri.org/GRMProject.xsd}LandCover'):
            GridValue = element.findtext("{http://tempuri.org/GRMProject.xsd}GridValue")
            _util.MessageboxShowInfo("land", "2")
            if str(Landcover_Result)== GridValue:
                GRMCode = element.findtext("{http://tempuri.org/GRMProject.xsd}GRMCode")
                RoughnessCoefficient = element.findtext("{http://tempuri.org/GRMProject.xsd}RoughnessCoefficient")
                ImperviousRatio = element.findtext("{http://tempuri.org/GRMProject.xsd}ImperviousRatio")
                _util.GlobalControl_Landcover_SetValue(GridValue,GRMCode,RoughnessCoefficient,ImperviousRatio)
                break


    def Point_To_RowColumn(self,point):
        column = int(((_ymax - point.y()) / _ysize))
        row = int(((point.x() - _xmin) / _xsize))
        return row,column



    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)


    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)


    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

    # canvas event
    def ZoomtoExtent(self):
        self.canvas.zoomToFullExtent()
        self.canvas.refresh()

    def ZoomtoNextExtent(self):
        self.canvas.zoomToNextExtent()
        self.canvas.refresh()

    def ZoomtoPrevious(self):
        self.canvas.zoomToPreviousExtent()
        self.canvas.refresh()

    def canvas_zoomIn(self):
        actionZoomIn = QAction(self)
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False)  # false = in
        self.toolZoomIn.setAction(actionZoomIn)
        self.canvas.setMapTool(self.toolZoomIn)
        self.canvas.refresh()

    def canvas_zoomOut(self):
        actionZoomOut = QAction(self)
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True)  # True = out
        self.toolZoomOut.setAction(actionZoomOut)
        self.canvas.setMapTool(self.toolZoomOut)
        self.canvas.refresh()

    def canvas_pan(self):
        actionPan = QAction(self)
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(actionPan)
        self.canvas.setMapTool(self.toolPan)
#
#     #2017/11/23----------------------
    def channel_width_cal(self,FAcvalue):
         #mw에서는 line edit 값을 바꿀 수 있고 그에 따라 결과 값이 바뀜. 일단 여기는 이렇세 처리함

        #c = float(GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQc'])
        #d = float(GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQd'])
        #e = float(GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQe'])

        c = float(1.698)
        d = float(0.318)
        e = float(0.5)

        # width = c * (mSelectedCV.FAc * (cProject.Current.Watershed.mCellSize * cProject.Current.Watershed.mCellSize / 1000000)) ^ d / slope ^ e
        #FAc 는 cell 값, Slope는 gmp의 MinSlopeChBed 값임
        #slope = float(GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinSlopeChBed'])
        slope = float(0.0005)

        width = c * pow(( FAcvalue * (_xsize * _xsize / 1000000)) , d) / pow(slope, e)

        User_Cw = '%.3f'%width

        return str(User_Cw)
#
#
#
#
#



