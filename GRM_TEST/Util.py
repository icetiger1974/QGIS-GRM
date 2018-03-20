# -*- coding: utf-8 -*-


# from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo

# from PyQt4.QtGui import QAction, QIcon, QFileDialog, QLineEdit, QMessageBox , QComboBox,QLabel,QLineEdit
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import QgsMapLayerRegistry
from subprocess import call
import sys
import os
import os.path
import win32api
import re
import tempfile
from subprocess import Popen
import GRM_Plugin_dockwidget as GRM
import ElementTree as ET



reload(sys)
sys.setdefaultencoding('utf-8')


class util:
    def __init__(self):
        self.Input_Layer_Path = ""
        self.FillSink_Layer_Path = ""
        self.FD_Layer_Path = ""
        self.FA_Layer_Path = ""
        self.Stream_Layer_Path = ""
        self.tauDemPath = ""
        self.tauDEMCommand = self.enum('SK', 'FD', 'FA', 'SG', 'ST', 'STV', 'CAT')
        self.StaticDB = os.path.dirname(os.path.realpath(__file__)) + "\DLL\GRMStaticDB.xml"

    def enum(*sequential, **named):
        enums = dict(zip(sequential, range(len(sequential))), **named)
        reverse = dict((value, key) for key, value in enums.iteritems())
        enums['reverse_mapping'] = reverse
        return type('Enum', (), enums)

    # Taudem path 받아 오기
    def GetTaudemPath(self):
        tauPath = "C:\\Program Files\\TauDEM\\TauDEM5Exe\\"
        return tauPath

    def Execute(self, arg):
        value = call(arg)
        return value

    def FlowControlGrid_XmlCount(self):
        FlowNameCount = []
        ProjectFile = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']
        doc = ET.parse(ProjectFile)
        root = doc.getroot()
        for element in root.findall('{http://tempuri.org/GRMProject.xsd}FlowControlGrid'):
            FlowNameCount.append(element.findtext("{http://tempuri.org/GRMProject.xsd}Name"))
        return len(FlowNameCount)

    def RainfallCount(self):
        RainfallDataType=GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallDataType']
        RainfallDataFile=GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallDataFile']
        RainfallInterval=GRM._xmltodict['GRMProject']['ProjectSettings']['RainfallInterval']
        if RainfallDataType !="":
            with open(RainfallDataFile, "r") as ins:
                array = []
                for line in ins:
                    array.append(line)
                if int(RainfallInterval)>0:
                    return (len(array) * int(RainfallInterval))
                else:
                    return 0
        else:
            return 0





    # 각각의 기능별로 arg를 생성하고 반환 하는 기능
    def GetTaudemArg(self, inputfile, ouputfile, taudemcommand, facoption, optionvalue):
        option = optionvalue
        tauPath = self.GetTaudemPath()
        input = inputfile.replace('\\', '\\\\')
        output = ouputfile.replace('\\', '\\\\')
        output_Temp = self.GetTempFilePath(ouputfile)
        arg = ""
        if taudemcommand == self.tauDEMCommand.SK:
            tauPath = tauPath + "PitRemove.exe"
            arg = '"' + tauPath + '"' + ' -z ' + '"' + input + '"' + ' -fel ' + '"' + output + '"'
        elif taudemcommand == self.tauDEMCommand.FD:
            tauPath = tauPath + "D8FlowDir.exe"
            arg = '"' + tauPath + '"' + ' -fel ' + '"' + input + '"' + ' -p ' + '"' + output + '"' + ' -sd8 ' + '"' + output_Temp + '"'
        elif taudemcommand == self.tauDEMCommand.FA:
            tauPath = tauPath + "AreaD8.exe"
            if str(facoption) == "True":
                arg = '"' + tauPath + '"' + ' -p ' + '"' + input + '"' + ' -ad8 ' + '"' + output + '"'
            else:
                arg = '"' + tauPath + '"' + ' -p ' + '"' + input + '"' + ' -ad8 ' + '"' + output + '"' + ' -nc '
        elif taudemcommand == self.tauDEMCommand.SG:
            tauPath = tauPath + "D8FlowDir.exe"
            arg = '"' + tauPath + '"' + ' -fel ' + '"' + input + '"' + ' -p ' + '"' + output_Temp + '"' + ' -sd8 ' + '"' + output + '"'
        elif taudemcommand == self.tauDEMCommand.ST:
            tauPath = tauPath + "Threshold.exe"
            arg ='"' + tauPath + '"' + ' -ssa '  + '"' + input + '"' + ' -src ' + '"' + output + '"' + ' -thresh ' +  option
        return arg

    def GetCacthmentsArg(self, input_layer, fd_layer, fa_layer, stream_Layer, txtoutput):
        output1 = self.GetTempFilePath(input_layer)
        output2 = output1.replace('tif', 'dat')
        output3 = output1.replace('tif', 'dat')
        output4 = output1.replace('tif', 'shp')
        output5 = txtoutput
        input0 = input_layer
        input1 = fd_layer
        input2 = fa_layer
        input3 = stream_Layer
        tauPath = self.GetTaudemPath()
        tauPath = tauPath + "StreamNet.exe"
        arg = '"' + tauPath + '"' + ' -fel ' + '"' + input0 + '"' + ' -p ' + '"' + input1 + '"' + ' -ad8 ' + '"' + input2 + '"' + ' -src ' + '"' + input3 + '"' + ' -ord ' + '"' + output1 + '"' + ' -tree ' + '"' + output2 + '"' + ' -coord  ' + '"' + output3 + '"' + ' -net ' + '"' + output4 + '"' + ' -w ' + '"' + output5 + '"'
        return arg



    #Watershed 처리
    def GetWatershedArg(self,fill_layer,fd_layer,fa_layer,txtstream_cellvalue,shp_layer,txtoutput,flag):
        # shape 파일의 경로를 받아 오면 경로상에 layerid가 붙어서 넘오옴 그래서 문자열 잘라서 사용
        shpPath= shp_layer.split('|')[0]

        #임시 파일 경로 생성 함수 tempfile.mktemp()
        #tempfile.mktemp() 파이썬 기본 모듈로 파일을 같은 경로로 옮기고 사용
        temOutput = tempfile.mktemp() + ".tif"
        temOutput2 = tempfile.mktemp() + ".tif"
        temOutput3 = tempfile.mktemp() + ".tif"
        streamOutput = tempfile.mktemp() + ".tif"

        temptif =tempfile.mktemp() + ".tif"
        tempdat = tempfile.mktemp() + ".dat"
        tempdat2 = tempfile.mktemp() + ".dat"
        tempShape = os.path.dirname(shpPath)  + "\\"+ os.path.basename(shpPath).replace('.shp', '_net.shp')

        tauPathAread8 = self.GetTaudemPath() + "Aread8.exe"
        tauPathPeukerDouglas  = self.GetTaudemPath() + "PeukerDouglas.exe"
        tauPthThreshold = self.GetTaudemPath() + "Threshold.exe"
        tauPathStreamnet = self.GetTaudemPath() + "Streamnet.exe"

        returns='1'
        arg = '"' + tauPathAread8 + '"' + ' -p ' + '"' + fd_layer + '"' + ' -ad8 ' + '"' +  temOutput + '"' + ' -o ' + '"' +  shpPath + '"'
        re=self.Execute(arg)
        if str(re)=='0':
            arg = '"' + tauPathPeukerDouglas + '"' + ' -fel ' +  '"' + fill_layer + '"' + ' -ss ' + '"' + temOutput2 + '"'
            re1 = self.Execute(arg)
            if str(re1) == '0':
                arg = '"' + tauPathAread8 + '"' + ' -p ' + '"' + fd_layer + '"' + ' -ad8 ' + '"' + temOutput3 + '"' + ' -o ' + '"' +  shpPath + '"' + ' -wg '  + '"' + temOutput2 + '"'
                re2 = self.Execute(arg)
                if str(re2) == '0':
                    arg = '"' + tauPthThreshold + '"' + ' -ssa ' + '"' + temOutput3 + '"' + ' -src ' + '"' + streamOutput + '"' + ' -thresh ' + txtstream_cellvalue
                    re3 = self.Execute(arg)
                    if str(re3)=='0':
                        arg = '"' + tauPathStreamnet + '"' + ' -fel ' +  '"' + fill_layer + '"' + ' -p ' + '"' + fd_layer + '"' \
                              + ' -ad8 ' + '"' + fa_layer + '"' + ' -src ' +  '"' + streamOutput +  '"' + ' -ord ' +  '"' + temptif + '"' + ' -tree '\
                              + '"' + tempdat + '"' + ' -coord ' + '"' + tempdat2 + '"' + ' -net ' + '"' +  tempShape + '"' + ' -w ' + '"' +  txtoutput + '"' + ' -o ' + '"' +  shpPath + '"'
                        if str(flag)=='True' :
                            arg = arg + ' -sw'
                        re4 = self.Execute(arg)
                        if str(re4)=='0':
                            returns='0'
        return returns

    # 윈도우 임시 폴더에 임시 파일 생성
    def GetTempFilePath(self, tempfilepath):
        output_temp = win32api.GetTempPath() + os.path.basename(tempfilepath)
        output_temp = output_temp.replace('\\', '\\\\')
        return output_temp

    # 콤보박스 리스트 셋팅 type은( tif, shp , "" 일땐 모두다)
    def SetCommbox(self, layers, commbox, type):
        layer_list = []
        if type.upper() == "TIF" or  type.upper() == "ASC" :
            for layer in layers:
                layertype = layer.type()
                if layertype == layer.RasterLayer:
                    layer_list.append(layer.name())
        elif type.upper() == "SHP":
            for layer in layers:
                layertype = layer.type()
                if layertype == layer.VectorLayer:
                    layer_list.append(layer.name())
        else:
            for layer in layers:
                layer_list.append(layer.name())
        commbox.clear()
        combolist = ['select layer']
        combolist.extend(layer_list)
        commbox.addItems(combolist)

    # 메시지 박스 출력
    def MessageboxShowInfo(self, title, message):
        QMessageBox.information(None, title, message)

    def MessageboxShowError(self, title, message):
        QMessageBox.warning(None, title, message)

    # 콤보 박스에서 선택된 레이어 경로 받아 오기
    def GetcomboSelectedLayerPath(self, commbox):
        layername = commbox.currentText()
        if layername == 'select layer':
            return ""
        else:
            layer = None
            for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                if lyr.name() == layername:
                    layer = lyr
            return layer.dataProvider().dataSourceUri()


     # 레이어 명으로 경로 받아 오기
    def GetTxtToLayerPath(self, layernametxt):
        layername = layernametxt
        layer = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == layername:
                layer = lyr
        if layer != None :
            return layer.dataProvider().dataSourceUri()
        else :
            return "Null"

    def GetLayerPath(self, layername):
        layername = layername
        layer = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == layername:
                layer = lyr
        return layer.dataProvider().dataSourceUri()




    # 파일 존재 유무 확인
    def CheckFile(self, path):
        filepath = path.replace('\\', '\\\\')
        if (os.path.isfile(filepath)):
            return True
        else:
            return False

    # 폴더 경로 맞는지 확인
    def CheckFolder(self, path):
        filepath = path.replace('\\', '\\\\')
        if (os.path.isdir(filepath)):
            return True
        else:
            return False

    def CheckTaudem(self):
        if os.path.isdir('C:\\Program Files\\TauDEM'):
            return True
        else:
            return False


    # 폴더및 파일 명칭에 한글 포함하고 있는지 체크
    def CheckKorea(self,string):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        strs = re.sub('[^가-힣]', '', string.decode('utf-8').encode('utf-8'))
        if len(strs)>0:
            return True
        else :
            return False

    # 라벨, 타입으로 구분
    def GlobalLabel(self, label, type):
        if type.upper() == "COLROW":
            self.label1 = label
       
    # 라벨, 타입으로 구분
    def GlobalEdit(self, edit, type):
        if type.upper() == "CW":
            self.edit = edit

    # 라벨 텍스트,타입으로 구분
    def GlobalLabel_SetText(self, mess, type):
        if type.upper() == "COLROW":
            self.label1.setText(mess)


    # 라벨 텍스트,타입으로 구분
    def GlobalEdit_SetText(self, mess, type):
        if type.upper() == "CW":
            self.edit.setText(mess)

    # Cell info 정보 넣기
    def GlobalControl(self,Celltype,StreamValue,FD,FA,Slope,watershed):
        self.txtCelltype = Celltype
        self.txtStreamValue=StreamValue
        self.txtFD=FD
        self.txtFA=FA
        self.txtSlope=Slope
        self.txtWatershedID = watershed

    def GlobalControl_SetValue(self, Celltype, StreamValue, FD, FA, Slope,watershed):
        self.txtCelltype.setText(Celltype)
        self.txtCelltype.setCursorPosition(0)
        self.txtStreamValue.setText(StreamValue)
        self.txtFD.setText(FD)
        self.txtFA.setText(FA)
        self.txtSlope.setText(Slope)
        self.txtSlope.setCursorPosition(0)
        self.txtWatershedID.setText(watershed)

    def GlobalControl_Landcover(self,txtLandGridValue, txtLandType, txtRoughness, txtratio):
        self.txtLandGridValue=txtLandGridValue
        self.txtLandType=txtLandType
        self.txtRoughness=txtRoughness
        self.txtratio=txtratio

    def GlobalControl_Landcover_SetValue(self, txtLandGridValue, txtLandType, txtRoughness, txtratio):
        self.txtLandGridValue.setText(txtLandGridValue)
        self.txtLandType.setText(txtLandType)
        self.txtRoughness.setText(txtRoughness)
        self.txtratio.setText(txtratio)



    def GlobalControl_Depth(self,GridValue, UserDepthClass, SoilDepth):
        self.DepthGridValue=GridValue
        self.UserDepthClass=UserDepthClass
        self.SoilDepth= SoilDepth

    def GlobalControl_Depth_SetValue(self,GridValue, UserDepthClass, SoilDepth):
        self.DepthGridValue.setText(str(GridValue))
        self.UserDepthClass.setText(UserDepthClass)
        self.SoilDepth.setText(str(SoilDepth))


    def GlobalControl_texture(self, GridValue, GRMCode, Porosity, EffectivePorosity, WFSoilSuctionHead,
                                       HydraulicConductivity):
        self.GridValue = GridValue
        self.GRMCode = GRMCode
        self.Porosity = Porosity
        self.EffectivePorosity= EffectivePorosity
        self.WFSoilSuctionHead = WFSoilSuctionHead
        self.HydraulicConductivity = HydraulicConductivity

    def GlobalControl_texture_SetValue(self,GridValue, GRMCode, Porosity, EffectivePorosity, WFSoilSuctionHead,HydraulicConductivity):
        self.GridValue.setText(GridValue)
        self.GRMCode.setText(GRMCode)
        self.Porosity.setText(Porosity)
        self.EffectivePorosity.setText(EffectivePorosity)
        self.WFSoilSuctionHead.setText(WFSoilSuctionHead)
        self.HydraulicConductivity.setText(HydraulicConductivity)


   

    def Opewn_ViewFile(self,path):
        _notpad = "C:/Windows/System32/notepad.exe"
        Popen([_notpad,path])

    #def GetFileName(self,path):
    #    name =os.path.basename(path)
    #    a=os.path.splitext(path)[1]
    #    return name.replace(a,"")

        # 파일 경로 중에 파일명만 받아 오기
    def GetFilename(self,filename):
        s = os.path.splitext(filename)
        s = os.path.split(s[0])
        return  s[1]

    def ASC_Header_info(self,asc_file):

        dataHeaderItems = open(asc_file).readlines()[:6]
        read_lower = [item.lower() for item in dataHeaderItems] #리스트 의 모든 글자를 소문자화 시킴
        self.MessageboxShowError("read_lower",read_lower)

        #headerItems=""
        #for row in read_lower:
	       # headerItems = headerItems+row
	       # if "nodata_value" in row:
		      #  header = headerItems
		      #  index_heder= numpy.reshape(header.split(),(6,-1))
	       # elif "nodata_value" not in row:
		      #  if "cellsize" in row:
			     #   header = headerItems
			     #   index_heder= numpy.reshape(header.split(),(5,-1))   
        #return header,index_heder







