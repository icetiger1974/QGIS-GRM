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
from PyQt4.QtCore import *
import ElementTree as ET
import Util
from subprocess import Popen

reload(sys)
sys.setdefaultencoding('utf8')


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'View_Chart.ui'))

_util  = Util.util()
_disCharge =""
_mdb=""


#-----2017/10/12 CHO 메모장에서 열기 위해서 메모장 위치 하드코딩함
_notpad = "C:/Windows/System32/notepad.exe"
#하드코딩 경로고, 다른 곳에서도 사용 되서..
_disCharge = "C:\GRM\Sample\SampleProjectDischarge.out"
#-----2017/10/12 CHO 추가 Depth 파일은 임시
_Depth="C:\GRM\Sample\GRMTestProjectDepth.out"

class View_ChartDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(View_ChartDialog, self).__init__(parent)
        self.setupUi(self)

        # # 프로젝트 파일을 읽고 테이블에 셋팅
        self.SettingsTable()

        # 테이블 셀값을 변경 불가능 하게 설정
        self.tbldischarge.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tbldepth.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        
        
        # 사용 파일 오픈 (discharge.out)
        self.btnViwfileQ.clicked.connect(lambda :self.OpenViweFile(_disCharge))
        # 사용 파일 오픈 (depth.out)
        self.btnViwfileT.clicked.connect(lambda :self.OpenViweFile(_Depth))

        # 폼 종료
        self.btnClose.clicked.connect(self.Close_Form)

        self.setFixedSize(self.size())


    def SettingsTable(self):
        global _disCharge,_Depth
#         _disCharge = "C:\GRM\Sample\SampleProjectDischarge.out"
#         _Depth="C:\GRM\Sample\GRMTestProjectDepth.out"
        #테이블 스타일 - 헤더 부분, 색, font-style
        stylesheet = "::section{Background-color : rgb(255,255,255); font: bold}"
        file_open = open(_disCharge).readlines()
        # Table에 데이터 값 대입
        datalist = []
        for line in file_open[4:]:
            splitsdata = line.strip().split()
            if len(splitsdata) == 4:
                datalist.append(splitsdata)
        # mw4 에는 ThisStep_sec 항목이 있는 파일을 사용 하고 있는데 우리 측에서 사용 하는 파일에는 항목이 없음
        
        
        self.tbldischarge.horizontalHeader().setStyleSheet(stylesheet)
        self.tbldischarge.setColumnCount(6)
        self.tbldischarge.setRowCount(len(datalist))
        self.tbldischarge.setHorizontalHeaderLabels(
            ['DataNo', 'DataTime', 'MD', 'Rainfall_Mean', 'ThisStep_sec', 'FromStarting_sec'])
        self.tbldischarge.resizeColumnsToContents()
        self.tbldischarge.resizeRowsToContents()

        for i in range(len(datalist)):
            self.tbldischarge.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.tbldischarge.setItem(i, 1, QTableWidgetItem(datalist[i][0]))
            self.tbldischarge.setItem(i, 2, QTableWidgetItem(datalist[i][1]))
            self.tbldischarge.setItem(i, 3, QTableWidgetItem(datalist[i][2]))
            self.tbldischarge.setItem(i, 4, QTableWidgetItem(str("")))
            self.tbldischarge.setItem(i, 5, QTableWidgetItem(datalist[i][3]))
        
        #-----2017/10/12 CHO 테이블 열기
        #Depth 데이터
        depth_open = open(_Depth).readlines()
        depth_data = []
        for line in depth_open[4:]:
            splitsdata = line.strip().split()
            if 4<=len(splitsdata):#-----2017/10/12 CHO 임시 데이터는 4개 이상이라서 코드를 다음과 같이 함
                depth_data.append(splitsdata)
        
        self.tbldepth.horizontalHeader().setStyleSheet(stylesheet)
        self.tbldepth.setColumnCount(6)
        self.tbldepth.setRowCount(len(depth_data))
        self.tbldepth.setHorizontalHeaderLabels(
                ['DataNo', 'DataTime', 'MD', 'Rainfall_Mean', 'ThisStep_sec', 'FromStarting_sec'])
        self.tbldepth.resizeColumnsToContents()
        self.tbldepth.resizeRowsToContents()

        for j in range(len(depth_data)):
            self.tbldepth.setItem(j, 0, QTableWidgetItem(str(j+1)))
            self.tbldepth.setItem(j, 1, QTableWidgetItem(depth_data[j][0]))
            self.tbldepth.setItem(j, 2, QTableWidgetItem(depth_data[j][1]))
            self.tbldepth.setItem(j, 3, QTableWidgetItem(depth_data[j][2]))
            self.tbldepth.setItem(j, 4, QTableWidgetItem(str("")))
            self.tbldepth.setItem(j, 5, QTableWidgetItem(depth_data[j][3]))
        
        #-----2017/10/12 CHO 데이터가 없어서 하드코딩함.
        #Observed data
        self.tblobserveddata.horizontalHeader().setStyleSheet(stylesheet)
        self.tblobserveddata.setColumnCount(2)
        self.tblobserveddata.setRowCount(1)
        self.tblobserveddata.setHorizontalHeaderLabels(
                ['DataNo', 'DataTime'])
        self.tblobserveddata.resizeRowsToContents()



        # 리스트 파일 열기
        # with open(_disCharge) as fp:
        #     # 파일을 열고 바로 데이터 값을 Table에 넣을수가 없음 이유는 모르겠으나
        #     # 테이블에 데이터 넣으면 공백으로 표시됨- 버그인지 확인 안되나 ㅜㅜ 고생좀 했음
        #     lines = fp.read().split("\n")
        #
        # _util.MessageboxShowError("line",str(len(lines)))
        # # mw4 에는 ThisStep_sec 항목이 있는 파일을 사용 하고 있는데 우리 측에서 사용 하는 파일에는 항목이 없음
        # self.tbldischarge.setColumnCount(6)
        # self.tbldischarge.setRowCount(len(lines)-4)
        # self.tbldischarge.setHorizontalHeaderLabels(['DataNo', 'DataTime', 'MD', 'Rainfall_Mean', 'ThisStep_sec', 'FromStarting_sec'])
        # self.tbldischarge.resizeColumnsToContents()
        # self.tbldischarge.resizeRowsToContents()
        #
        #
        # # Table에 데이터 값 대입
        # for i in range(4, len(lines)):
        #     splitsdata = lines[i].split()
        #     self.tbldischarge.setItem(i-4, 0, QTableWidgetItem(str(i-3)))
        #     self.tbldischarge.setItem(i-4, 1, QTableWidgetItem(splitsdata[0]))
        #     self.tbldischarge.setItem(i-4, 2, QTableWidgetItem(splitsdata[1]))
        #     self.tbldischarge.setItem(i-4, 3, QTableWidgetItem(splitsdata[2]))
        #     self.tbldischarge.setItem(i-4, 4, QTableWidgetItem(str("")))
        #     self.tbldischarge.setItem(i-4, 5, QTableWidgetItem(splitsdata[3]))
    
    #-----2017/10/12 CHO *.out 열기
    def OpenViweFile(self,path):
        Popen([_notpad,path])
    
    # mdb할 프로젝트 파일을 선택 한다.(최박사님과 협의 없이 임시로 개발)
    def Select_Project_File(self):
        filename = QFileDialog.getOpenFileName(self, "select output file ", "*.mdb")
        self.txtMdb.setText(filename)

    # 폼 종료
    def Close_Form(self):
        self.SaveRoject()
        self.close()
