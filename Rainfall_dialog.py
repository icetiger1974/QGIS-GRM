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
import os
import sys
import Util
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtGui, uic
import GRM_Plugin_dockwidget as GRM
from PyQt4.QtGui import QFileDialog
# # import math
# sys.path.append("C:/Program Files/QGIS 2.18/apps/Python27/Lib/site-packages/pygments/lexers")
# import math.py


sys.path.insert(0, 'C:/Program Files/QGIS 2.18/apps/Python27\lib\site-packages/future/backports')
import datetime
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'Rainfall.ui'))
_util = Util.util()

class RainFallDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(RainFallDialog, self).__init__(parent)
        self.setupUi(self)
        # 프로젝트 파일 내용을 받아 옴
        self.ProjectSetting()
        # 프로젝트 파일 내용을 받아서 폼에 셋팅
        self.SettingForm()

        # 버튼 이벤트 셋팅
        self.SetbtnEvent()
        if self.RainfallDataType == "TextFileASCgrid" or self.RainfallDataType is None :
            filelsit = self.search(self.txtFolderPath.text())
            self.ReSettingListWidgetASC(filelsit)
        elif self.RainfallDataType == "TextFileMAP" :
            filelsit = self.search(self.txtFolderPath.text())
            self.SettingListWidget(filelsit)

    # 프로젝트 파일 내용을 받아 옴
    def ProjectSetting(self):
        self.projectPath = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
        self.RainfallDataType = GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallDataType']
        self.RainfallInterval = GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallInterval']
        self.RainfallDataFile = GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallDataFile']

    # 프로젝트 파일 내용을 받아서 초기 폼 셋팅
    def SettingForm(self):
        # 사용자가 time step 값을 변경시 테이블에 적용
        self.spbtimestep.valueChanged.connect(self.RefreshTable)

        # 폴더 경로 처리
        self.txtFolderPath.textChanged.connect(self.Chage_textFolderpath)


         # 시간 인터벌 없으면 기본 10분
        if self.RainfallInterval is not None:
            self.spbtimestep.setValue(int(self.RainfallInterval))
            # self.txtRainfallTimeStep.setText(self.RainfallInterval)
        else:
            self.spbtimestep.setValue(10)
            # self.txtRainfallTimeStep.setText("10")


        #Open Project 시행시 처리
        if self.RainfallDataFile is not None:
            #텍스트 박스에 폴더 경로 설정 (util 에서 맞는 폴더 경로 인지 확인)
            if _util.CheckFolder(os.path.dirname(self.RainfallDataFile)):
                self.txtFolderPath.setText(os.path.dirname(self.RainfallDataFile))
                self.txtSaveFileName.setText(self.RainfallDataFile)
                self.SettingTable(self.RainfallDataFile)
        #New project 시행시 처리 
        else:
            #처음 시행 했을때 파일 경로 없기 때문에 "" 로 처리 
            self.txtFolderPath.setText(os.path.dirname(""))
            self.ReomveAll()

        #라디오 버튼 초기 설정
        if self.RainfallDataType == "TextFileASCgrid" or self.RainfallDataType is None :
            self.UseASCgirdLayer()
        elif self.RainfallDataType == "TextFileMAP" :
            self.rdoUseTextFile()

        #ASC 파일 목록을 저장시에 Default 파일 이름을 텍스트 박스에 넣어둠
        if self.RainfallDataFile is not None  and _util.CheckFile(self.RainfallDataFile):
            self.txtSaveFileName.setText(self.RainfallDataFile)
        else:
            filename = _util.GetFilename(self.projectPath)
            dirname = os.path.dirname(self.projectPath)
            self.txtSaveFileName.setText( dirname + "\\"+filename + "_RF.txt")


    def Chage_textFolderpath(self):
        FolderPath =self.txtFolderPath.text()
        try:
            if _util.CheckFolder(FolderPath.rstrip()):
                self.txtFolderPath.setText(FolderPath.rstrip())
                if self.rbUseASCgirdLayer.isChecked():
                    self.rbUseASCgirdLayer_click()
                if self.rbUseTextFileMRF.isChecked():
                    self.rbUseTextFileMRF_click()
        except Exception as es1:
            pass
    def SetbtnEvent(self):
        self.btOpenRfFolder.clicked.connect(self.SelectFolder)
        # self.btApplyNewFloder.clicked.connect(self.ApplyFolderFile)
        self.btAddSelectedFile.clicked.connect(self.AddSelectedFile)
        self.btReomveAll.clicked.connect(self.ReomveAll)


        #라디오 버튼 클릭 이벤트
        self.rbUseASCgirdLayer.clicked.connect(self.rbUseASCgirdLayer_click)
        self.rbUseTextFileMRF.clicked.connect(self.rbUseTextFileMRF_click)

        #Ok  and cancel 버튼 이벤트
        self.btnOK.clicked.connect(self.OKclieck)
        self.btnCancel.clicked.connect(self.Close_Form)

        #리스트 박스 이벤트 처리
        self.lstRFfiles.itemClicked.connect(self.SetSelectFilePath)

        self.btnSaveFile.clicked.connect(self.SeaveFilepath)


    def SeaveFilepath(self):
        if self.txtFolderPath.text() !="":
            dir = self.txtFolderPath.text()
            filename = QFileDialog.getSaveFileName(self, "select output file ", dir, "*.txt")
        else:
            filename = QFileDialog.getSaveFileName(self, "select output file ", "", "*.txt")
        self.txtSaveFileName.setText(filename)


    def SetSelectFilePath(self):
        if self.rbUseTextFileMRF.isChecked():
            self.txtSaveFileName.setText(self.txtFolderPath.text()+ "\\" + self.lstRFfiles.currentItem().text())

    #첫번째 라디오 버튼 선택 이벤트
    def rbUseASCgirdLayer_click(self):
        self.ReomveAll()
        self.UseASCgirdLayer()
        if self.txtFolderPath.text()!="" :
            filelsit = self.search(self.txtFolderPath.text())
            self.ReSettingListWidgetASC(filelsit)
            self.SetTableData_To_Text()
        self.txtSaveFileName.setText("")

    # spin box 값이 변경 될때 Table에 변경된 값 적용
    def RefreshTable(self):
        if self.dgvRainfallList.rowCount()>0:
            for i in range(self.dgvRainfallList.rowCount()):
                self.dgvRainfallList.setItem(i, 1, QTableWidgetItem(str(int(self.spbtimestep.value()) * i)))

    def rbUseTextFileMRF_click(self):
        self.ReomveAll()
        self.rdoUseTextFile()

        if self.txtFolderPath.text()!="" :
            filelsit = self.search(self.txtFolderPath.text())
            self.SettingListWidget(filelsit)
            self.SettingTable(self.RainfallDataFile)
        self.txtSaveFileName.setText("")
        self.label_4.setText("     File name : ")


    #첫번째 라디오 버튼 선택 이벤트 하위
    def UseASCgirdLayer(self):
        self.rbUseASCgirdLayer.setChecked(True)
        # self.btApplyNewFloder.setEnabled(True)
        self.btAddSelectedFile.setEnabled(True)
        # self.btAddSelectedFile.setText('Add files')
        self.btAddSelectedFile.setText('Add selected or all files')
        self.txtSaveFileName.setEnabled(True)
        self.btnSaveFile.setEnabled(True)
        # 다중 파일 선택 가능
        self.lstRFfiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.label_4.setText("Save file name : ")

    #두번째 라디오 버튼 선택 이벤트
    def rdoUseTextFile(self):
        self.rbUseTextFileMRF.setChecked(True)
        # self.btApplyNewFloder.setEnabled(False)
        self.btAddSelectedFile.setEnabled(True)
        self.btAddSelectedFile.setText('View rainfall data')
        self.txtSaveFileName.setEnabled(False)
        self.btnSaveFile.setEnabled(False)
        # 단일 파일만 선택
        self.lstRFfiles.setSelectionMode(QAbstractItemView.SingleSelection)

    # 테이블에 데이터 셋팅
    def SettingTable(self,Datafile):

        if Datafile !="" and Datafile is not None:
            if _util.CheckFile(Datafile):
                self.dgvRainfallList.clear()
                file_open = open(Datafile).readlines()
                datalist = []

                for line in file_open[0:]:
                    splitsdata = line.strip().split()
                    datalist.append(splitsdata)

                if len(datalist) >= 0:

                    stylesheet = "::section{Background-color : rgb(255,255,255)}"
                    self.dgvRainfallList.horizontalHeader().setStyleSheet(stylesheet)
                    self.dgvRainfallList.setColumnCount(3)

                    self.dgvRainfallList.setHorizontalHeaderLabels(['Order', 'DataTime', 'Rainfall'])
                    self.dgvRainfallList.setRowCount(len(datalist))

                    self.ListCount = len(datalist)
                    for i in range(len(datalist)):
                        self.dgvRainfallList.setItem(i, 0, QTableWidgetItem(str(i+1)))
                        self.dgvRainfallList.setItem(i, 1, QTableWidgetItem(str(int(self.spbtimestep.value())*i)))
                        self.dgvRainfallList.setItem(i, 2, QTableWidgetItem(datalist[i][0]))
                else :

                    stylesheet = "::section{Background-color : rgb(255,255,255)}"
                    self.dgvRainfallList.horizontalHeader().setStyleSheet(stylesheet)
                    self.dgvRainfallList.setColumnCount(3)
                    self.dgvRainfallList.setHorizontalHeaderLabels(['Order', 'DataTime', 'Rainfall'])

        else:

            stylesheet = "::section{Background-color : rgb(255,255,255)}"
            self.dgvRainfallList.horizontalHeader().setStyleSheet(stylesheet)
            self.dgvRainfallList.setColumnCount(3)
            self.dgvRainfallList.setHorizontalHeaderLabels(['Order', 'DataTime', 'Rainfall'])


    # 폴더 선택 버튼 이벤트
    def SelectFolder(self):
        if self.RainfallDataFile is not None:
            folderpath  =QtGui.QFileDialog.getExistingDirectory(None, 'Select a folder:', os.path.dirname(self.RainfallDataFile), QtGui.QFileDialog.ShowDirsOnly)
        else:
            folderpath  =QtGui.QFileDialog.getExistingDirectory(None, 'Select a folder:', os.path.dirname(GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']), QtGui.QFileDialog.ShowDirsOnly)
        
        if folderpath!="":
            self.txtFolderPath.setText(folderpath)

            filelsit = self.search(folderpath)
            if self.rbUseASCgirdLayer.isChecked():
                self.ReSettingListWidgetASC(filelsit)
            else:
                self.SettingListWidget(filelsit)

    def search(self,dirname):
        filenames = os.listdir(dirname)
        fileList=[]
        for filename in filenames:
            fileList.append(filename)
        return fileList


    def SettingListWidget(self,filelsit):
        self.lstRFfiles.clear()
        for file in filelsit:
            filename = os.path.splitext(file)[1]
            if ".TXT"in filename.upper() or ".MRF"in filename.upper()  :
                self.lstRFfiles.addItem(file)

    def ReSettingListWidgetASC(self,filelsit):
        self.lstRFfiles.clear()
        for file in filelsit:
            filename = os.path.splitext(file)[1]
            if ".ASC"in filename.upper() :
                self.lstRFfiles.addItem(file)

    def AddSelectedFile(self):
        if self.rbUseTextFileMRF.isChecked():
            if self.lstRFfiles.currentItem().text() !="" :
                selectPath = self.txtFolderPath.text() + "\\" +self.lstRFfiles.currentItem().text()
                self.SettingTable(selectPath)
            else :
                self.SettingTable("")
        elif self.rbUseASCgirdLayer.isChecked():
            self.SettingTableASC()

    def ReomveAll(self):
        self.dgvRainfallList.clear()
        stylesheet = "::section{Background-color : rgb(255,255,255)}"
        self.dgvRainfallList.horizontalHeader().setStyleSheet(stylesheet)
        self.dgvRainfallList.setColumnCount(3)
        self.dgvRainfallList.setRowCount(0)
        if self.rbUseTextFileMRF.isChecked():
            self.dgvRainfallList.setHorizontalHeaderLabels(['Order', 'DataTime', 'Rainfall'])
        else:
            self.dgvRainfallList.setHorizontalHeaderLabels(['Order', 'DataTime', 'Rainfall file'])

    def OKclieck(self):
        try:
            if self.txtFolderPath.text() == "":
                self.txtFolderPath.setFocus()
                raise Exception("\n Folder path is required for data generation. \n")

            if self.spbtimestep.value() == 0:
                self.spbtimestep.setFocus()
                raise Exception("\n Rainfall time step must be valid. \n")

            if self.txtSaveFileName.text() == "":
                self.txtSaveFileName.setFocus()
                raise Exception("\n Rainfall Save file path is not entered.  \n")

            if self.rbUseASCgirdLayer.isChecked():
                if self.lstRFfiles.count()==0 or self.dgvRainfallList.columnCount()==0 :
                    raise Exception("\n Rainfall data is not entered. \n")
            if self.rbUseTextFileMRF.isChecked():
                if self.lstRFfiles.count() == 0 :
                    raise Exception("\n Rainfall data is not entered.  \n")

            self.UpdateMenuStatus()
        except Exception as exce:
            _util.MessageboxShowError("RainFall", exce.args[0])
        else:
            _util.MessageboxShowInfo("RainFall", "Rainfall setup is completed.   ")
            # 저장이 완료 되면 다시 로드
            self.ProjectSetting()
            self.close()

    def UpdateMenuStatus(self):
        GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallDataFile'] = self.txtSaveFileName.text()
        GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallInterval'] = str(self.spbtimestep.value())

        OutputTimeStep=GRM._xmltodict['GRMProject']['ProjectSettings']['OutputTimeStep']
        if self.spbtimestep.value()!=0:
            GRM._xmltodict['GRMProject']['ProjectSettings']['OutputTimeStep'] =str(self.spbtimestep.value())

        SimulationDuration = GRM._xmltodict['GRMProject']['ProjectSettings']['SimulationDuration']
        if self.dgvRainfallList.rowCount()>0 and self.spbtimestep.value()!=0:
            Rcount = self.dgvRainfallList.rowCount()
            timestep = int((self.spbtimestep.value()))
            cal_result = float((Rcount * timestep)/60)
            GRM._xmltodict['GRMProject']['ProjectSettings']['SimulationDuration'] = str(int(cal_result)+1)


        if self.rbUseTextFileMRF.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallDataType'] = 'TextFileMAP'
        elif self.rbUseASCgirdLayer.isChecked():
            GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallDataType'] = 'TextFileASCgrid'
            self.SettingTableASC()
            self.SaveTableData_to_Text()



    # apply 버튼 눌렀을때 파일 리스트를 테이블에 보여줌
    def ApplyFolderFile(self):
        # 폴더 파일 리스트 받기
        # self.lstRFfiles
        items = []
        for index in xrange(self.lstRFfiles.count()):
            items.append(self.lstRFfiles.item(index).text())
       
        # 아이템 정렬
        if len(items)!=0:
            items.sort()
            self.dgvRainfallList.setColumnCount(3)
            self.dgvRainfallList.setRowCount(len(items))
            self.dgvRainfallList.setHorizontalHeaderLabels(['Order', 'DataTime', 'Rainfall'])
            for i in range(len(items)):
                Datafile = self.txtFolderPath.text() + "\\" + items[i]
                self.dgvRainfallList.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                # self.dgvRainfallList.setItem(i, 1, QTableWidgetItem(str(int(self.txtRainfallTimeStep.text()) * i)))
                self.dgvRainfallList.setItem(i, 1, QTableWidgetItem(str(int(self.spbtimestep.value()) * i)))
                self.dgvRainfallList.setItem(i, 2, QTableWidgetItem(items[i]))

    # view file data 버튼을 눌렀을때 선택된 파일이 없으면 현재 파일리스트에 표시된 모두를 tablewiget에 표출
    def SettingTableASC(self):
        itemsList = self.lstRFfiles.selectedItems()
        if len(itemsList)!=0:
            itemsList.sort()
            self.dgvRainfallList.setColumnCount(3)
            self.dgvRainfallList.setRowCount(len(itemsList))
            self.dgvRainfallList.setHorizontalHeaderLabels(['Order', 'DataTime', 'Rainfall'])

            for i in range(len(itemsList)):
                Datafile = self.txtFolderPath.text() + "/" + itemsList[i].text()
                self.dgvRainfallList.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                # self.dgvRainfallList.setItem(i, 1, QTableWidgetItem(str(int(self.txtRainfallTimeStep.text()) * i)))
                self.dgvRainfallList.setItem(i, 1, QTableWidgetItem(str(int(self.spbtimestep.value()) * i)))
                self.dgvRainfallList.setItem(i, 2, QTableWidgetItem(Datafile))
                #self.dgvRainfallList.setItem(i, 2, QTableWidgetItem(itemsList[i].text()))
        elif len(itemsList)==0 and self.lstRFfiles.count()>0 :
            self.dgvRainfallList.setColumnCount(3)
            self.dgvRainfallList.setRowCount(self.lstRFfiles.count())
            self.dgvRainfallList.setHorizontalHeaderLabels(['Order', 'DataTime', 'Rainfall'])
            for i in range(self.lstRFfiles.count()):
                self.dgvRainfallList.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                # self.dgvRainfallList.setItem(i, 1, QTableWidgetItem(str(int(self.txtRainfallTimeStep.text()) * i)))
                self.dgvRainfallList.setItem(i, 1, QTableWidgetItem(str(int(self.spbtimestep.value()) * i)))
                self.dgvRainfallList.setItem(i, 2, QTableWidgetItem(str(self.txtFolderPath.text() + "/"+ self.lstRFfiles.item(i).text())))

    # 폼 종료
    def Close_Form(self):
        self.close()

    # 텍스트 파일로 테이블 내용 저장
    def SaveTableData_to_Text(self):
        SaveTxtPath = self.txtSaveFileName.text()

        Rcount = self.dgvRainfallList.rowCount()
        GRM._RainFallCount = Rcount
        if os.path.exists(SaveTxtPath):
            fh = open(SaveTxtPath, "r+")
            for i in range(Rcount):
                value=self.dgvRainfallList.item(i, 2).text()
                #value=self.txtFolderPath.text() + "\\" + self.dgvRainfallList.item(i, 2).text()
                fh.write(value.replace("\\","/") + "\n")
            fh.truncate()
        else:
            fh = open(SaveTxtPath, "w")
            for i in range(Rcount):
                value =self.dgvRainfallList.item(i, 2).text()
                #value = self.txtFolderPath.text() + "\\" + self.dgvRainfallList.item(i, 2).text()
                fh.write(value.replace("\\", "/") + "\n")
            fh.close()

    # 라디오 버튼 클릭시에 기존에 셋팅한 내용을 테이블에 채워 넣음
    def SetTableData_To_Text(self):
        SaveTxtPath = self.RainfallDataFile
        if _util.CheckFile(SaveTxtPath):
            self.SettingTable(SaveTxtPath)



