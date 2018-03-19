# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GRMDockWidget
                                 A QGIS plugin
 GRM Plugin
                             -------------------
        begin                : 2017-05-11
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
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QFileInfo
from qgis.core import QgsMapLayerRegistry
from ElementTree import *
import ElementTree as ET
import Util
from AddFlowControlGrid_dialog import AddFlowControlGridDialog
from fAnalyzer_dialog import FAnalyzerDialog
from Watershed_Stetup_dialog import  Watershed_StetupDialog
from fSetWatershed_dialog import FSetWatershedDialog
from Call_EXE_dialog import Call_EXE_arg_Dialog
from View_Chart_dialog import View_ChartDialog
from SetLCST_dialog import SetLCST_StetupDialog
from plugin.dict2xml import dict2xml
from Rainfall_dialog import RainFallDialog
import xmltodict
import GRM_Plugin
import GRM_GetSet
import shutil
import sys
import clr
import System
import XMLMake
from XMLCheck import xmls
sys.path.insert(0, 'C:\\Program Files\\QGIS 2.18\\apps\Python27\\Lib\\xml\\etree')
import time

import clr
DllPath = os.path.dirname(os.path.realpath(__file__)) + "\DLL\GRMCore.dll"
clr.AddReference(DllPath)
import GRMCore
from GRMCore import GRMProject


reload(sys)
sys.setdefaultencoding('utf8')

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'GRM_Plugin_dockwidget_base.ui'))

path = os.path.dirname(os.path.realpath(__file__))
Project = path +'\image\Folder_3.png'
InputData =  path +'\image\database.png'
RunGRM =  path +'\image\settings.png'
GRMTools = path + '\image\Tool.png'
Help =  path +'\image\information.png'
Analysis =  path +'\image\Analysis.png'
Flask =  path +'\image\Flask.png'
_util = Util.util()

_item0 = QtGui.QTreeWidgetItem()
_ProjectFlage = False
_ProjectFile=""
_xmltodict={}
_XmlMake = XMLMake.make()
_XmlCheck = xmls()

_SubWatershedCount = 0
_WatchPointCount = 0
_FlowControlCount = 0
_GreenAmptCount = 0
_SoilDepthCount = 0
_LandCoverCount = 0
_RainFallCount=0

