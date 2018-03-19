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
# from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import *
from PyQt4.QtCore import QFileInfo
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView
import os
import Util
from PyQt4 import QtGui, uic
from ElementTree import *
from qgis.core import QgsMapLayerRegistry
import GRM_Plugin

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Call_EXE.ui'))

_util = Util.util()
_argumentFile = ""
_exeFile =""
_projectFile =""
class Call_EXE_arg_Dialog(QtGui.QDialog, FORM_CLASS):
    plot1= None
    def __init__(self, parent=None):
        """Constructor."""
        super(Call_EXE_arg_Dialog, self).__init__(parent)
        self.setupUi(self)
        global _argumentFile,_exeFile ,_projectFile
        # QGIS 레이어 목록 XML
        _argumentFile = os.path.dirname(os.path.abspath(__file__)) + "\LayerList.xml"
        _projectFile= os.path.dirname(os.path.abspath(__file__)) + "\gd.gmp"
        # VB exe 프로그램 경로
        _exeFile = os.path.dirname(os.path.abspath(__file__)) + "\CallSetWatershed.exe"
        self.btnCall.clicked.connect(self.CallVB)


    def CallVB(self):
        # XML 파일 있는지 확인 하여 없으면 생성 있으면 지우고 새로 생성
        if os.path.isfile(_argumentFile)==True:
            self.MakeXML(_argumentFile)
        else:
            os.remove(_argumentFile)
            self.MakeXML(_argumentFile)

        # arg =  _exeFile  + " -sf "  + "'" +  argumentFile
        arg = '"' + _exeFile + '"' + ' -sf ' + '"' + _argumentFile + '"'  + ' "' + _projectFile + '"'
        _util.MessageboxShowInfo("arg" , str(arg))




        value=_util.Execute(arg)
        _util.MessageboxShowError("GRM",str(value))

    # 레이어 목록 전달할 XML 생성
    # 아래 XML 형식으로 변경
    def MakeXML(self,filpath):
        # root = Element("GRM")
        # layers = GRM_Plugin._iface.legendInterface().layers()
        # for layer in layers:
        #     layerpath=_util.GetLayerPath(layer.name())
        #     SubElement(root, "data", LayerName=layer.name()).text = layerpath
        # ElementTree(root).write(filpath, "utf-8")

        # 2017/06/19 XML 생성 부분 수정
        Employees = Element("Employees")
        layers = GRM_Plugin._iface.legendInterface().layers()
        for layer in layers:
            layerpath=_util.GetLayerPath(layer.name())
            Employee = Element('Employee', LayerName=layer.name())
            LayerPath = Element('LayerPath')
            LayerPath.text = layerpath
            Employee.append(LayerPath)
            Employees.append(Employee)
        ElementTree(Employees).write(filpath, "utf-8")

    '''
    <Employees>
      <Employee LayerName="logan">
        <LayerPath>G:/프로젝트별 샘플자료/KGIS실행시 샘플자료/sampleData_20150826/3_sampleData/GridClip_Test/logan.tif</LayerPath>
      </Employee>
      <Employee LayerName="logan2">
        <LayerPath>G:/프로젝트별 샘플자료/KGIS실행시 샘플자료/sampleData_20150826/3_sampleData/GridClip_Test/logan2.tif</LayerPath>
      </Employee>
    </Employees>
    '''

















