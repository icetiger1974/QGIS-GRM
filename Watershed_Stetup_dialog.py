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
_new_wsinfo={}
_FlowControlTable = {}
_FYROW =0
_FXCOL =0
_ClickX=""
_ClickY=""
_AddFlowcontrolFilePath =""
_AddFlowcontrolType=""
_AddFlowcontrolTimeInterval = ""
_AddFlowcontrolName = ""
_AddFlowcontrol_Edit_or_Insert_type=""
_AddFlowcontrol_DT=""
_AddFlowcontrol_IniStorage =""
_AddFlowcontrol_MaxStorage=""
_AddFlowcontrol_MaxStorageR =""
_AddFlowcontrol_ROType=""
_AddFlowcontrol_ROConstQ=""
_AddFlowcontrol_ROConstQDuration=""
_EditFlowCurrentRow = 0

_Flowcontrolgrid_flag = False
_Flowcontrolgrid_flag_Insert = False

_EditFlowColX=""
_EditFlowRowY =""
_EditFlowName=""
_EditFlowDT=""
# _EditFlowTimeInterval=""
_EditFlowControlType=""
_EditFlowFlowDataFile =""
_EditFlowIniStorage =""
_EditFlowMaxStorage=""
_EditFlowMaxStorageR =""
_EditFlowROType=""
_EditFlowROConstQ=""
_EditFlowROConstQDuration=""
_EditFlowCurrentRow = 0
_StreamWSID=0