class GRMDockWidget(QtGui.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    """Constructor."""
    def __init__(self, parent=None):
        super(GRMDockWidget, self).__init__(parent)

        self.setupUi(self)
        # 화면 초기화
        self.initUI()

    # tree widget 초기화 시키고 다시 메뉴 셋팅(프로젝트 파일 로드후 비활성화 메뉴 활성화로 변경)
    def clear(self):
        self.treeWidget.clear()
        self.Newset()

    def Newset(self):
        # 트리 메뉴가 비활성화 되어도 더블클릭 이베트가 먹히는 현상으로 인해 플래그 설정
        global _ProjectFlage
        _ProjectFlage = True

        # treeWidget refresh 문제로 메뉴 항목 재설정
        self.setWindowTitle("GRM")

        # Qtree 박스에 헤더 부분 제거
        self.treeWidget.setHeaderHidden(True)

        result = _util.CheckTaudem()
        if (result == False):
            _util.MessageboxShowError("Drainage", "Taudem is not installed.")

        item0 = QtGui.QTreeWidgetItem(self.treeWidget, ['Project'])
        item01 = QtGui.QTreeWidgetItem(item0, ['New Project'])
        item02 = QtGui.QTreeWidgetItem(item0, ['Open Project'])
        item03 = QtGui.QTreeWidgetItem(item0, ['Save Project'])
        item04 = QtGui.QTreeWidgetItem(item0, ['Save As Project'])
        # 기능 제거
        # item05 = QtGui.QTreeWidgetItem(item0, ['Project info'])
        icon = QtGui.QIcon(Project)
        item0.setIcon(0, icon)


        item1 = QtGui.QTreeWidgetItem(self.treeWidget, ['Setup input data'])
        item11 = QtGui.QTreeWidgetItem(item1, ['Watershed'])
        # item111 = QtGui.QTreeWidgetItem(item11, ['python Watershed'])
        # item112 = QtGui.QTreeWidgetItem(item11, ['Exe Watershed'])
        item12 = QtGui.QTreeWidgetItem(item1, ['Land Cover / Soil'])
        item13 = QtGui.QTreeWidgetItem(item1, ['Rainfall'])
        icon = QtGui.QIcon(InputData)
        item1.setIcon(0, icon)

        item2 = QtGui.QTreeWidgetItem(self.treeWidget, ['Run GRM'])
        item21 = QtGui.QTreeWidgetItem(item2, ['Setup / Run GRM'])
        item22 = QtGui.QTreeWidgetItem(item2, ['Output Table'])
        item23 = QtGui.QTreeWidgetItem(item2, ['Output Graph'])
        item24 = QtGui.QTreeWidgetItem(item2, ['GRM Multiple Events'])
        icon = QtGui.QIcon(RunGRM)
        item2.setIcon(0, icon)

        item3 = QtGui.QTreeWidgetItem(self.treeWidget, ['Uncertainty Analysis'])
        item31 = QtGui.QTreeWidgetItem(item3, ['Uncertainty'])
        icon = QtGui.QIcon(Analysis)
        item3.setIcon(0, icon)

        item4 = QtGui.QTreeWidgetItem(self.treeWidget, ['GRM Tools'])
        item41 = QtGui.QTreeWidgetItem(item4, ['Make RainFall Grid Layers with point time Series'])
        item42 = QtGui.QTreeWidgetItem(item4, ['Raster File Processing'])
        item43 = QtGui.QTreeWidgetItem(item4, ['Grid Rainfall Calibration'])
        item44 = QtGui.QTreeWidgetItem(item4, ['Generate Precipitation from Satellite Data'])
        item45 = QtGui.QTreeWidgetItem(item4, ['Grid Data Series Analysis'])
        item46 = QtGui.QTreeWidgetItem(item4, ['Create Soil Grid Layers'])
        icon = QtGui.QIcon(GRMTools)
        item4.setIcon(0, icon)

        item5 = QtGui.QTreeWidgetItem(self.treeWidget, ['Help'])
        item51 = QtGui.QTreeWidgetItem(item5, ['Helps'])
        # 아이콘 설정
        icon = QtGui.QIcon(Help)
        item5.setIcon(0, icon)



        # 2017/09/05 시연으로 인해서 기능 중지
        item6 = QtGui.QTreeWidgetItem(self.treeWidget, ['GRM_Forms'])
        item61 = QtGui.QTreeWidgetItem(item6, ['Call_GRM_EXE'])
        item62 = QtGui.QTreeWidgetItem(item6, ['Add Flow Control Grid'])
        item63 = QtGui.QTreeWidgetItem(item6, ['Analyzer'])
        item64 = QtGui.QTreeWidgetItem(item6, ['Watershed Stetup'])
        item65 = QtGui.QTreeWidgetItem(item6, ['Set Watershed'])
        item66 = QtGui.QTreeWidgetItem(item65, ['python Watershed'])
        item67 = QtGui.QTreeWidgetItem(item65, ['Exe Watershed'])
        item68 = QtGui.QTreeWidgetItem(item6, ['View Chart'])
        icon = QtGui.QIcon(Flask)
        item6.setIcon(0, icon)

        self.mainLayout = QtGui.QGridLayout(self)
        self.mainLayout.addWidget(self.treeWidget)
        # self.treeWidget.itemDoubleClicked.connect(self.OnDoubleClick)


    def initUI(self):
        self.setWindowTitle("GRM")

        # 배경 색상 회색
        # self.treeWidget.setStyleSheet("background-color: gray;")
        self.treeWidget.setItemsExpandable(True)
        self.treeWidget.setAnimated(True)
        self.treeWidget.setItemsExpandable(True)
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderLabels([''])

        # Qtree 박스에 헤더 부분 제거
        self.treeWidget.setHeaderHidden(True)

        result = _util.CheckTaudem()
        if (result == False):
            _util.MessageboxShowError("Drainage", "Taudem is not installed.")

        item0 = QtGui.QTreeWidgetItem(self.treeWidget, ['Project'])
        item01 = QtGui.QTreeWidgetItem(item0, ['New Project'])
        item02 = QtGui.QTreeWidgetItem(item0, ['Open Project'])
        item03 = QtGui.QTreeWidgetItem(item0, ['Save Project'])
        item03.setDisabled(True)
        item04 = QtGui.QTreeWidgetItem(item0, ['Save As Project'])
        item04.setDisabled(True)
        # 기능 제거
        # item05 = QtGui.QTreeWidgetItem(item0, ['Project info'])
        # item05.setDisabled(True)
        icon = QtGui.QIcon(Project)
        item0.setIcon(0, icon)



        item1 = QtGui.QTreeWidgetItem(self.treeWidget, ['Setup input data'])
        item11 = QtGui.QTreeWidgetItem(item1, ['Watershed'])
        # item111 = QtGui.QTreeWidgetItem(item11, ['python Watershed'])
        # item112 = QtGui.QTreeWidgetItem(item11, ['Exe Watershed'])
        item12 = QtGui.QTreeWidgetItem(item1, ['Land Cover / Soil'])
        item13 = QtGui.QTreeWidgetItem(item1, ['Rainfall'])
        icon = QtGui.QIcon(InputData)
        item1.setIcon(0, icon)
        item1.setDisabled(True)

        item2 = QtGui.QTreeWidgetItem(self.treeWidget, ['Run GRM'])
        item21 = QtGui.QTreeWidgetItem(item2, ['Setup / Run GRM'])
        item22 = QtGui.QTreeWidgetItem(item2, ['Output Table'])
        item23 = QtGui.QTreeWidgetItem(item2, ['Output Graph'])
        item24 = QtGui.QTreeWidgetItem(item2, ['GRM Multiple Events'])
        icon = QtGui.QIcon(RunGRM)
        item2.setIcon(0, icon)
        item2.setDisabled(True)

        item3 = QtGui.QTreeWidgetItem(self.treeWidget, ['Uncertainty Analysis'])
        item31 = QtGui.QTreeWidgetItem(item3, ['Uncertainty'])
        icon = QtGui.QIcon(Analysis)
        item3.setIcon(0, icon)
        item3.setDisabled(True)

        item4 = QtGui.QTreeWidgetItem(self.treeWidget, ['GRM Tools'])
        item41 = QtGui.QTreeWidgetItem(item4, ['Make RainFall Grid Layers with point time Series'])
        item42 = QtGui.QTreeWidgetItem(item4, ['Raster File Processing'])
        item43 = QtGui.QTreeWidgetItem(item4, ['Grid Rainfall Calibration'])
        item44 = QtGui.QTreeWidgetItem(item4, ['Generate Precipitation from Satellite Data'])
        item45 = QtGui.QTreeWidgetItem(item4, ['Grid Data Series Analysis'])
        item46 = QtGui.QTreeWidgetItem(item4, ['Create Soil Grid Layers'])
        icon = QtGui.QIcon(GRMTools)
        item4.setIcon(0, icon)
        item4.setDisabled(True)

        item5 = QtGui.QTreeWidgetItem(self.treeWidget, ['Help'])
        item51 = QtGui.QTreeWidgetItem(item5, ['Helps'])
        #아이콘 설정
        icon = QtGui.QIcon(Help)
        item5.setIcon(0, icon)
        item5.setDisabled(True)

        item6 = QtGui.QTreeWidgetItem(self.treeWidget, ['GRM_Forms'])
        item61 = QtGui.QTreeWidgetItem(item6, ['Call_GRM_EXE'])
        item62 = QtGui.QTreeWidgetItem(item6, ['Add Flow Control Grid'])
        item63 = QtGui.QTreeWidgetItem(item6, ['Analyzer'])
        item64 = QtGui.QTreeWidgetItem(item6, ['Watershed Stetup'])
        item65 = QtGui.QTreeWidgetItem(item6, ['Set Watershed'])
        item66 = QtGui.QTreeWidgetItem(item65, ['python Watershed'])
        item67 = QtGui.QTreeWidgetItem(item65, ['Exe Watershed'])
        item68 = QtGui.QTreeWidgetItem(item6, ['View Chart'])
        icon = QtGui.QIcon(Flask)
        item6.setIcon(0, icon)

        self.mainLayout = QtGui.QGridLayout(self)
        self.mainLayout.addWidget(self.treeWidget)
        # 더블 클릭 했을대 메뉴 명칭 확인
        self.treeWidget.itemDoubleClicked.connect(self.OnDoubleClick)

    def OnDoubleClick(self, item):
        SelectItme = item.text(0)
        # 프로젝트 파일 오픈
        if SelectItme == 'Open Project':
            self.Select_Project_File()
        # 프로젝트 파일 생성
        elif SelectItme=="New Project":
            self.NewProjectFile()
        elif SelectItme =="Save Project":
            self.SaveProjectFile()
        elif SelectItme =="Save As Project":
            self.SaveASProjectFile()
        elif SelectItme == 'Add Flow Control Grid':
            results_dialog = AddFlowControlGridDialog()
            results_dialog.exec_()
        elif SelectItme =='Analyzer':
            results_dialog = FAnalyzerDialog()
            results_dialog.exec_()
            # Setup / Run GRM
        #     20170905 박: 시연 위해서 기능 변경
        # elif SelectItme=='Watershed Stetup':
        elif SelectItme == 'Setup / Run GRM':
            # 3가지 사전 기능을 완료 했을때 시행
            #chWatershed = _xmltodict['GRMProject']['ProjectSettings']['WatershedCheck']
            #if chWatershed != "True":
            #    _util.MessageboxShowInfo("Setup / Run GRM","The watershed feature has not been implemented.")
            #    return

            #chRainfall = _xmltodict['GRMProject']['ProjectSettings']['RainfallCheck']
            #if chRainfall != "True":
            #    _util.MessageboxShowInfo("Setup / Run GRM","The Rainfall feature has not been implemented.")
            #    return

            #chLandCover = _xmltodict['GRMProject']['ProjectSettings']['LandCoverCheck']
            #if chLandCover != "True":
            #    _util.MessageboxShowInfo("Setup / Run GRM","The Land cover / soil feature has not been implemented.")
            #    return

            #if chWatershed =="True" and chRainfall =="True" and chLandCover =="True" :
            results_dialog = Watershed_StetupDialog()
            results_dialog.exec_()

        elif SelectItme=='Watershed':
            results_dialog = FSetWatershedDialog()
            results_dialog.exec_()
        elif SelectItme == "Output Graph":
            exeFile = os.path.dirname(os.path.abspath(__file__)) + "\ChartEXE.exe"
            chartDischarge= os.path.splitext(_ProjectFile)[0] + "Discharge.out"
            _util.MessageboxShowInfo("base",str(chartDischarge))
            arg = '"' + exeFile + '"' + " " + '"' +chartDischarge + '"'
            _util.Execute(arg)
        elif SelectItme =="Output Table" :
            results_dialog = View_ChartDialog()
            results_dialog.exec_()
        elif SelectItme =="Rainfall":
            results = RainFallDialog()
            results.exec_()
        elif SelectItme == "Call_GRM_EXE":
            exeFile = os.path.dirname(os.path.abspath(__file__)) +"\GRM.exe"
            arg = '"' + exeFile+ '"' + " " + '"' + _ProjectFile + '"'
            _util.MessageboxShowInfo("test",arg)
            _util.Execute(arg)
        elif SelectItme =="Land Cover / Soil":
            results_dialog = SetLCST_StetupDialog()
            results_dialog.exec_()
        elif SelectItme == "Uncertainty":
            _xmltodict['GRMProject']['ProjectSettings']['ChannelWidthFile']="test"
            test = _xmltodict['GRMProject']['ProjectSettings']['ChannelWidthFile']
            _util.MessageboxShowInfo("FDType", test)

    def CloseEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


    def Select_Project_File(self):
        # 프로젝트 파일 찾을 다이얼 로그
        global _ProjectFile,_xmltodict
        # self.filename = "C:\GRM\Sample\SampleProject.gmp"



        # self.filename ="C:\\GRM\\NGD\\ngd.gmp"
        # # 기존에 사용 하던 경로를 디폴트로 여는 옵션 적용 options=QtGui.QFileDialog.DontUseNativeDialog
        self.filename = QtGui.QFileDialog.getOpenFileName(self,'select output file','','GRM Project xml files (*.gmp)',options=QtGui.QFileDialog.DontUseNativeDialog)
        _ProjectFile = self.filename
        _XmlCheck.Check_Gmp_xml(self.filename)
        # 프로젝트 파일 확인 후에 QtreeWidget 재설정(비활성화 메뉴 활성화)
        if len(self.filename)>0:
            self.clear()
        # 2017/09/17 프로젝트 파일(XML)을 그냥 일반 문서 처럼 읽어옴
        Projectfile = open(self.filename, 'r')
        data = Projectfile.read()
        Projectfile.close()
        # 읽어온 파일 내용(XML)을 dictionary 로 변경
        self.doc = dict(xmltodict.parse(data))
        _xmltodict = self.doc

        # dictionary 값을 받아서 레이어 목록을 Qgis 에 올림
        self.AddlayerQGIS(self.doc['GRMProject']['ProjectSettings']['WatershedFile'])
        self.AddlayerQGIS(self.doc['GRMProject']['ProjectSettings']['SlopeFile'])
        self.AddlayerQGIS(self.doc['GRMProject']['ProjectSettings']['FlowDirectionFile'])
        self.AddlayerQGIS(self.doc['GRMProject']['ProjectSettings']['FlowAccumFile'])
        self.AddlayerQGIS(self.doc['GRMProject']['ProjectSettings']['StreamFile'])
        self.AddlayerQGIS(self.doc['GRMProject']['ProjectSettings']['LandCoverFile'])
        self.AddlayerQGIS(self.doc['GRMProject']['ProjectSettings']['SoilDepthFile'])
        self.AddlayerQGIS(self.doc['GRMProject']['ProjectSettings']['SoilTextureFile'])

        # 현재 열은 프로젝트 파일 경로와 GMP 내부 프로젝트 파일 경로 동기화
        self.doc['GRMProject']['ProjectSettings']['ProjectFile'] = _ProjectFile


    # gis에 올리기
    def AddlayerQGIS(self, path):
        if (os.path.isfile(path)) and (self.CheckLayer(path)):
            fileName = path
            fileInfo = QFileInfo(fileName)
            baseName = fileInfo.baseName()
            GRM_Plugin._iface.addRasterLayer(fileName, baseName)

    def NewProjectFile(self):
        global _ProjectFile, _xmltodict


        # New Project 시에 GMP 파일 새로 생성
        filename = QFileDialog.getSaveFileName(self, "select output file ", "", "*.gmp")
        _ProjectFile = filename
        _XmlMake.Make_GMP_File(filename)
        if len(filename)>0:
            self.clear()
        Projectfile = open(filename, 'r')
        data = Projectfile.read()
        Projectfile.close()

        # 여기서 dataset 대신 datatable로 하면 안된다.
        ds = System.Data.DataSet()
        ds.ReadXml(filename)
        ds.WriteXml(filename)
        ds.Dispose()

        self.doc = dict(xmltodict.parse(data))
        _xmltodict = self.doc


    def SaveProjectFile(self):
        #값 변경 테스트 용 WatershedFile 파일 경로를 바꿈
        # self.doc['GRMProject']['ProjectSettings']['WatershedFile'] = "im your brother"

        # 현재 변경된 XML 자료를 파일에 덮어 씌우는 부분
        DictoXml = xmltodict.unparse(self.doc)
        fw = open(_ProjectFile, 'w+')
        fw.write(DictoXml)
        time.sleep(0.5)
        fw.close()






        # ds = System.Data.DataSet()
        # ds.ReadXml(self.filename)


        # 여기서 dataset 대신 datatable로 하면 안된다.
        ds = GRMCore.GRMProject()
        ds.ReadXml(_ProjectFile)
        ds.WriteXml(_ProjectFile)
        ds.Dispose()
        _util.MessageboxShowInfo("GRM Save"," Saving is complete. ")




        #
        #
        # # 줄바꿈과 뛰어쓰기 부분
        # def indent(elem, level=0):
        #     i = "\n" + level * "  "
        #     j = "\n" + (level - 1) * "  "
        #     if len(elem):
        #         if not elem.text or not elem.text.strip():
        #             elem.text = i + "  "
        #         if not elem.tail or not elem.tail.strip():
        #             elem.tail = i
        #         for subelem in elem:
        #             indent(subelem, level + 1)
        #         if not elem.tail or not elem.tail.strip():
        #             elem.tail = i
        #     else:
        #         if level and (not elem.tail or not elem.tail.strip()):
        #             elem.tail = i
        #     return elem
        #
        # # 저장된 파일 다시 불러와서 줄바꿈과 정렬 하기
        # doc = ET.parse(_ProjectFile)
        # root = doc.getroot()
        # ET.register_namespace("", "http://tempuri.org/GRMProject.xsd")
        # indent(root)
        # doc.write(_ProjectFile, encoding="utf-8", xml_declaration=True)



        # _util.MessageboxShowInfo("_ProjectFile",_ProjectFile)
        # _util.MessageboxShowInfo("_ProjectFile", str(ET.tostring(root)))
        #
        # retxml=str(ET.tostring(root))
        #
        # fw = open(_ProjectFile, 'w+')
        # fw.write(retxml.replace("ns0:", ""))
        # fw.close()
        #
        # file = codecs.open("lol", "w", "utf-8")
        # file.write(u'\ufeff')
        # file.close()






    def SaveASProjectFile(self):
       SaveAsPath=self.Select_Ouput_File()
       DictoXml = xmltodict.unparse(self.doc)
       fw = open(SaveAsPath, 'w+')
       fw.write(DictoXml)
       fw.close()

    # Util 에 있는 기능 임시로 여기에 만듬
    def Select_Ouput_File(self):
        filename = QFileDialog.getSaveFileName(self, "select output file ", "", "*.gmp")
        return filename

    # 레이어가 Qgis에 올라와 있는지 확인 (현재 QGIS에 올라온 레이어면 올리지 않음)
    def CheckLayer(self,layerpath):
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.dataProvider().dataSourceUri() == layerpath:
                return False
        return True