class Watershed_StetupDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(Watershed_StetupDialog, self).__init__(parent)
        self.setupUi(self)

        # 프로젝트 파일의 내용 및 Default 값을 설정
        try:
            self.Set_ProjectDataInit()

            # 캔버스 상위 버튼 아이콘 설정(Zoom , Pan.....)
            self.Set_Canvas_btn_icon()
            # 캔버스 툴 셋팅
            self.Set_Cavas_tool_btn()

            # 캔버스에 레이어 올리기
            self.Set_Canvas_Layer_default()

            # 시뮬레이션 탭 기능 기본값 셋팅
            self.Set_simulation_tab_default()

            # default 설정이지만 프로그램 흐름상 나중에 처리 해야 하는 목록
            # Watchpoint 체크박스 선택 상태로 처리
            self.chkWatch_Point.setChecked(True)
            self.chkFlowContorGird.setChecked(True)

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


            # 시뮬레이션 버튼 이벤트  임시위치
            self.btnStart_Simulation.clicked.connect(self.Click_StartSimulation)
            #
            # 시뮬레이션 시행 종료 기능 비활성화 처리

            # self.btnStop_simulation.clicked.connect(self.Click_Stop_simulation)
            #_util에서 self.lblColRow 라벨
            _util.GlobalLabel(self.lblColRow,type="colrow")

            # Cell info Flow 텍스트 박스에 값 셋팅에 사용 하기 위해 유틸에 텍스트 박스 넘김
            _util.GlobalControl(self.txtCelltype,self.txtStreamValue,self.txtFD,self.txtFA,self.txtSlope,self.txtWatershedID)
            #_util.GlobalControl(self.txtCelltype,self.txtStreamValue,self.txtFD,self.txtFA,self.txtSlope)

            # Cell info Land cover
            _util.GlobalControl_Landcover(self.txtLandGridValue, self.txtLandType, self.txtRoughness, self.txtratio)

            # Cell info Depth
            _util.GlobalControl_Depth(self.txtDepthValue,self.txtSoilDepthClass, self.txtSoilDepth)


            # Cell info Texture
            _util.GlobalControl_texture(self.txtTextureGridValue, self.txtSoilTexture, self.txtPorosity, self.txtEffectivePorosity, self.txtSuctionhead,self.txtcondcutivity)

            #_util.GlobalEdit(self.txtChannel_width, "cw")
            # Discharge 파일 열기 이벤트
            self.btnViewResult.clicked.connect(self.Open_ViewResult)

            self.btnSaveproject.clicked.connect(self.SaveProject)

            # 임시 처리
            self.RubberBand = []
        except Exception as e:
            _util.MessageboxShowError("Error", str(e))
            pass


    def SaveProject(self):
        self.InputDictionary()
        DictoXml = xmltodict.unparse(GRM._xmltodict)
        fw = open(self.ProjectFile, 'w+')
        fw.write(DictoXml)
        time.sleep(0.1)
        fw.close()

        ds = GRMCore.GRMProject()
        ds.ReadXml(self.ProjectFile)
        time.sleep(0.1)
        ds.WriteXml(self.ProjectFile)
        time.sleep(0.1)
        ds.Dispose()
        _util.MessageboxShowInfo("GRM Save", '"' + self.ProjectFile + '"' + ' was saved. ')

    def Click_StartSimulation(self):
        #값 변경 테스트 용 WatershedFile 파일 경로를 바꿈
        self.InputDictionary()
        GRMCore_exe = os.path.dirname(os.path.realpath(__file__)) + "\DLL\GRM.exe"
        DictoXml = xmltodict.unparse(GRM._xmltodict)
        fw = open(self.ProjectFile, 'w+')
        fw.write(DictoXml)
        time.sleep(0.5)
        fw.close()

        ds = GRMCore.GRMProject()
        ds.ReadXml(self.ProjectFile)
        ds.WriteXml(self.ProjectFile)
        ds.Dispose()
        arg = GRMCore_exe + " " + self.ProjectFile
        result=_util.Execute(arg)

        if result==0:
            _util.MessageboxShowError("GRM","Simulation completed")
        else:
            _util.MessageboxShowError("GRM", " Simulation was stopped.")

    #def Click_Stop_simulation(self):
    #    self.p.kill()

    def Set_ProjectDataInit(self):

        # 툴박스 인덱스를 셋팅
        self.toolBox.setCurrentIndex(0)

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


        self.IsParallel= GRM._xmltodict['GRMProject']['ProjectSettings']['IsParallel']
        self.MaxDegreeOfParallelism= GRM._xmltodict['GRMProject']['ProjectSettings']['MaxDegreeOfParallelism']



        self.SimulationDuration = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulationDuration']
        self.OutputTimeStep = GRM._xmltodict['GRMProject']['ProjectSettings']['OutputTimeStep']
        self.SimulateInfiltration = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateInfiltration']
        self.SimulateSubsurfaceFlow = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateSubsurfaceFlow']
        self.SimulateBaseFlow = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateBaseFlow']
        self.SimulateFlowControl = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateFlowControl']

        self.IsFixedTimeStep = GRM._xmltodict['GRMProject']['ProjectSettings']['IsFixedTimeStep']

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

        self.MakeIMGFile = GRM._xmltodict['GRMProject']['ProjectSettings']['MakeIMGFile']
        self.MakeASCFile = GRM._xmltodict['GRMProject']['ProjectSettings']['MakeASCFile']
        self.MakeSoilSaturationDistFile = GRM._xmltodict['GRMProject']['ProjectSettings']['MakeSoilSaturationDistFile']
        self.MakeRfDistFile = GRM._xmltodict['GRMProject']['ProjectSettings']['MakeRfDistFile']
        self.MakeRFaccDistFile = GRM._xmltodict['GRMProject']['ProjectSettings']['MakeRFaccDistFile']
        self.MakeFlowDistFile = GRM._xmltodict['GRMProject']['ProjectSettings']['MakeFlowDistFile']
        self.PrintOption = GRM._xmltodict['GRMProject']['ProjectSettings']['PrintOption']
        self.WriteLog = GRM._xmltodict['GRMProject']['ProjectSettings']['WriteLog']


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
        global _StreamWSID
        _StreamWSID = _wsinfo.mostDownStreamWSID()

        self.Set_Wathpoint_default_value()
        # ChannelWidth tab 변수

        self.CrossSectionType = GRM._xmltodict['GRMProject']['ProjectSettings']['CrossSectionType']
        self.SingleCSChannelWidthType= GRM._xmltodict['GRMProject']['ProjectSettings']['SingleCSChannelWidthType']

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
        self.btnZoomExtent.setIconSize(QtCore.QSize(200, 200))

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

        # chkFC
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
        # 프린트 옵션 콤보 박스 셋팅
        combolist = ('All','DischargeFileQ','AllQ')
        self.cmbPrint.addItems(combolist)
        index = self.cmbPrint.findText(self.PrintOption, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cmbPrint.setCurrentIndex(index)

        self.cmbPrint.currentIndexChanged.connect(self.printcombo)
        self.spTimeStep_min_2.valueChanged.connect(self.SPvaluechange)


        self.chkParallel.stateChanged.connect(self.Check_Parallel)
        self.Check_Parallel()

        if self.MakeIMGFile.upper() == 'TRUE':
            self.chkmakeimage.setChecked(True)
        else:
            self.chkmakeimage.setChecked(False)

        if self.MakeASCFile.upper() == 'TRUE':
            self.chkmakeASC.setChecked(True)
        else:
            self.chkmakeASC.setChecked(False)

        if self.MakeSoilSaturationDistFile.upper() == 'TRUE':
            self.chksoiSaturation.setChecked(True)
        else:
            self.chksoiSaturation.setChecked(False)

        if self.MakeRfDistFile.upper() == 'TRUE':
            self.chkrfDistFile.setChecked(True)
        else:
            self.chkrfDistFile.setChecked(False)

        if self.MakeRFaccDistFile.upper() == 'TRUE':
            self.chkrfaacDistfile.setChecked(True)
        else:
            self.chkrfaacDistfile.setChecked(False)


        if self.MakeFlowDistFile.upper() == 'TRUE':
            self.chkdischarge.setChecked(True)
        else:
            self.chkdischarge.setChecked(False)

        if self.WriteLog.upper() == 'TRUE':
            self.chklog.setChecked(True)
        else:
            self.chklog.setChecked(False)


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


        if self.IsParallel.upper() == 'TRUE':
            self.chkParallel.setChecked(True)
        else:
            self.chkParallel.setChecked(False)




        if self.ComputationalTimeStep is not None :
            intvalue = int(self.ComputationalTimeStep)
            self.spTimeStep_min.setValue(intvalue)
        else:
            if _xsize<=200:
                value =3
            elif _xsize>200:
                value = 5
            self.spTimeStep_min.setValue(value)


        if self.MaxDegreeOfParallelism is not None :
            intvalue = int(self.MaxDegreeOfParallelism)
            self.spTimeStep_min_2.setValue(intvalue)
     
        if self.OutputTimeStep is not None and self.OutputTimeStep!="":
            self.txtOutput_time_step.setText(str(self.OutputTimeStep))
        else:
            self.txtOutput_time_step.setText(str(self.RainfallInterval))

        Allcount=_wsinfo.grmPrj.CVCount
        if Allcount is not None:
            self.txtCellCount.setText(str(Allcount))


        # 기본 사양은 비활성화
        self.txtCellCount.setDisabled(True)


        # # 프로젝트 파일에서 기본 셋팅 분을 받아 옴
        # if self.ComputationalTimeStep is not None:
        #     Time_step_s = float(self.ComputationalTimeStep) * 60
        #     # 타임스텝 (분)
        #     self.txtTimeStep_min.setText(self.ComputationalTimeStep)
        #     # 타임스텝 (초)
        #     # self.txtTimeStep_sec.setText(str(Time_step_s))
        if self.SimulationDuration is not None:
            self.txtSimulation_duration.setText(self.SimulationDuration)
        else:
            self.txtSimulation_duration.setText("")


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

        self.chkmakeimage.stateChanged.connect(self.MakeASC_IMAGE)
        self.chkmakeASC.stateChanged.connect(self.MakeASC_IMAGE)
        self.MakeASC_IMAGE()

        if self.IsFixedTimeStep.upper() == "TRUE":
            self.chkfixeTimeStep.setChecked(True)

    def SPvaluechange(self):
        value=self.spTimeStep_min_2.text()
        if value =="0":
            _util.MessageboxShowError(" GRM " , " Input 0 can not be input. ")

    def Check_Parallel(self):
        if self.chkParallel.isChecked():
            self.spTimeStep_min_2.setEnabled(True)
        else:
            self.spTimeStep_min_2.setEnabled(False)

    def printcombo(self):
        if self.cmbPrint.currentText()=="All":
            self.chkmakeimage.setEnabled(True)
            self.chkmakeASC.setEnabled(True)
            self.MakeASC_IMAGE()
        else:
            self.chkmakeimage.setEnabled(False)
            self.chkmakeASC.setEnabled(False)
            self.chksoiSaturation.setEnabled(False)
            self.chkrfDistFile.setEnabled(False)
            self.chkrfaacDistfile.setEnabled(False)
            self.chkdischarge.setEnabled(False)


    def MakeASC_IMAGE(self):
        if self.chkmakeimage.isChecked() or self.chkmakeASC.isChecked():
            self.chksoiSaturation.setEnabled(True)
            self.chkrfDistFile.setEnabled(True)
            self.chkrfaacDistfile.setEnabled(True)
            self.chkdischarge.setEnabled(True)
        else:
            self.chksoiSaturation.setEnabled(False)
            self.chkrfDistFile.setEnabled(False)
            self.chkrfaacDistfile.setEnabled(False)
            self.chkdischarge.setEnabled(False)

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
        try:
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
            # self.btnColorPicker_3.clicked.connect(lambda: self.color_picker(self.btnColorPicker, "watchpoint"))
            self.btnColorPicker_3.clicked.connect(lambda: self.color_picker(self.btnColorPicker_3, "flow"))

            #2017/11/22-------------------
            #테이블 셀 값 선택한 값의 위치로 view 이동
            self.btnGrid.clicked.connect(self.GoToGrid)

            # 테이블 셀값을 변경 가능하게 설정 ----> 색상값 변경임 잘못된 구현 변경 해야함
            self.btnEdit.clicked.connect(self.Edit)

            self.btnAddSelectCell.clicked.connect(self.Add_Selected_Cell)

            # 최하류 셀 넣기
            self.btnAddMostDown.clicked.connect(self.Add_MostDown_Stream)

            # 각각의 컬럼에 갑셋팅(xml 상에 'ObTSId', 'ObTSLegend', 'ObTSMissingCount' 항목의 값이 없음
            self.Watchpoint_TableCreate(len(self.Name))
            self.Watchpoint_Table_Insert()
        except Exception as wa:
            _util.MessageboxShowError("Error" , str(wa))


    def Add_MostDown_Stream(self):
        x = _wsinfo.mostDownStreamCellArrayXColPosition()
        y = _wsinfo.mostDownStreamCellArrayYRowPosition()
        rowCount = self.tbList.rowCount()
        if self.CheckTableValue(x,y):
            self.tbList.insertRow(rowCount)
            text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter name:', QLineEdit.Normal, "")
            self.tbList.setItem(rowCount, 0, QTableWidgetItem(text))
            self.tbList.setItem(rowCount, 1, QTableWidgetItem(str(x)))
            self.tbList.setItem(rowCount, 2, QTableWidgetItem(str(y)))
            self.row_cols_grid(x, y, "watchpoint")
            self.SetMostDownStream(_StreamWSID)
        else:
            _util.MessageboxShowInfo("GRM"," The most downstream value already exists. ")


    def CheckTableValue(self,x,y):
        rowCount = self.tbList.rowCount()
        self.RetBool= True
        for row in range(0, rowCount):
            X = self.tbList.item(row, 1).text()
            Y = self.tbList.item(row, 2).text()
            if X==str(x) and Y==str(y) :
                self.RetBool= False
        return self.RetBool

    def Watchpoint_Table_Insert(self):
        if len(self.Name) >0:
            for i in range(0, len(self.Name)):
                # 사용자에게 CVID 표출 안함
                self.tbList.setItem(i, 0, QTableWidgetItem(self.Name[i]))
                self.tbList.setItem(i, 1, QTableWidgetItem(self.ColX[i]))
                self.tbList.setItem(i, 2, QTableWidgetItem(self.RowY[i]))


    # watchpoint datault 값을 변수에 저장
    def Set_Wathpoint_default_value(self):
        self.Name = []
        self.ColX = []
        self.RowY = []
        if GRM._WatchPointCount== 0:
            # Dll 에서 X,Y 값을 넣었을때 받는 값
            x = _wsinfo.mostDownStreamCellArrayXColPosition()
            y = _wsinfo.mostDownStreamCellArrayYRowPosition()
            #proname = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
            #names = _util.GetFilename(proname)
            names = "MD"

            self.Name.append(names)
            self.ColX.append(str(x))
            self.RowY.append(str(y))
            # New Project 일때 프로그램 최하류 정보를 Dll에 넣음
            self.SetMostDownStream(_StreamWSID)
        elif GRM._WatchPointCount>1:
            for flowitem in GRM._xmltodict['GRMProject']['WatchPoints']:
                self.ColX.append(str(flowitem['ColX']))
                self.RowY.append(str(flowitem['RowY']))
                self.Name.append(flowitem['Name'])
        elif  GRM._WatchPointCount==1:
            self.ColX.append(str(GRM._xmltodict['GRMProject']['WatchPoints']['ColX']))
            self.RowY.append(str(GRM._xmltodict['GRMProject']['WatchPoints']['RowY']))
            self.Name.append(str(GRM._xmltodict['GRMProject']['WatchPoints']['Name']))


    def SetMostDownStream(self,id):
        # 만약에 Cell size 값이 없으면 레이어에서 값을 받음
        if self.GridCellSize is not None:
            Allsize =self.GridCellSize
        else:
            self.GridCellSize = str(_xsize)
            if self.GridCellSize is not None:
                GRM._xmltodict['GRMProject']['ProjectSettings']['GridCellSize'] = str(_xsize)
                Allsize=self.GridCellSize

        IniSaturation = "1"
        MinSlopeOF = "0.0001"
        MinSlopeChBed = "0.0001"
        intAll = float(Allsize)
        if intAll > 0:
            MinChBaseWidth = intAll / 10
        IniFlow = "0"
        ChRoughness = "0.045"
        DryStreamOrder = "0"
        CalCoefLCRoughness = "1"
        CalCoefSoilDepth = "1"
        CalCoefPorosity = "1"
        CalCoefWFSuctionHead = "1"
        CalCoefHydraulicK = "1"
        UnsturatedType ="Linear"
        CoefUnsatruatedk = "0.2"

        _wsinfo.SetOneSWSParametersAndUpdateAllSWSUsingNetwork(id, float(IniSaturation), float(MinSlopeOF),UnsturatedType,float(CoefUnsatruatedk),
                                                               float(MinSlopeChBed),float(MinChBaseWidth),
                                                               float(ChRoughness),int(DryStreamOrder), float(CalCoefLCRoughness),
                                                               float(CalCoefSoilDepth), float(CalCoefPorosity), float(CalCoefWFSuctionHead),
                                                               float(CalCoefHydraulicK),0)

        # doc = ET.parse(self.ProjectFile)
        # root = doc.getroot()
        # for element in root.findall("{http://tempuri.org/GRMProject.xsd}WatchPoints"):
        #     self.Name.append(element.findtext("{http://tempuri.org/GRMProject.xsd}Name"))
        #     self.ColX.append(element.findtext("{http://tempuri.org/GRMProject.xsd}ColX"))
        #     self.RowY.append(element.findtext("{http://tempuri.org/GRMProject.xsd}RowY"))
        #
        # if len(self.Name) ==0:
        #     # Dll 에서 X,Y 값을 넣었을때 받는 값
        #     x = _wsinfo.mostDownStreamCellArrayXColPosition()
        #     y = _wsinfo.mostDownStreamCellArrayYRowPosition()
        #     proname = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
        #     names = _util.GetFilename(proname)
        #     self.Name.append(names)
        #     self.ColX.append(str(x))
        #     self.RowY.append(str(y))

    # ======================WatchPoint Tab Table Setting 종료=======================================


    # ----------------- Channel CS 탭 텍스트 박스 셋팅 -----------------------------
    def Set_ChannelCS_tab_default(self):

        CrossSectionType=self.CrossSectionType.upper()
        SingleCSChannelWidthType=self.SingleCSChannelWidthType.upper()

        if CrossSectionType=="CSSINGLE":
            if SingleCSChannelWidthType=="CWGENERATION":
                self.rdo_single.setChecked(True)
                self.rdo_generateCh.setChecked(True)
            elif SingleCSChannelWidthType=="CWEQUATION":
                self.rdo_single.setChecked(True)
                self.rdo_useCh.setChecked(True)
            else:
                self.rdo_single.setChecked(True)
                self.rdo_useCh.setChecked(True)
        elif CrossSectionType == "CSCOMPOUND":
            self.rdo_compound.setChecked(True)
        else:
            self.rdo_single.setChecked(True)
            self.rdo_generateCh.setChecked(True)



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

        # self.groupBox_6.setDisabled(True)
        # self.rdo_useCh.setChecked(True)
        self.txt_douwnstream.setDisabled(True)
        self.ChannelCS_rdo_able()
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
        self.btnfcgotogrid.clicked.connect(self.btnFCGotoGrid)


    # Flow control 테이블 셋팅
    # 프로젝트 파일에서 데이터 값이 있으면 테이블에 값을 셋팅
    def FlowControlTableSetting(self):
        global  _Flowcontrolgrid_xmlCount
        self.tlbFlowControl.setColumnCount(12)
        # self.tlbFlowControl.setHorizontalHeaderLabels(['ColX', 'RowY', 'Name', 'DT', 'ControlType', 'FlowDataFile','IniStorage','MaxStorage','MaxStorageR','ROType','ROConstQ','ROConstQDuration'])
        self.tlbFlowControl.setHorizontalHeaderLabels(['Name','ColX', 'RowY', 'DT', 'ControlType', 'FlowDataFile','IniStorage','MaxStorage','MaxStorageR','ROType','ROConstQ','ROConstQDuration'])
        self.tlbFlowControl.verticalHeader().hide()

        if _Flowcontrolgrid_flag == False:
            _Flowcontrolgrid_xmlCount = _util.FlowControlGrid_XmlCount()
        if _Flowcontrolgrid_xmlCount == 1:

            self.tlbFlowControl.insertRow(0)
            self.tlbFlowControl.setItem(0, 0, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['Name']))
            self.tlbFlowControl.setItem(0, 1, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['ColX']))
            self.tlbFlowControl.setItem(0, 2, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['RowY']))
            self.tlbFlowControl.setItem(0, 3, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['DT']))
            self.tlbFlowControl.setItem(0, 4, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['ControlType']))
            self.tlbFlowControl.setItem(0, 5, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['FlowDataFile']))

            # self.tlbFlowControl.setItem(0, 0, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['ColX']))
            # self.tlbFlowControl.setItem(0, 1, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['RowY']))
            # self.tlbFlowControl.setItem(0, 2, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['Name']))
            # self.tlbFlowControl.setItem(0, 3, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['DT']))
            # self.tlbFlowControl.setItem(0, 4, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['ControlType']))
            # self.tlbFlowControl.setItem(0, 5, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['FlowDataFile']))
            #




            if 'ROType' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                self.tlbFlowControl.setItem(0, 9, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['ROType']))
            else:
                self.tlbFlowControl.setItem(0, 9, QTableWidgetItem(""))
            # _util.MessageboxShowInfo("Table", "4")
            if 'ROConstQ' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                self.tlbFlowControl.setItem(0, 10, QTableWidgetItem(
                    GRM._xmltodict['GRMProject']['FlowControlGrid']['ROConstQ']))
            else:
                self.tlbFlowControl.setItem(0, 10, QTableWidgetItem(""))
            # _util.MessageboxShowInfo("Table", "5")
            if 'ROConstQDuration' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                self.tlbFlowControl.setItem(0, 11, QTableWidgetItem(
                    GRM._xmltodict['GRMProject']['FlowControlGrid']['ROConstQDuration']))
            else:
                self.tlbFlowControl.setItem(0, 11, QTableWidgetItem(""))
            # _util.MessageboxShowInfo("Table", "6")
            if GRM._xmltodict['GRMProject']['FlowControlGrid']['ControlType'] =="ReservoirOperation":
                if 'IniStorage' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                    self.tlbFlowControl.setItem(0, 6, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['IniStorage']))
                else:
                    self.tlbFlowControl.setItem(0, 6, QTableWidgetItem(""))
                # _util.MessageboxShowInfo("Table", "7")
                if 'MaxStorage' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                    self.tlbFlowControl.setItem(0, 7, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['MaxStorage']))
                else:
                    self.tlbFlowControl.setItem(0, 7, QTableWidgetItem(""))
                # _util.MessageboxShowInfo("Table", "8")
                if 'MaxStorageR' in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                    self.tlbFlowControl.setItem(0, 8, QTableWidgetItem(GRM._xmltodict['GRMProject']['FlowControlGrid']['MaxStorageR']))
                else:
                    self.tlbFlowControl.setItem(0, 8, QTableWidgetItem(""))
                # _util.MessageboxShowInfo("Table", "9")
        elif _Flowcontrolgrid_xmlCount > 1:
            # _util.MessageboxShowInfo("Table", "3")
            row =0
            for flowitem in GRM._xmltodict['GRMProject']['FlowControlGrid']:
                self.tlbFlowControl.insertRow(row)
                # self.tlbFlowControl.setItem(row, 0, QTableWidgetItem(str(flowitem['ColX'])))
                # self.tlbFlowControl.setItem(row, 1, QTableWidgetItem(str(flowitem['RowY'])))
                # self.tlbFlowControl.setItem(row, 2, QTableWidgetItem(flowitem['Name']))
                # self.tlbFlowControl.setItem(row, 3, QTableWidgetItem(str(flowitem['DT'])))
                # self.tlbFlowControl.setItem(row, 4, QTableWidgetItem(flowitem['ControlType']))
                # self.tlbFlowControl.setItem(row, 5, QTableWidgetItem(flowitem['FlowDataFile']))

                self.tlbFlowControl.setItem(row, 0, QTableWidgetItem(flowitem['Name']))
                self.tlbFlowControl.setItem(row, 1, QTableWidgetItem(str(flowitem['ColX'])))
                self.tlbFlowControl.setItem(row, 2, QTableWidgetItem(str(flowitem['RowY'])))
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
            # _util.MessageboxShowInfo("flag",str(_Flowcontrolgrid_flag_Insert))
            if _Flowcontrolgrid_flag_Insert :
                self.ADDFlowData()
                _Flowcontrolgrid_flag_Insert = False

            global _AddFlowcontrolFilePath ,_AddFlowcontrolName ,_AddFlowcontrolType ,_AddFlowcontrolTimeInterval
            global _AddFlowcontrol_DT,_AddFlowcontrol_IniStorage ,_AddFlowcontrol_MaxStorage
            global _AddFlowcontrol_MaxStorageR,_AddFlowcontrol_ROType,_AddFlowcontrol_ROConstQ,_AddFlowcontrol_ROConstQDuration


            _AddFlowcontrolFilePath = ""
            _AddFlowcontrolType = ""
            _AddFlowcontrolTimeInterval = ""
            _AddFlowcontrolName = ""
            _AddFlowcontrol_Edit_or_Insert_type = ""
            _AddFlowcontrol_DT=""
            _AddFlowcontrol_IniStorage =""
            _AddFlowcontrol_MaxStorage=""
            _AddFlowcontrol_MaxStorageR =""
            _AddFlowcontrol_ROType=""
            _AddFlowcontrol_ROConstQ=""
            _AddFlowcontrol_ROConstQDuration=""

    def ADDFlowData(self):
        if _AddFlowcontrolFilePath=="" :
            pass
        if _AddFlowcontrolType=="":
            pass
        counts=self.tlbFlowControl.rowCount()
        if _FXCOL !=0 and _FYROW!=0:
            global _FXCOL , _FYROW
            self.tlbFlowControl.insertRow(counts)
            # self.tlbFlowControl.setItem(counts, 0, QTableWidgetItem(str(_YROW)))
            # self.tlbFlowControl.setItem(counts,1, QTableWidgetItem(str(_XCOL)))
            # self.tlbFlowControl.setItem(counts,3, QTableWidgetItem(_AddFlowcontrolTimeInterval))


            self.tlbFlowControl.setItem(counts,0, QTableWidgetItem(_AddFlowcontrolName))
            self.tlbFlowControl.setItem(counts,1, QTableWidgetItem(str(_YROW)))
            self.tlbFlowControl.setItem(counts,2, QTableWidgetItem(str(_XCOL)))

            _FXCOL=0
            _FYROW=0
            self.tlbFlowControl.setItem(counts,3, QTableWidgetItem(_AddFlowcontrolTimeInterval))
            self.tlbFlowControl.setItem(counts,4, QTableWidgetItem(_AddFlowcontrolType))
            self.tlbFlowControl.setItem(counts,5, QTableWidgetItem(_AddFlowcontrolFilePath))
            self.tlbFlowControl.setItem(counts,6, QTableWidgetItem(_AddFlowcontrol_IniStorage))
            self.tlbFlowControl.setItem(counts,7, QTableWidgetItem(_AddFlowcontrol_MaxStorage))
            self.tlbFlowControl.setItem(counts,8, QTableWidgetItem(_AddFlowcontrol_MaxStorageR))
            self.tlbFlowControl.setItem(counts,9, QTableWidgetItem(_AddFlowcontrol_ROType))
            self.tlbFlowControl.setItem(counts,10, QTableWidgetItem(_AddFlowcontrol_ROConstQ))
            self.tlbFlowControl.setItem(counts,11, QTableWidgetItem(_AddFlowcontrol_ROConstQDuration))
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
        GRM._FlowControlCount = count
        for row in range(0, _Flowcontrolgrid_xmlCount):
            child = ET.Element("FlowControlGrid")
            root.append(child)
            #
            # GridValue = ET.Element("ColX")
            # GridValue.text = self.tlbFlowControl.item(row, 0).text()
            # child.append(GridValue)
            #
            # UserLandCover = ET.Element("RowY")
            # UserLandCover.text = self.tlbFlowControl.item(row, 1).text()
            # child.append(UserLandCover)
            #
            # GRMLandCoverCode = ET.Element("Name")
            # GRMLandCoverCode.text = self.tlbFlowControl.item(row, 2).text()
            # child.append(GRMLandCoverCode)

            GRMLandCoverCode = ET.Element("Name")
            GRMLandCoverCode.text = self.tlbFlowControl.item(row, 0).text()
            child.append(GRMLandCoverCode)

            GridValue = ET.Element("ColX")
            GridValue.text = self.tlbFlowControl.item(row, 1).text()
            child.append(GridValue)

            UserLandCover = ET.Element("RowY")
            UserLandCover.text = self.tlbFlowControl.item(row, 2).text()
            child.append(UserLandCover)

            DT = ET.Element("DT")
            DT.text = self.tlbFlowControl.item(row, 3).text()
            child.append(DT)

            ControlType = ET.Element("ControlType")
            testvalue = self.tlbFlowControl.item(row, 4).text()
            if testvalue == "Reservoir outflow":
                ControlType.text = "ReservoirOutflow"
            elif testvalue == "Reservoir operation":
                ControlType.text = "ReservoirOperation"
            elif testvalue == "Sink flow":
                ControlType.text = "SinkFlow"
            elif testvalue == "Source flow":
                ControlType.text = "SourceFlow"
            elif testvalue == "Inlet":
                ControlType.text = "Inlet"
            child.append(ControlType)

            FlowDataFile = ET.Element("FlowDataFile")
            FlowDataFile.text = self.tlbFlowControl.item(row, 5).text()
            child.append(FlowDataFile)


            try:
                IniStorage = ET.Element("IniStorage")
                storage = self.tlbFlowControl.item(row, 6).text()
                if storage != "":
                    IniStorage.text = self.tlbFlowControl.item(row, 6).text()
                else:
                    IniStorage.text = ""
                child.append(IniStorage)
            except :
                IniStorage = ET.Element("IniStorage")
                IniStorage.text = ""
                child.append(IniStorage)

            try:
                MaxStorage = ET.Element("MaxStorage")
                if self.tlbFlowControl.item(row, 7).text() != "":
                    MaxStorage.text = self.tlbFlowControl.item(row, 7).text()
                else:
                    MaxStorage.text = ""
                child.append(MaxStorage)
            except:
                 MaxStorage = ET.Element("MaxStorage")
                 MaxStorage.text = ""
                 child.append(MaxStorage)

            try:
                MaxStorageR = ET.Element("MaxStorageR")
                if self.tlbFlowControl.item(row, 8).text() != "":
                    MaxStorageR.text = self.tlbFlowControl.item(row, 8).text()
                else:
                    MaxStorageR.text = ""
                child.append(MaxStorageR)
            except:
                 MaxStorageR = ET.Element("MaxStorageR")
                 MaxStorageR.text = ""
                 child.append(MaxStorageR)

            try:
                ROType = ET.Element("ROType")
                if self.tlbFlowControl.item(row, 9).text() != "":
                    ROType.text = self.tlbFlowControl.item(row, 9).text()
                else:
                    ROType.text = ""
                child.append(ROType)
            except:
                 ROType = ET.Element("ROType")
                 ROType.text = ""
                 child.append(ROType)


            try:
                ROConstQ = ET.Element("ROConstQ")
                if self.tlbFlowControl.item(row, 10).text() != "":
                    ROConstQ.text = self.tlbFlowControl.item(row, 10).text()
                else:
                    ROConstQ.text = ""
                child.append(ROConstQ)
            except:
                ROConstQ = ET.Element("ROConstQ")
                ROConstQ.text = ""
                child.append(ROConstQ)

            try:
                ROConstQDuration = ET.Element("ROConstQDuration")
                if self.tlbFlowControl.item(row, 11).text() != "":
                    ROConstQDuration.text = self.tlbFlowControl.item(row, 11).text()
                else:
                    ROConstQDuration.text = ""
                child.append(ROConstQDuration)
            except:
                ROConstQDuration = ET.Element("ROConstQDuration")
                ROConstQDuration.text = ""
                child.append(ROConstQDuration)
        xmltree_string = ET.tostring(xmltree.getroot())
        docs = dict(xmltodict.parse(xmltree_string))
        GRM._xmltodict.clear()
        GRM._xmltodict.update(docs)


        # 테이블에 값 셋팅후 화면에 점 표시
        if self.chkFlowContorGird.isChecked():
            self.FlowContorGird_paint()

    def FlowControlEdit(self):
        global _AddFlowcontrol_Edit_or_Insert_type,_Flowcontrolgrid_xmlCount
        global _EditFlowColX,_EditFlowRowY,_EditFlowName,_EditFlowDT,_EditFlowControlType,_EditFlowFlowDataFile,_EditFlowIniStorage
        global _EditFlowMaxStorage,_EditFlowMaxStorageR,_EditFlowROType,_EditFlowROConstQ,_EditFlowROConstQDuration,_EditFlowCurrentRow
        global _FlowControlTable
        _FlowControlTable = self.tlbFlowControl
        row = self.tlbFlowControl.currentRow()
        _EditFlowCurrentRow = row
        if row>-1:
            # _EditFlowColX = self.tlbFlowControl.item(row, 0).text()
            # _EditFlowRowY = self.tlbFlowControl.item(row, 1).text()
            # _EditFlowName = self.tlbFlowControl.item(row, 2).text()

            _EditFlowName = self.tlbFlowControl.item(row, 0).text()
            _EditFlowColX = self.tlbFlowControl.item(row, 1).text()
            _EditFlowRowY = self.tlbFlowControl.item(row, 2).text()
            _EditFlowDT = self.tlbFlowControl.item(row, 3).text()
            _EditFlowControlType = self.tlbFlowControl.item(row, 4).text()
            _EditFlowFlowDataFile = self.tlbFlowControl.item(row, 5).text()
            try:
                test11 = str(self.tlbFlowControl.item(row, 6).text().strip())
                if test11 =="":
                    _EditFlowIniStorage = ""
                else:
                    _EditFlowIniStorage = self.tlbFlowControl.item(row, 6).text()

                if self.tlbFlowControl.item(row, 7).text() != "":
                    _EditFlowMaxStorage = self.tlbFlowControl.item(row, 7).text()
                else:
                    _EditFlowMaxStorage = ""

                if self.tlbFlowControl.item(row, 8).text() != "":
                    _EditFlowMaxStorageR = self.tlbFlowControl.item(row, 8).text()
                else:
                    _EditFlowMaxStorageR = ""

                if self.tlbFlowControl.item(row, 9).text() != "":
                    _EditFlowROType = self.tlbFlowControl.item(row, 9).text()
                else:
                    _EditFlowROType = ""

                if self.tlbFlowControl.item(row, 10).text() != "":
                    _EditFlowROConstQ = self.tlbFlowControl.item(row, 10).text()
                else:
                    _EditFlowROConstQ = ""

                if self.tlbFlowControl.item(row, 11).text() != "":
                    _EditFlowROConstQDuration = self.tlbFlowControl.item(row, 11).text()
                else:
                    _EditFlowROConstQDuration = ""
            except Exception as e:
                pass

            _AddFlowcontrol_Edit_or_Insert_type = "Edit"
            _Flowcontrolgrid_xmlCount=_util.FlowControlGrid_XmlCount()
            results = AddFlowControl()
            results.exec_()




    def tlbFlowControl_clik_enent(self):
        global _ClickX,_ClickY
        row=self.tlbFlowControl.currentRow()
        # _ClickX = self.tlbFlowControl.item(row,0).text()
        # _ClickY = self.tlbFlowControl.item(row, 1).text()

        _ClickX = self.tlbFlowControl.item(row, 1).text()
        _ClickY = self.tlbFlowControl.item(row, 2).text()

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
                GRM._FlowControlCount = count
    
                for row in range(0, count):
                    child = ET.Element("FlowControlGrid")
                    root.append(child)

                    # GridValue = ET.Element("ColX")
                    # GridValue.text = self.tlbFlowControl.item(row, 0).text()
                    # child.append(GridValue)
                    #
                    # UserLandCover = ET.Element("RowY")
                    # UserLandCover.text = self.tlbFlowControl.item(row, 1).text()
                    # child.append(UserLandCover)
                    #
                    # GRMLandCoverCode = ET.Element("Name")
                    # GRMLandCoverCode.text = self.tlbFlowControl.item(row, 2).text()
                    # child.append(GRMLandCoverCode)





                    GRMLandCoverCode = ET.Element("Name")
                    GRMLandCoverCode.text = self.tlbFlowControl.item(row, 0).text()
                    child.append(GRMLandCoverCode)

                    GridValue = ET.Element("ColX")
                    GridValue.text = self.tlbFlowControl.item(row, 1).text()
                    child.append(GridValue)
    
                    UserLandCover = ET.Element("RowY")
                    UserLandCover.text = self.tlbFlowControl.item(row, 2).text()
                    child.append(UserLandCover)

                    DT = ET.Element("DT")
                    DT.text = self.tlbFlowControl.item(row, 3).text()
                    child.append(DT)

                    ControlType = ET.Element("ControlType")
                    testvalue = self.tlbFlowControl.item(row, 4).text()
                    if testvalue == "Reservoir outflow":
                        ControlType.text = "ReservoirOutflow"
                    elif testvalue == "Reservoir operation":
                        ControlType.text = "ReservoirOperation"
                    elif testvalue == "Sink flow":
                        ControlType.text = "SinkFlow"
                    elif testvalue == "Source flow":
                        ControlType.text = "SourceFlow"
                    elif testvalue == "Inlet":
                        ControlType.text = "Inlet"
                    child.append(ControlType)


    
                    FlowDataFile = ET.Element("FlowDataFile")
                    FlowDataFile.text = self.tlbFlowControl.item(row, 5).text()
                    child.append(FlowDataFile)

                    try:
                        IniStorage = ET.Element("IniStorage")
                        storage = self.tlbFlowControl.item(row, 6).text()
                        if storage != "":
                            IniStorage.text = self.tlbFlowControl.item(row, 6).text()
                        else:
                            IniStorage.text = ""
                        child.append(IniStorage)
                    except:
                        IniStorage = ET.Element("IniStorage")
                        IniStorage.text = ""
                        child.append(IniStorage)

                    try:
                        MaxStorage = ET.Element("MaxStorage")
                        if self.tlbFlowControl.item(row, 7).text() != "":
                            MaxStorage.text = self.tlbFlowControl.item(row, 7).text()
                        else:
                            MaxStorage.text = ""
                        child.append(MaxStorage)
                    except:
                        MaxStorage = ET.Element("MaxStorage")
                        MaxStorage.text = ""
                        child.append(MaxStorage)

                    try:
                        MaxStorageR = ET.Element("MaxStorageR")
                        if self.tlbFlowControl.item(row, 8).text() != "":
                            MaxStorageR.text = self.tlbFlowControl.item(row, 8).text()
                        else:
                            MaxStorageR.text = ""
                        child.append(MaxStorageR)
                    except:
                        MaxStorageR = ET.Element("MaxStorageR")
                        MaxStorageR.text = ""
                        child.append(MaxStorageR)

                    try:
                        ROType = ET.Element("ROType")
                        if self.tlbFlowControl.item(row, 9).text() != "":
                            ROType.text = self.tlbFlowControl.item(row, 9).text()
                        else:
                            ROType.text = ""
                        child.append(ROType)
                    except:
                        ROType = ET.Element("ROType")
                        ROType.text = ""
                        child.append(ROType)

                    try:
                        ROConstQ = ET.Element("ROConstQ")
                        if self.tlbFlowControl.item(row, 10).text() != "":
                            ROConstQ.text = self.tlbFlowControl.item(row, 10).text()
                        else:
                            ROConstQ.text = ""
                        child.append(ROConstQ)
                    except:
                        ROConstQ = ET.Element("ROConstQ")
                        ROConstQ.text = ""
                        child.append(ROConstQ)

                    try:
                        ROConstQDuration = ET.Element("ROConstQDuration")
                        if self.tlbFlowControl.item(row, 11).text() != "":
                            ROConstQDuration.text = self.tlbFlowControl.item(row, 11).text()
                        else:
                            ROConstQDuration.text = ""
                        child.append(ROConstQDuration)
                    except:
                        ROConstQDuration = ET.Element("ROConstQDuration")
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

        # 함수로 빼야함 급해서 그냥 넣음
        combolist = ('Linear','Exponential','Constant')
        self.cmbUnsturatedType.addItems(combolist)
        self.cmbUnsturatedType.currentIndexChanged.connect(self.chage_UnsturatedType)

        # 최하류 셀값 설정정
        self.Set_MostDownStream()
        self.cb_selectws.currentIndexChanged.connect(self.SelectWsCombobox)
        self.btnApplyWS.clicked.connect(self.UserSet_Add)
        self.btnRemoveWS.clicked.connect(self.UserSet_remove)
        self.SetWatershedstream()
        self.SetMostDownStream_combobox()
        self.SelectWsCombobox()


    def SetMostDownStream_combobox(self):
        count = self.cb_selectws.count()
        for i in range(0, count):
            selectWS=self.cb_selectws.itemText(i)

            if str(selectWS) ==str(_StreamWSID):
                self.cb_selectws.setCurrentIndex(i)
                return

    def chage_UnsturatedType(self):
        self.selectText=self.cmbUnsturatedType.currentText()
        if self.selectText=="Linear":
            self.txtCoefUnsatruatedk.setText("0.2")
            self.txtCoefUnsatruatedk.setEnabled(True)
        elif self.selectText=="Exponential":
           self.txtCoefUnsatruatedk.setText("6.4")
           self.txtCoefUnsatruatedk.setEnabled(True)
        else :
            self.txtCoefUnsatruatedk.setText("0.1")
            self.txtCoefUnsatruatedk.setEnabled(True)

    def UserSet_remove(self):
        id = self.cb_selectws.currentText()
        comboindex = self.cb_selectws.currentIndex()
        result=_wsinfo.RemoveUserParametersSetting(int(id))

        if result:
            count = self.lisw_UserSet.count()
            for index in range(0,count):
                item = self.lisw_UserSet.item(index).text()
                if item==id:
                    if id!=str(_StreamWSID):
                        self.lisw_UserSet.takeItem(index)
                        _util.MessageboxShowInfo("GRM" , "Remove parameter was completed")
                        self.cb_selectws.setCurrentIndex(0)
                        self.cb_selectws.setCurrentIndex(comboindex)

    def UserSet_Add(self):
        id = int(self.cb_selectws.currentText())
        items = self.lisw_UserSet.findItems(str(id), Qt.MatchExactly)
        if len(items) ==0:
            item1 = QListWidgetItem(str(id))
            self.lisw_UserSet.addItem(item1)

        IniSaturation = self.txtIniSaturation.text()
        MinSlopeOF = self.txtMinSlopeOF.text()
        MinSlopeChBed = self.txtMinSlopeChBed.text()
        IniFlow = self.txtIniFlow.text()

        UnsturatedType = self.cmbUnsturatedType.currentText()
        CoefUnsatruatedk = self.txtCoefUnsatruatedk.text()
        ChRoughness = self.txtChRoughness.text()
        DryStreamOrder = self.txtDryStreamOrder.text()
        CalCoefLCRoughness = self.txtCalCoefLCRoughness.text()
        CalCoefSoilDepth = self.txtCalCoefSoilDepth.text()
        CalCoefPorosity = self.txtCalCoefPorosity.text()
        CalCoefWFSuctionHead = self.txtCalCoefWFSuctionHead.text()
        CalCoefHydraulicK = self.txtCalCoefHydraulicK.text()
        if float(self.GridCellSize) > 0:
            MinChBaseWidth = float(self.GridCellSize) / 10
        result=_wsinfo.SetOneSWSParametersAndUpdateAllSWSUsingNetwork(id, float(IniSaturation), float(MinSlopeOF),UnsturatedType,float(CoefUnsatruatedk),
                                                               float(MinSlopeChBed), float(MinChBaseWidth),
                                                               float(ChRoughness), int(DryStreamOrder),
                                                               float(CalCoefLCRoughness),
                                                               float(CalCoefSoilDepth), float(CalCoefPorosity),
                                                               float(CalCoefWFSuctionHead),
                                                               float(CalCoefHydraulicK),float(IniFlow))
        if result:
            _util.MessageboxShowInfo("GRM" , "Apply parameter was completed")
        else:
            _util.MessageboxShowError("GRM" , "Apply parameter was not completed!")

    def Set_MostDownStream(self):


        # if GRM._SubWatershedCount==0:
        item1 = QListWidgetItem(str(_StreamWSID))
        self.lisw_UserSet.addItem(item1)
        #     self.txtIniSaturation.setText("1")
        #     self.txtMinSlopeOF.setText("0.001")
        #     self.txtMinSlopeChBed.setText("0.001")
        #
        #     intAll = float(self.GridCellSize)
        #     if intAll > 0:
        #         cal_MinChBaseWidth = intAll / 10
        #     self.txtMinChBaseWidth.setText(str(cal_MinChBaseWidth))
        #     self.txtIniFlow.setText("0")
        #     self.txtChRoughness.setText("0.045")
        #     self.txtDryStreamOrder.setText("0")
        #     self.txtCalCoefLCRoughness.setText("1")
        #     self.txtCalCoefSoilDepth.setText("1")
        #     self.txtCalCoefPorosity.setText("1")
        #     self.txtCalCoefWFSuctionHead.setText("1")
        #     self.txtCalCoefHydraulicK.setText("1")
        #
        # elif GRM._SubWatershedCount==1:
        #     item1 = QListWidgetItem(str(_StreamWSID))
        #     self.lisw_UserSet.addItem(item1)
        #
        #     self.txtIniSaturation.setText("1")
        #     self.txtMinSlopeOF.setText("0.001")
        #     self.txtMinSlopeChBed.setText("0.001")
        #
        #     # 만약에 Cell size 값이 없으면 레이어에서 값을 받음
        #     intAll = float(self.GridCellSize)
        #     if intAll > 0:
        #         cal_MinChBaseWidth = intAll / 10
        #     self.txtMinChBaseWidth.setText(str(cal_MinChBaseWidth))
        #     self.txtIniFlow.setText("0")
        #     self.txtChRoughness.setText("0.045")
        #     self.txtDryStreamOrder.setText("0")
        #     self.txtCalCoefLCRoughness.setText("1")
        #     self.txtCalCoefSoilDepth.setText("1")
        #     self.txtCalCoefPorosity.setText("1")
        #     self.txtCalCoefWFSuctionHead.setText("1")
        #     self.txtCalCoefHydraulicK.setText("1")
        # elif GRM._SubWatershedCount> 1:
        #     item1 = QListWidgetItem(str(_StreamWSID))
        #     self.lisw_UserSet.addItem(item1)
        #





        # 콤보 박스에 유역 설정 하기
    def Set_Watershed_combo(self):
        WS_list = []
        wscount=_wsinfo.WScount()
        AllItem=_wsinfo.WSIDsAll()
        for i in range(wscount):
            WS_list.append(str(AllItem[i]))
        self.cb_selectws.clear()
        self.cb_selectws.addItems(WS_list)





    def SetWatershedstream(self):
        self.ID = []; self.IniSaturation=[];self.MinSlopeOF=[];self.MinSlopeChBed=[]
        self.MinChBaseWidth=[]; self.ChRoughness=[]; self.DryStreamOrder=[]; self.IniFlow=[]
        self.CalCoefLCRoughness=[]; self.CalCoefPorosity=[]; self.CalCoefWFSuctionHead=[]; self.CalCoefHydraulicK=[]
        self.CalCoefSoilDepth=[];self.UserSet =[]
        self.UnsaturatedKType=[];self.CoefUnsaturatedK=[]
        doc = ET.parse(self.ProjectFile)
        root = doc.getroot()
        # 최하류 유역 Id 값
        try:
            if GRM._SubWatershedCount == 1:
                i=0
                self.ID.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['ID'])
                self.IniSaturation.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['IniSaturation'])
                self.MinSlopeOF.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinSlopeOF'])
                self.MinSlopeChBed.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinSlopeChBed'])
                self.MinChBaseWidth.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinChBaseWidth'])
                self.ChRoughness.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['ChRoughness'])
                self.DryStreamOrder.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['DryStreamOrder'])
                self.IniFlow.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['IniFlow'])
                self.UnsaturatedKType.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['UnsaturatedKType'])
                self.CoefUnsaturatedK.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CoefUnsaturatedK'])
                self.CalCoefLCRoughness.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefLCRoughness'])
                self.CalCoefPorosity.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefPorosity'])
                self.CalCoefWFSuctionHead.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefWFSuctionHead'])
                self.CalCoefHydraulicK.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefHydraulicK'])
                self.CalCoefSoilDepth.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefSoilDepth'])
                usersetString = GRM._xmltodict['GRMProject']['SubWatershedSettings']['UserSet']
                self.UserSet.append(usersetString)
                results=_wsinfo.SetOneSWSParametersAndUpdateAllSWSUsingNetwork(int(self.ID[i]), float(self.IniSaturation[i]),float(self.MinSlopeOF[i]),self.UnsaturatedKType[i],float(self.CoefUnsaturatedK[i]), float(self.MinSlopeChBed[i]), float(self.MinChBaseWidth[i]),
                                                                       float(self.ChRoughness[i]), int(self.DryStreamOrder[i]), float(self.CalCoefLCRoughness[i]), float(self.CalCoefSoilDepth[i])
                                                                       ,float(self.CalCoefPorosity[i]), float(self.CalCoefWFSuctionHead[i]), float(self.CalCoefHydraulicK[i])
                                                                       ,float(self.IniFlow[i]))

            elif GRM._SubWatershedCount>1:
                i = 0
                for watershed in GRM._xmltodict['GRMProject']['SubWatershedSettings']:
                    idvalue = str(watershed['ID'])
                    self.ID.append(str(watershed['ID']))
                    self.IniSaturation.append(watershed['IniSaturation'])
                    self.MinSlopeOF.append(watershed['MinSlopeOF'])
                    self.MinSlopeChBed.append(watershed['MinSlopeChBed'])
                    self.MinChBaseWidth.append(watershed['MinChBaseWidth'])
                    self.ChRoughness.append(watershed['ChRoughness'])
                    self.DryStreamOrder.append(watershed['DryStreamOrder'])
                    self.IniFlow.append(watershed['IniFlow'])
                    self.UnsaturatedKType.append(watershed['UnsaturatedKType'])
                    self.CoefUnsaturatedK.append(watershed['CoefUnsaturatedK'])
                    self.CalCoefLCRoughness.append(watershed['CalCoefLCRoughness'])
                    self.CalCoefPorosity.append(watershed['CalCoefPorosity'])
                    self.CalCoefWFSuctionHead.append(watershed['CalCoefWFSuctionHead'])
                    self.CalCoefHydraulicK.append(watershed['CalCoefHydraulicK'])
                    self.CalCoefSoilDepth.append(watershed['CalCoefSoilDepth'])
                    usersetString = watershed['UserSet']
                    self.UserSet.append(usersetString)
                    if usersetString.upper() == "TRUE" or self.ID[i] == str(_StreamWSID):
                        _wsinfo.SetOneSWSParametersAndUpdateAllSWSUsingNetwork(int(self.ID[i]),
                                                                               float(self.IniSaturation[i]),
                                                                               float(self.MinSlopeOF[i]),
                                                                               self.UnsaturatedKType[i],
                                                                               float(self.CoefUnsaturatedK[i]),
                                                                               float(self.MinSlopeChBed[i]),
                                                                               float(self.MinChBaseWidth[i]),
                                                                               float(self.ChRoughness[i]),
                                                                               int(self.DryStreamOrder[i]),
                                                                               float(self.CalCoefLCRoughness[i]),
                                                                               float(self.CalCoefSoilDepth[i]),
                                                                               float(self.CalCoefPorosity[i]),
                                                                               float(self.CalCoefWFSuctionHead[i]),
                                                                               float(self.CalCoefHydraulicK[i]),
                                                                               float(self.IniFlow[i]))
                        if str(self.ID[i])!= str(_StreamWSID):
                            item1 = QListWidgetItem(self.ID[i])
                            self.lisw_UserSet.addItem(item1)

                    i = i+1
            elif GRM._SubWatershedCount==0:
                intAll = float(self.GridCellSize)
                if intAll > 0:
                    cal_MinChBaseWidth = intAll / 10
                else:
                    cal_MinChBaseWidth=0
                _wsinfo.SetOneSWSParametersAndUpdateAllSWSUsingNetwork(int(_StreamWSID),1,0.0001,"Linear",0.2,0.0001,float(cal_MinChBaseWidth),0.045,0,1,1,1,1,1,0)
        except Exception as esd:
            _util.MessageboxShowError("error",str(esd))
            pass


    # 콤보박스 선택시 하류 유역과 상류 유역의 콤보박스에 값 셋팅
    def SelectWsCombobox(self):
        self.project_use_flag = False
        # 2018-01-29 박: Watershed parmeter 함수 호출
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
        else:
            self.lisw_DownWS.clear()

        # 상류 유역 정보 셋팅
        UPSW = []
        Dllresult_UP = _wsinfo.upStreamWSIDs(int(selectWS))
        UPSW.extend(Dllresult_UP)
        if len(UPSW)>0:
            self.lisw_UpWS.clear()
            for s in range(len(UPSW)):
                item1 = QListWidgetItem(str(UPSW[s]))
                self.lisw_UpWS.addItem(item1)
        else:
            self.lisw_UpWS.clear()

        # --------------------------------------------------------------------------------------------------------------
        #self.ID = []; self.IniSaturation=[];self.MinSlopeOF=[];self.MinSlopeChBed=[]
        #self.MinChBaseWidth=[]; self.ChRoughness=[]; self.DryStreamOrder=[]; self.IniFlow=[]
        #self.CalCoefLCRoughness=[]; self.CalCoefPorosity=[]; self.CalCoefWFSuctionHead=[]; self.CalCoefHydraulicK=[]
        #self.CalCoefSoilDepth=[];self.UserSet =[]
        #self.UnsaturatedKType=[];self.CoefUnsaturatedK=[]
        #doc = ET.parse(self.ProjectFile)
        #root = doc.getroot()
        ## 최하류 유역 Id 값

        #try:
        #    if GRM._SubWatershedCount == 1:
        #        i = 0
        #        self.ID.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['ID'])
        #        self.IniSaturation.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['IniSaturation'])
        #        self.MinSlopeOF.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinSlopeOF'])
        #        self.MinSlopeChBed.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinSlopeChBed'])
        #        self.MinChBaseWidth.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinChBaseWidth'])
        #        self.ChRoughness.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['ChRoughness'])
        #        self.DryStreamOrder.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['DryStreamOrder'])
        #        self.IniFlow.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['IniFlow'])


        #        self.UnsaturatedKType.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['UnsaturatedKType'])
        #        self.CoefUnsaturatedK.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CoefUnsaturatedK'])

        #        self.CalCoefLCRoughness.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefLCRoughness'])
        #        self.CalCoefPorosity.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefPorosity'])
        #        self.CalCoefWFSuctionHead.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefWFSuctionHead'])
        #        self.CalCoefHydraulicK.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefHydraulicK'])
        #        self.CalCoefSoilDepth.append(GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefSoilDepth'])
        #        usersetString = GRM._xmltodict['GRMProject']['SubWatershedSettings']['UserSet']
        #        self.UserSet.append(usersetString)
        #        results=_wsinfo.SetOneSWSParametersAndUpdateAllSWSUsingNetwork(int(self.ID[i]), float(self.IniSaturation[i]),float(self.MinSlopeOF[i]),self.UnsaturatedKType[i],float(self.CoefUnsaturatedK[i]), float(self.MinSlopeChBed[i]), float(self.MinChBaseWidth[i]),
        #                                                               float(self.ChRoughness[i]), int(self.DryStreamOrder[i]), float(self.CalCoefLCRoughness[i]), float(self.CalCoefSoilDepth[i])
        #                                                               , float(self.CalCoefPorosity[i]), float(self.CalCoefWFSuctionHead[i]), float(self.CalCoefHydraulicK[i])
        #                                                               , 0)

        #    if GRM._SubWatershedCount>1:
        #        i = 0
        #        for watershed in GRM._xmltodict['GRMProject']['SubWatershedSettings']:
        #            self.ID.append(watershed['ID'])
        #            self.IniSaturation.append(watershed['IniSaturation'])
        #            self.MinSlopeOF.append(watershed['MinSlopeOF'])
        #            self.MinSlopeChBed.append(watershed['MinSlopeChBed'])
        #            self.MinChBaseWidth.append(watershed['MinChBaseWidth'])
        #            self.ChRoughness.append(watershed['ChRoughness'])
        #            self.DryStreamOrder.append(watershed['DryStreamOrder'])
        #            self.IniFlow.append(watershed['IniFlow'])

        #            self.UnsaturatedKType.append(watershed['UnsaturatedKType'])
        #            self.CoefUnsaturatedK.append(watershed['CoefUnsaturatedK'])

        #            self.CalCoefLCRoughness.append(watershed['CalCoefLCRoughness'])
        #            self.CalCoefPorosity.append(watershed['CalCoefPorosity'])
        #            self.CalCoefWFSuctionHead.append(watershed['CalCoefWFSuctionHead'])
        #            self.CalCoefHydraulicK.append(watershed['CalCoefHydraulicK'])
        #            self.CalCoefSoilDepth.append(watershed['CalCoefSoilDepth'])



        #            usersetString = watershed['UserSet']
        #            self.UserSet.append(usersetString)
        #            if usersetString.upper() == "TRUE":
        #                _wsinfo.SetOneSWSParametersAndUpdateAllSWSUsingNetwork(int(self.ID[i]),
        #                                                                       float(self.IniSaturation[i]),
        #                                                                       float(self.MinSlopeOF[i]),
        #                                                                       self.UnsaturatedKType[i],
        #                                                                       float(self.CoefUnsaturatedK[i]),
        #                                                                       float(self.MinSlopeChBed[i]),
        #                                                                       float(self.MinChBaseWidth[i]),
        #                                                                       float(self.ChRoughness[i]),
        #                                                                       int(self.DryStreamOrder[i]),
        #                                                                       float(self.CalCoefLCRoughness[i]),
        #                                                                       float(self.CalCoefSoilDepth[i]),
        #                                                                       float(self.CalCoefPorosity[i]),
        #                                                                       float(self.CalCoefWFSuctionHead[i]),
        #                                                                       float(self.CalCoefHydraulicK[i]),
        #                                                                       0)
        #                self.project_use_flag = True
        #            i = i + 1
        #except Exception as esd:
        #    _util.MessageboxShowError("error",str(esd))
        # -------------------------------------------------------------------------------------------------------------


        try:
            global _wsinfo
            iniSaturation = str(_wsinfo.subwatershedPars(int(selectWS)).iniSaturation)
            minSlopeChBed = str(_wsinfo.subwatershedPars(int(selectWS)).minSlopeChBed)
            minSlopeOF = str(_wsinfo.subwatershedPars(int(selectWS)).minSlopeOF)

            # 2018-03-12 박: 화면 수정
            UKType = str(_wsinfo.subwatershedPars(int(selectWS)).UKType)
            coefUK = str(_wsinfo.subwatershedPars(int(selectWS)).coefUK)

            minChBaseWidth = str(_wsinfo.subwatershedPars(int(selectWS)).minChBaseWidth)
            chRoughness = str(_wsinfo.subwatershedPars(int(selectWS)).chRoughness)
            dryStreamOrder = str(_wsinfo.subwatershedPars(int(selectWS)).dryStreamOrder)
            ccLCRoughness = str(_wsinfo.subwatershedPars(int(selectWS)).ccLCRoughness)
            ccSoilDepth = str(_wsinfo.subwatershedPars(int(selectWS)).ccSoilDepth)
            ccPorosity = str(_wsinfo.subwatershedPars(int(selectWS)).ccPorosity)
            ccWFSuctionHead = str(_wsinfo.subwatershedPars(int(selectWS)).ccWFSuctionHead)
            ccHydraulicK = str(_wsinfo.subwatershedPars(int(selectWS)).ccHydraulicK)
            iniFlow = str(_wsinfo.subwatershedPars(int(selectWS)).iniFlow)
            if iniFlow.upper() =="NONE":
                iniFlow ="0"


            self.txtIniSaturation.setText(iniSaturation)
            self.txtMinSlopeOF.setText(minSlopeOF)
            self.txtMinSlopeChBed.setText(minSlopeChBed)
            # Allsize=self.txtGrid_Size.text()
            # intAll = float(Allsize)
            # cal_MinChBaseWidth = intAll/10
            self.txtMinChBaseWidth.setText(str(minChBaseWidth))
            self.txtIniFlow.setText(str(iniFlow))
            self.txtChRoughness.setText(chRoughness)
            self.txtDryStreamOrder.setText(dryStreamOrder)
            self.txtCalCoefLCRoughness.setText(ccLCRoughness)
            self.txtCalCoefSoilDepth.setText(ccSoilDepth)
            self.txtCalCoefPorosity.setText(ccPorosity)
            self.txtCalCoefWFSuctionHead.setText(ccWFSuctionHead)
            self.txtCalCoefHydraulicK.setText(ccHydraulicK)

            # if UKType.upper()=="LINEAR":
            #     self.cmbUnsturatedType.setCurrentIndex(0)
            # else:
            #     self.cmbUnsturatedType.setCurrentIndex(1)
            #
            #self.selectText=self.cmbUnsturatedType.currentText()
            if UKType == "Linear":
                self.cmbUnsturatedType.setCurrentIndex(0)
                self.txtCoefUnsatruatedk.setEnabled(True)
            elif UKType == "Exponential":
                self.cmbUnsturatedType.setCurrentIndex(1)
                self.txtCoefUnsatruatedk.setEnabled(True)
            else:
                self.cmbUnsturatedType.setCurrentIndex(2)
                self.txtCoefUnsatruatedk.setEnabled(False)

            self.txtCoefUnsatruatedk.setText(coefUK)






            # else:
            #     iniSaturation = str(_wsinfo.subwatershedPars(int(selectWS)).iniSaturation)
            #     minSlopeChBed = str(_wsinfo.subwatershedPars(int(selectWS)).minSlopeChBed)
            #     minSlopeOF = str(_wsinfo.subwatershedPars(int(selectWS)).minSlopeOF)
            #
            #     # 2018-03-12 박: 화면 수정
            #     UKType = str(_new_wsinfo.subwatershedPars(int(selectWS)).UKType)
            #     coefUK = str(_new_wsinfo.subwatershedPars(int(selectWS)).coefUK)
            #
            #
            #     minChBaseWidth = str(_wsinfo.subwatershedPars(int(selectWS)).minChBaseWidth)
            #     chRoughness = str(_wsinfo.subwatershedPars(int(selectWS)).chRoughness)
            #     dryStreamOrder = str(_wsinfo.subwatershedPars(int(selectWS)).dryStreamOrder)
            #     ccLCRoughness = str(_wsinfo.subwatershedPars(int(selectWS)).ccLCRoughness)
            #     ccSoilDepth = str(_wsinfo.subwatershedPars(int(selectWS)).ccSoilDepth)
            #     ccPorosity = str(_wsinfo.subwatershedPars(int(selectWS)).ccPorosity)
            #     ccWFSuctionHead = str(_wsinfo.subwatershedPars(int(selectWS)).ccWFSuctionHead)
            #     ccHydraulicK = str(_wsinfo.subwatershedPars(int(selectWS)).ccHydraulicK)
            #     iniFlow = str(_wsinfo.subwatershedPars(int(selectWS)).iniFlow)
            #     self.txtIniSaturation.setText(iniSaturation)
            #     self.txtMinSlopeOF.setText(minSlopeOF)
            #     self.txtMinSlopeChBed.setText(minSlopeChBed)
            #     # Allsize=self.txtGrid_Size.text()
            #     # intAll = float(Allsize)
            #     # cal_MinChBaseWidth = intAll/10
            #     self.txtMinChBaseWidth.setText(str(minChBaseWidth))
            #     if iniFlow is None  or iniFlow =="None":
            #         self.txtIniFlow.setText("0")
            #     else:
            #         self.txtIniFlow.setText(iniFlow)
            #
            #     self.txtChRoughness.setText(chRoughness)
            #     self.txtDryStreamOrder.setText(dryStreamOrder)
            #     self.txtCalCoefLCRoughness.setText(ccLCRoughness)
            #     self.txtCalCoefSoilDepth.setText(ccSoilDepth)
            #     self.txtCalCoefPorosity.setText(ccPorosity)
            #     self.txtCalCoefWFSuctionHead.setText(ccWFSuctionHead)
            #     self.txtCalCoefHydraulicK.setText(ccHydraulicK)

        except Exception as e:
            self.txtIniSaturation.setText("1")
            self.txtMinSlopeOF.setText("0.0001")
            self.txtMinSlopeChBed.setText("0.0001")
            intAll = float(self.GridCellSize)
            if intAll>0:
                cal_MinChBaseWidth = intAll/10
            self.txtMinChBaseWidth.setText(str(cal_MinChBaseWidth))
            self.txtIniFlow.setText("0")

            self.cmbUnsturatedType.setCurrentIndex(0)
            self.txtCoefUnsatruatedk.setText('0.2')

            self.txtChRoughness.setText("0.045")
            self.txtDryStreamOrder.setText("0")
            self.txtCalCoefLCRoughness.setText("1")
            self.txtCalCoefSoilDepth.setText("1")
            self.txtCalCoefPorosity.setText("1")
            self.txtCalCoefWFSuctionHead.setText("1")
            self.txtCalCoefHydraulicK.setText("1")
            item1 = QListWidgetItem(str(_StreamWSID))
            # self.lisw_UserSet.addItem(item1)

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
            self.click_FlowContorGird()
        elif type == "flow":
            self.post_grid_remove2()
            self.watchpoint()
            self.click_FlowContorGird()

    # 폼 종료
    def Close_Form(self):
        self.close()

    def closeEvent(self, ev):
        # 화면 종료 하기 전에 딕셔너리에 값넣기
        self.InputDictionary()

        QtGui.QDialog.closeEvent(self, ev)
        global _FXCOL, _FYROW
        _FXCOL = 0
        _FYROW = 0


    def InputDictionary(self):
        # =========================simulation tab ===================================



        GRM._xmltodict['GRMProject']['ProjectSettings']['ComputationalTimeStep'] = self.spTimeStep_min.text()

        if self.chkStartingTime.isChecked():
            DateTime = self.dateTimeEdit.dateTime().toString("yyyy-MM-dd hh:mm")
            GRM._xmltodict['GRMProject']['ProjectSettings']['SimulStartingTime'] = DateTime
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['SimulStartingTime'] = "0"


        if self.chkParallel.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['IsParallel'] = 'true'
            GRM._xmltodict['GRMProject']['ProjectSettings']['MaxDegreeOfParallelism'] =self.spTimeStep_min_2.text()

        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['IsParallel'] = 'false'
            GRM._xmltodict['GRMProject']['ProjectSettings']['MaxDegreeOfParallelism'] ="-1"

        GRM._xmltodict['GRMProject']['ProjectSettings']['OutputTimeStep'] = self.txtOutput_time_step.text()
        GRM._xmltodict['GRMProject']['ProjectSettings']['SimulationDuration'] = self.txtSimulation_duration.text()
        GRM._xmltodict['GRMProject']['ProjectSettings']['OutputTimeStep'] = self.txtOutput_time_step.text()

        if self.chkInfiltration.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateInfiltration'] = 'true'
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateInfiltration'] = 'false'

        if self.chkSubsurfaceFlow.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateSubsurfaceFlow'] = 'true'
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateSubsurfaceFlow'] = 'false'

        if self.chkBaseFlow.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateBaseFlow'] = 'true'
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateBaseFlow'] = 'false'

        if self.chkFlowControl.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateFlowControl'] = 'true'
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['SimulateFlowControl'] = 'false'

        if self.chkmakeimage.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeIMGFile'] = 'true'
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeIMGFile'] = 'false'

        if self.chkmakeASC.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeASCFile'] = 'true'
        else :
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeASCFile'] = 'false'

        if self.chksoiSaturation.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeSoilSaturationDistFile'] = 'true'
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeSoilSaturationDistFile'] = 'false'

        if self.chkrfDistFile.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeRfDistFile'] = 'true'
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeRfDistFile'] = 'false'

        if self.chkrfaacDistfile.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeRFaccDistFile'] = 'true'
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeRFaccDistFile'] = 'false'

        if self.chkdischarge.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeFlowDistFile'] = 'true'
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['MakeFlowDistFile'] = 'false'

        if self.chklog.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['WriteLog'] = 'true'
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['WriteLog'] = 'false'

        GRM._xmltodict['GRMProject']['ProjectSettings']['PrintOption'] =self.cmbPrint.currentText()


        # 2018-03-06
        if self.chkfixeTimeStep.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['IsFixedTimeStep']= 'true'
        else:
            GRM._xmltodict['GRMProject']['ProjectSettings']['IsFixedTimeStep'] = 'false'

        # =========================simulation tab end ===============================================

        # =========================Watch Point tab===================================================
        #     GRM._WatchPointCount
        if GRM._WatchPointCount > 0:
            del GRM._xmltodict['GRMProject']['WatchPoints']
        GRM._WatchPointCount = self.tbList.rowCount()

        DictoXml = xmltodict.unparse(GRM._xmltodict)
        ET.register_namespace('', "http://tempuri.org/GRMProject.xsd")
        xmltree = ET.ElementTree(ET.fromstring(DictoXml))
        root = xmltree.getroot()

        wcount = self.tbList.rowCount()
        GRM._WatchPointCount = wcount
        for row in range(0, wcount):
            child = ET.Element("WatchPoints")
            root.append(child)

            WathchName = ET.Element("Name")
            WathchName.text = self.tbList.item(row, 0).text()
            child.append(WathchName)

            WathchColX = ET.Element("ColX")
            WathchColX.text = self.tbList.item(row, 1).text()
            child.append(WathchColX)

            WathchRowY = ET.Element("RowY")
            WathchRowY.text = self.tbList.item(row, 2).text()
            child.append(WathchRowY)
        xmltree_string = ET.tostring(xmltree.getroot())
        docs = dict(xmltodict.parse(xmltree_string))
        GRM._xmltodict.clear()
        GRM._xmltodict.update(docs)

        # =========================Wahch Point tab end===============================================

        # =========================Channel CS tab====================================================
        if self.rdo_single.isChecked() and self.rdo_useCh.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['CrossSectionType'] = "CSSingle"
            GRM._xmltodict['GRMProject']['ProjectSettings']['SingleCSChannelWidthType'] = "CWEquation"
            GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQc'] = self.txt_c.text()
            GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQd'] = self.txt_d.text()
            GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthEQe'] = self.txt_e.text()

        if self.rdo_single.isChecked() and self.rdo_generateCh.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['CrossSectionType'] = "CSSingle"
            GRM._xmltodict['GRMProject']['ProjectSettings']['SingleCSChannelWidthType'] = "CWGeneration"
            GRM._xmltodict['GRMProject']['ProjectSettings']['ChannelWidthMostDownStream'] = self.txt_douwnstream.text()

        if self.rdo_compound.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['CrossSectionType'] = "CSCompound"
            GRM._xmltodict['GRMProject']['ProjectSettings']['LowerRegionHeight'] = self.txtLower_Region_Height.text()
            GRM._xmltodict['GRMProject']['ProjectSettings']['LowerRegionBaseWidth'] = self.txtLower_Region_Base_Width.text()
            GRM._xmltodict['GRMProject']['ProjectSettings']['UpperRegionBaseWidth'] = self.txtUpper_Region_Base_Width.text()
            GRM._xmltodict['GRMProject']['ProjectSettings']['CompoundCSChannelWidthLimit'] = self.txtCompound_CSChannel_Width_Limit.text()

        GRM._xmltodict['GRMProject']['ProjectSettings']['BankSideSlopeRight'] = self.txtRight_bank.text()
        GRM._xmltodict['GRMProject']['ProjectSettings']['BankSideSlopeLeft'] = self.txtLeft_bank.text()

        # version
        #
        #
        # GRM._xmltodict['GRMProject']['ProjectSettings']['GRMVersion'] = version
        #


        # =========================Channel CS tab end================================================
        # =========================Flow Control Tab==================================================
        # 딕셔너리 삭제
        if GRM._FlowControlCount>0:
            del GRM._xmltodict['GRMProject']['FlowControlGrid']

        DictoXml = xmltodict.unparse(GRM._xmltodict)
        ET.register_namespace('', "http://tempuri.org/GRMProject.xsd")
        xmltree = ET.ElementTree(ET.fromstring(DictoXml))
        root = xmltree.getroot()
        fcount = self.tlbFlowControl.rowCount()
        _Flowcontrolgrid_xmlCount = fcount
        GRM._FlowControlCount = fcount

        for row in range(0, fcount):
            child = ET.Element("FlowControlGrid")
            root.append(child)
            #
            # GridValue = ET.Element("ColX")
            # GridValue.text = self.tlbFlowControl.item(row, 0).text()
            # child.append(GridValue)
            #
            # UserLandCover = ET.Element("RowY")
            # UserLandCover.text = self.tlbFlowControl.item(row, 1).text()
            # child.append(UserLandCover)
            #
            # GRMLandCoverCode = ET.Element("Name")
            # GRMLandCoverCode.text = self.tlbFlowControl.item(row, 2).text()
            # child.append(GRMLandCoverCode)

            GRMLandCoverCode = ET.Element("Name")
            GRMLandCoverCode.text = self.tlbFlowControl.item(row, 0).text()
            child.append(GRMLandCoverCode)

            GridValue = ET.Element("ColX")
            GridValue.text = self.tlbFlowControl.item(row, 1).text()
            child.append(GridValue)

            UserLandCover = ET.Element("RowY")
            UserLandCover.text = self.tlbFlowControl.item(row, 2).text()
            child.append(UserLandCover)

            DT = ET.Element("DT")
            DT.text = self.tlbFlowControl.item(row, 3).text()
            child.append(DT)

            ControlType = ET.Element("ControlType")
            testvalue = self.tlbFlowControl.item(row, 4).text()
            if testvalue == "Reservoir outflow":
                ControlType.text = "ReservoirOutflow"
            elif testvalue == "Reservoir operation":
                ControlType.text = "ReservoirOperation"
            elif testvalue == "Sink flow":
                ControlType.text = "SinkFlow"
            elif testvalue == "Source flow":
                ControlType.text = "SourceFlow"
            elif  testvalue == "Inlet":
                ControlType.text = "Inlet"
            child.append(ControlType)


            #
            # ControlType.text = self.tlbFlowControl.item(row, 4).text()
            # child.append(ControlType)

            FlowDataFile = ET.Element("FlowDataFile")
            FlowDataFile.text = self.tlbFlowControl.item(row, 5).text()
            child.append(FlowDataFile)

            try:
                IniStorage = ET.Element("IniStorage")
                storage = self.tlbFlowControl.item(row, 6).text()
                if storage != "":
                    IniStorage.text = self.tlbFlowControl.item(row, 6).text()
                else:
                    IniStorage.text = ""
                child.append(IniStorage)
            except :
                IniStorage = ET.Element("IniStorage")
                IniStorage.text = ""
                child.append(IniStorage)

            try:
                MaxStorage = ET.Element("MaxStorage")
                if self.tlbFlowControl.item(row, 7).text() != "":
                    MaxStorage.text = self.tlbFlowControl.item(row, 7).text()
                else:
                    MaxStorage.text = ""
                child.append(MaxStorage)
            except:
                 MaxStorage = ET.Element("MaxStorage")
                 MaxStorage.text = ""
                 child.append(MaxStorage)

            try:
                MaxStorageR = ET.Element("MaxStorageR")
                if self.tlbFlowControl.item(row, 8).text() != "":
                    MaxStorageR.text = self.tlbFlowControl.item(row, 8).text()
                else:
                    MaxStorageR.text = ""
                child.append(MaxStorageR)
            except:
                 MaxStorageR = ET.Element("MaxStorageR")
                 MaxStorageR.text = ""
                 child.append(MaxStorageR)

            try:
                ROType = ET.Element("ROType")
                if self.tlbFlowControl.item(row, 9).text() != "":
                    ROType.text = self.tlbFlowControl.item(row, 9).text()
                else:
                    ROType.text = ""
                child.append(ROType)
            except:
                 ROType = ET.Element("ROType")
                 ROType.text = ""
                 child.append(ROType)


            try:
                ROConstQ = ET.Element("ROConstQ")
                if self.tlbFlowControl.item(row, 10).text() != "":
                    ROConstQ.text = self.tlbFlowControl.item(row, 10).text()
                else:
                    ROConstQ.text = ""
                child.append(ROConstQ)
            except:
                ROConstQ = ET.Element("ROConstQ")
                ROConstQ.text = ""
                child.append(ROConstQ)

            try:
                ROConstQDuration = ET.Element("ROConstQDuration")
                if self.tlbFlowControl.item(row, 11).text() != "":
                    ROConstQDuration.text = self.tlbFlowControl.item(row, 11).text()
                else:
                    ROConstQDuration.text = ""
                child.append(ROConstQDuration)
            except:
                ROConstQDuration = ET.Element("ROConstQDuration")
                ROConstQDuration.text = ""
                child.append(ROConstQDuration)


        xmltree_string = ET.tostring(xmltree.getroot())
        docs = dict(xmltodict.parse(xmltree_string))
        GRM._xmltodict.clear()
        GRM._xmltodict.update(docs)

        # =========================Flow Control Tab end ==================================================
        # ========================= Watershed tab ========================================================
        if GRM._SubWatershedCount>0:
            del GRM._xmltodict['GRMProject']['SubWatershedSettings']
        DictoXml = xmltodict.unparse(GRM._xmltodict)
        ET.register_namespace('', "http://tempuri.org/GRMProject.xsd")
        xmltree = ET.ElementTree(ET.fromstring(DictoXml))
        root = xmltree.getroot()
        GRM._SubWatershedCount = self.cb_selectws.count()
        scount = self.cb_selectws.count()

        for row in range(0, scount):
            selectWS=self.cb_selectws.itemText(row)

            child = ET.Element("SubWatershedSettings")
            root.append(child)

            ID = ET.Element("ID")
            ID.text = selectWS
            child.append(ID)

            IniSaturation = ET.Element("IniSaturation")
            IniSaturation.text = str(_wsinfo.subwatershedPars(int(selectWS)).iniSaturation)
            child.append(IniSaturation)

            MinSlopeOF = ET.Element("MinSlopeOF")
            MinSlopeOF.text = str(_wsinfo.subwatershedPars(int(selectWS)).minSlopeOF)
            child.append(MinSlopeOF)

            MinSlopeChBed = ET.Element("MinSlopeChBed")
            MinSlopeChBed.text = str(_wsinfo.subwatershedPars(int(selectWS)).minSlopeChBed)
            child.append(MinSlopeChBed)

            MinChBaseWidth = ET.Element("MinChBaseWidth")
            MinChBaseWidth.text = str(_wsinfo.subwatershedPars(int(selectWS)).minChBaseWidth)
            child.append(MinChBaseWidth)

            ChRoughness = ET.Element("ChRoughness")
            ChRoughness.text = str(_wsinfo.subwatershedPars(int(selectWS)).chRoughness)
            child.append(ChRoughness)

            DryStreamOrder = ET.Element("DryStreamOrder")
            DryStreamOrder.text =  str(_wsinfo.subwatershedPars(int(selectWS)).dryStreamOrder)
            child.append(DryStreamOrder)

            IniFlow = ET.Element("IniFlow")
            if _wsinfo.subwatershedPars(int(selectWS)).iniFlow is None:
                IniFlow.text = "0"
            else:
                IniFlow.text = str(_wsinfo.subwatershedPars(int(selectWS)).iniFlow)
            child.append(IniFlow)

            UnsaturatedKType=ET.Element('UnsaturatedKType')
            UnsaturatedKType.text = str(_wsinfo.subwatershedPars(int(selectWS)).UKType)
            child.append(UnsaturatedKType)


            CoefUnsaturatedK=ET.Element('CoefUnsaturatedK')
            CoefUnsaturatedK.text = str(_wsinfo.subwatershedPars(int(selectWS)).coefUK)
            child.append(CoefUnsaturatedK)


            CalCoefLCRoughness = ET.Element("CalCoefLCRoughness")
            CalCoefLCRoughness.text =  str(_wsinfo.subwatershedPars(int(selectWS)).ccLCRoughness)
            child.append(CalCoefLCRoughness)

            CalCoefPorosity = ET.Element("CalCoefPorosity")
            CalCoefPorosity.text =str(_wsinfo.subwatershedPars(int(selectWS)).ccPorosity)
            child.append(CalCoefPorosity)

            CalCoefWFSuctionHead = ET.Element("CalCoefWFSuctionHead")
            CalCoefWFSuctionHead.text = str(_wsinfo.subwatershedPars(int(selectWS)).ccWFSuctionHead)
            child.append(CalCoefWFSuctionHead)

            CalCoefHydraulicK = ET.Element("CalCoefHydraulicK")
            CalCoefHydraulicK.text = str(_wsinfo.subwatershedPars(int(selectWS)).ccHydraulicK)
            child.append(CalCoefHydraulicK)

            CalCoefSoilDepth = ET.Element("CalCoefSoilDepth")
            CalCoefSoilDepth.text = str(_wsinfo.subwatershedPars(int(selectWS)).ccSoilDepth)
            child.append(CalCoefSoilDepth)

            UserSet = ET.Element("UserSet")
            UserSet.text = str(_wsinfo.subwatershedPars(int(selectWS)).isUserSet)
            child.append(UserSet)

        xmltree_string = ET.tostring(xmltree.getroot())
        docs = dict(xmltodict.parse(xmltree_string))
        GRM._xmltodict.clear()
        GRM._xmltodict.update(docs)
        # else:
        #     if GRM._SubWatershedCount>0:
        #         del GRM._xmltodict['GRMProject']['SubWatershedSettings']
        #
        #     DictoXml = xmltodict.unparse(GRM._xmltodict)
        #     ET.register_namespace('', "http://tempuri.org/GRMProject.xsd")
        #     xmltree = ET.ElementTree(ET.fromstring(DictoXml))
        #     root = xmltree.getroot()
        #     GRM._SubWatershedCount = self.cb_selectws.count()
        #     count = self.cb_selectws.count()
        #
        #     for row in range(0, count):
        #         selectWS = self.cb_selectws.itemText(row)
        #         child = ET.Element("SubWatershedSettings")
        #         root.append(child)
        #
        #         ID = ET.Element("ID")
        #         ID.text = selectWS
        #         child.append(ID)
        #
        #
        #         IniSaturation = ET.Element("IniSaturation")
        #         IniSaturation.text = str(_wsinfo.subwatershedPars(int(selectWS)).iniSaturation)
        #         child.append(IniSaturation)
        #
        #         MinSlopeOF = ET.Element("MinSlopeOF")
        #         MinSlopeOF.text = str(_wsinfo.subwatershedPars(int(selectWS)).minSlopeOF)
        #         child.append(MinSlopeOF)
        #
        #         MinSlopeChBed = ET.Element("MinSlopeChBed")
        #         MinSlopeChBed.text = str(_wsinfo.subwatershedPars(int(selectWS)).minSlopeChBed)
        #         child.append(MinSlopeChBed)
        #
        #         MinChBaseWidth = ET.Element("MinChBaseWidth")
        #         MinChBaseWidth.text = str(_wsinfo.subwatershedPars(int(selectWS)).minChBaseWidth)
        #         child.append(MinChBaseWidth)
        #
        #         ChRoughness = ET.Element("ChRoughness")
        #         ChRoughness.text = str(_wsinfo.subwatershedPars(int(selectWS)).chRoughness)
        #         child.append(ChRoughness)
        #
        #         DryStreamOrder = ET.Element("DryStreamOrder")
        #         DryStreamOrder.text = str(_wsinfo.subwatershedPars(int(selectWS)).dryStreamOrder)
        #         child.append(DryStreamOrder)
        #
        #         IniFlow = ET.Element("IniFlow")
        #         if _wsinfo.subwatershedPars(int(selectWS)).iniFlow is None:
        #             IniFlow.text ="0"
        #         else:
        #             IniFlow.text = str(_wsinfo.subwatershedPars(int(selectWS)).iniFlow)
        #         child.append(IniFlow)
        #
        #         UnsaturatedKType=ET.Element('UnsaturatedKType')
        #         UnsaturatedKType.text = str(_new_wsinfo.subwatershedPars(int(selectWS)).UnsKType)
        #         child.append(UnsaturatedKType)
        #
        #
        #         CoefUnsaturatedK=ET.Element('CoefUnsaturatedK')
        #         CoefUnsaturatedK.text = str(_new_wsinfo.subwatershedPars(int(selectWS)).coefUnsK)
        #         child.append(CoefUnsaturatedK)
        #
        #
        #         CalCoefLCRoughness = ET.Element("CalCoefLCRoughness")
        #         CalCoefLCRoughness.text = str(_wsinfo.subwatershedPars(int(selectWS)).ccLCRoughness)
        #         child.append(CalCoefLCRoughness)
        #
        #         CalCoefPorosity = ET.Element("CalCoefPorosity")
        #         CalCoefPorosity.text = str(_wsinfo.subwatershedPars(int(selectWS)).ccPorosity)
        #         child.append(CalCoefPorosity)
        #
        #         CalCoefWFSuctionHead = ET.Element("CalCoefWFSuctionHead")
        #         CalCoefWFSuctionHead.text = str(_wsinfo.subwatershedPars(int(selectWS)).ccWFSuctionHead)
        #         child.append(CalCoefWFSuctionHead)
        #
        #         CalCoefHydraulicK = ET.Element("CalCoefHydraulicK")
        #         CalCoefHydraulicK.text = str(_wsinfo.subwatershedPars(int(selectWS)).ccHydraulicK)
        #         child.append(CalCoefHydraulicK)
        #
        #         CalCoefSoilDepth = ET.Element("CalCoefSoilDepth")
        #         CalCoefSoilDepth.text = str(_wsinfo.subwatershedPars(int(selectWS)).ccSoilDepth)
        #         child.append(CalCoefSoilDepth)
        #
        #         UserSet = ET.Element("UserSet")
        #         UserSet.text = str(_wsinfo.subwatershedPars(int(selectWS)).isUserSet)
        #         child.append(UserSet)
        #
        #     xmltree_string = ET.tostring(xmltree.getroot())
        #     docs = dict(xmltodict.parse(xmltree_string))
        #     GRM._xmltodict.clear()
        #     GRM._xmltodict.update(docs)


        # # Watershed Parmeters 탭
        # GRM._xmltodict['GRMProject']['SubWatershedSettings']['IniSaturation'] = self.txtIniSaturation.text()
        # GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinSlopeOF']=self.txtMinSlopeOF.text()
        # GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinSlopeChBed']=self.txtMinSlopeChBed.text()
        # GRM._xmltodict['GRMProject']['SubWatershedSettings']['MinChBaseWidth']=self.txtMinChBaseWidth.text()
        # GRM._xmltodict['GRMProject']['SubWatershedSettings']['ChRoughness']=self.txtChRoughness.text()
        # GRM._xmltodict['GRMProject']['SubWatershedSettings']['DryStreamOrder']=self.txtDryStreamOrder.text()
        # GRM._xmltodict['GRMProject']['SubWatershedSettings']['IniFlow']=self.txtIniFlow.text()
        # GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefLCRoughness']=self.txtCalCoefLCRoughness.text()
        # GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefSoilDepth']=self.txtCalCoefSoilDepth.text()
        # GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefPorosity']=self.txtCalCoefPorosity.text()
        # GRM._xmltodict['GRMProject']['SubWatershedSettings']['CalCoefWFSuctionHead']=self.txtCalCoefWFSuctionHead.text()
        #
        #
        #
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

        self.post_grid_remove2()
        if self.chkFlowContorGird.isChecked():
            self.FlowContorGird_paint()
        if self.chkWatch_Point.isChecked():
            self.watchpoint_paint()


    # def MoveUp(self):
    #     fixcount=len(self.Fixed)
    #     row = self.tbList.currentRow()
    #     column = self.tbList.currentColumn()
    #     if row > 0:
    #         if row-1 > fixcount-1:
    #             self.tbList.insertRow(row - 1)
    #             for i in range(self.tbList.columnCount()):
    #                 self.tbList.setItem(row - 1, i, self.tbList.takeItem(row + 1, i))
    #                 self.tbList.setCurrentCell(row - 1, column)
    #             self.tbList.removeRow(row + 1)

    def MoveUp(self):
        row = self.tbList.currentRow()
        column = self.tbList.currentColumn()
        if row > 0:
            self.tbList.insertRow(row - 1)
            for i in range(self.tbList.columnCount()):
                self.tbList.setItem(row - 1, i, self.tbList.takeItem(row + 1, i))
                self.tbList.setCurrentCell(row - 1, column)
            self.tbList.removeRow(row + 1)



    # def MoveDown(self):
    #     fixcount=len(self.Fixed)
    #     row = self.tbList.currentRow()
    #     column = self.tbList.currentColumn()
    #     if row < self.tbList.rowCount() - 1:
    #         if row > fixcount-1:
    #             self.tbList.insertRow(row + 2)
    #             for i in range(self.tbList.columnCount()):
    #                 self.tbList.setItem(row + 2, i, self.tbList.takeItem(row, i))
    #                 self.tbList.setCurrentCell(row + 2, column)
    #             self.tbList.removeRow(row)

    def MoveDown(self):
        row = self.tbList.currentRow()
        column = self.tbList.currentColumn()
        if row < self.tbList.rowCount() - 1:
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
                text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter name:',QLineEdit.Normal,"")
                if text.strip()!="":
                    if self.check_add_watchpoint(_YROW,_XCOL,text):
                        self.tbList.insertRow(rowCount)
                        self.tbList.setItem(rowCount, 0, QTableWidgetItem(text))
                        self.tbList.setItem(rowCount, 1, QTableWidgetItem(str(_YROW)))
                        self.tbList.setItem(rowCount, 2, QTableWidgetItem(str(_XCOL)))
                        if self.chkWatch_Point.isChecked():
                            self.row_cols_grid(_YROW, _XCOL, "watchpoint")
                    else:
                        _util.MessageboxShowInfo("GRM", " Name or watchpoint is required. ")
                else:
                    _util.MessageboxShowInfo("GRM"," Name is required. ")
            else:
                text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter name:',QLineEdit.Normal,"")
                if text.strip() != "":
                    self.tbList.insertRow(0)
                    self.tbList.setItem(rowCount, 0, QTableWidgetItem(text))
                    self.tbList.setItem(0, 1, QTableWidgetItem(str(_YROW)))
                    self.tbList.setItem(0, 2, QTableWidgetItem(str(_XCOL)))
                    if self.chkWatch_Point.isChecked():
                        self.row_cols_grid(_YROW, _XCOL, "watchpoint")
                else:
                    _util.MessageboxShowInfo("GRM", " Name is required. ")


    def check_add_watchpoint(self,x,y,name):
        rowCount = self.tbList.rowCount()
        self.RetBool= True
        for row in range(0, rowCount):
            Names = self.tbList.item(row,0).text()
            X = self.tbList.item(row, 1).text()
            Y = self.tbList.item(row, 2).text()
            if (X==str(x) and Y==str(y) ) or name==Names :
                self.RetBool= False
        return self.RetBool



    # 에디트 클릭시에 선택된 Row 의 name 변경
    def Edit(self):
        # 현재 선택된 Row
        row=self.tbList.currentRow()
        cell = self.tbList.item(row, 0).text()
        # 다이얼 로그 출력하여 사용자가 셀값 제정의
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter name:',QLineEdit.Normal,cell)
        if ok:
            item = QTableWidgetItem(str(text))  # create a new Item
            self.tbList.setItem(row, 0, item)

#
#     # 2017/11/22 -----------------------------임시.. 불완전
#
    #테이블의 Row cols의 위치로 view 이동
    def GoToGrid(self):
        # 사용자가 선택한 영역 표시를 vertex marker 로 표시 할때  사라지게 해야 하는데 그게 안됨

        if self.chkFlowContorGird.isChecked():
            self.FlowContorGird_paint()
        if self.chkWatch_Point.isChecked():
            self.watchpoint_paint()

        row = self.tbList.currentRow()
        ColX = int(self.tbList.item(row, 1).text())
        RowY = int(self.tbList.item(row, 2).text())
        self.row_cols_grid(ColX,RowY,None)

    def btnFCGotoGrid(self):
        # 사용자가 선택한 영역 표시를 vertex marker 로 표시 할때  사라지게 해야 하는데 그게 안됨

        if self.chkFlowContorGird.isChecked():
            self.FlowContorGird_paint()
        if self.chkWatch_Point.isChecked():
            self.watchpoint_paint()

        row = self.tlbFlowControl.currentRow()

        # ColX = int(self.tlbFlowControl.item(row, 0).text())
        # RowY = int(self.tlbFlowControl.item(row, 1).text())

        ColX = int(self.tlbFlowControl.item(row, 1).text())
        RowY = int(self.tlbFlowControl.item(row, 2).text())
        self.row_cols_grid(ColX, RowY, None)




    def FlowContorGird_paint(self):
        counts = self.tlbFlowControl.rowCount()
        for i in range(0,counts):
            xvalue = _xmin + _xsize / 2 + _xsize * (int(self.tlbFlowControl.item(i, 1).text()))
            yvalue = _ymax - _ysize / 2 - _ysize * (int(self.tlbFlowControl.item(i, 2).text()))
            self.draw_grid2(xvalue,yvalue,self.btnColorPicker_3)

    def watchpoint_paint(self):
        if len(self.ColX)>0 and len(self.RowY)>0:
            if self.tbList.rowCount()>0:
                for i in range(0,self.tbList.rowCount()):
                    x=self.tbList.item(i, 1).text()
                    y=self.tbList.item(i, 2).text()
                    self.row_cols_grid(int(x),int(y),"watchpoint")
            else:
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
                global Cell_X_Center1,Cell_Y_Center1
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
            if issubclass(type(v), QgsVertexMarker):
                self.mapcanvas.scene().removeItem(v)
                #self.mapcanvas().refresh()


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
        size=_xsize/2
        points = [[QgsPoint(x - size, y + size), QgsPoint(x - size, y - size), QgsPoint(x + size, y - size),QgsPoint(x + size, y + size)]]
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
        try:
            self.canvas.scaleChanged.disconnect(self.scale_change_marker)
        except:
            pass
     #canvas scale이 변화할 때  marker를 새로 그림
    def scale_change_marker(self):
        #global Cell_X_Center,Cell_Y_Center
        self.post_vertex_remove()
        self.create_vertex(Cell_X_Center,Cell_Y_Center)

     #이전에 생성한 vertexMaker제거 함
    def post_vertex_remove(self):
        for v in self.canvas.scene().items():
            if issubclass(type(v), QgsVertexMarker):
                self.canvas.scene().removeItem(v)

        # for v in self.canvas.scene().items():
        #     if issubclass(type(v), QgsRubberBand) == True:
        #         self.canvas.scene().removeItem(v)


    def create_vertex(self,x,y):

        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(QgsPoint(x, y))
        marker.setColor(QColor(255, 0, 0))
        width_Map = self.canvas.extent().xMaximum() - self.canvas.extent().xMinimum()
        Size_Marker = (_xsize / 200.0) * 100000 / width_Map
        marker.setIconSize(Size_Marker)
        marker.setIconType(QgsVertexMarker.ICON_BOX)
        marker.setPenWidth(1)

        #2018-0313 박:
        # r1 = QgsRubberBand(self.canvas, True)
        # r2 = QgsRubberBand(self.canvas, True)
        # r3 = QgsRubberBand(self.canvas, True)
        # r4 = QgsRubberBand(self.canvas, True)
        # size = _xsize / 2
        # #points = [[QgsPoint(x - size, y + size), QgsPoint(x - size, y - size), QgsPoint(x + size, y - size),QgsPoint(x + size, y + size)]]
        # #r.setToGeometry(QgsGeometry.fromPolygon(points), None)
        # r1.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(x - size, y + size), QgsPoint(x - size, y - size)]),None)
        # r2.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(x - size, y - size), QgsPoint(x + size, y - size)]),None)
        # r3.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(x + size, y - size), QgsPoint(x + size, y + size)]),None)
        # r4.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(x + size, y + size), QgsPoint(x - size, y + size)]),None)
        # r1.setColor(QColor(255,0,0))
        # r2.setColor(QColor(255,0,0))
        # r3.setColor(QColor(255,0,0))
        # r4.setColor(QColor(255,0,0))
        # r1.setWidth(1)
        # r2.setWidth(1)
        # r3.setWidth(1)
        # r4.setWidth(1)
             

        # marker = QgsVertexMarker(self.canvas)
        # marker.setCenter(QgsPoint(x,y))
        # marker.setColor(QColor(255,0,0))
        # scale = self.canvas.scale()
        # size = 750000.0 / scale
        # marker.setIconSize(size)
        # marker.setIconType(QgsVertexMarker.ICON_BOX)
        # marker.setPenWidth(1)





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
            self.Input_Cell_Value(row, column)
            if row < 0 or column < 0 or _height<=column or _width <= row :
                row = "out of extent"
                column="out of extent"

            else:
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
        watershed = _wsinfo.watershedID(x,y)


        _util.GlobalControl_SetValue(CellType_Result,str(Stream_Result), FD_Result, str(FA_Result), str(Slop_Result),str(watershed))

        Texture_Result=_wsinfo.soilTextureValue(x,y)

        # Cell Info Depth 그룹 박스 테이터 내용
        Depth_Result = _wsinfo.soilDepthValue(x,y)

        # Cell Info Landcover 그룹 박스 테이터 내용
        Landcover_Result = _wsinfo.landCoverValue(x,y)

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


        for element in root.findall('{http://tempuri.org/GRMProject.xsd}SoilDepth'):
            GridValue=element.findtext("{http://tempuri.org/GRMProject.xsd}GridValue")
            if str(Depth_Result)==GridValue:
                UserDepthClass=element.findtext("{http://tempuri.org/GRMProject.xsd}GRMCode")
                SoilDepth=element.findtext("{http://tempuri.org/GRMProject.xsd}SoilDepth")
                _util.GlobalControl_Depth_SetValue(GridValue, UserDepthClass, SoilDepth)
                break
            elif Depth_Result is None or Depth_Result=="":
                break

        # 최박사님과 협의 할것 (2018 03 04)
        for element in root.findall('{http://tempuri.org/GRMProject.xsd}LandCover'):
            GridValue = element.findtext("{http://tempuri.org/GRMProject.xsd}GridValue")
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



