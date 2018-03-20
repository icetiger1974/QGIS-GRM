# -*- coding: utf-8 -*-

import sys
import os
import os.path
from subprocess import Popen
import GRM_Plugin_dockwidget as GRM
import ElementTree as ET
import Util
reload(sys)
sys.setdefaultencoding('utf-8')


_util = Util.util()
class xmls:
    def __init__(self):
        self.ProjectFile = ""
        self.SubWatershedSettings_Count = 0
        self.SubWatershedSettings_ID = []
        self.Texture_Count = 0
        self.SoilDepth_Count = 0
        self.LandCover_Count = 0
        self.WatchPoint_Count = 0
        self.FlowControlGrid_Count = 0

    def ProjectLoad(self):
        self.ProjectFile = GRM._xmltodict['GRMProject']['ProjectSettings']['ProjectFile']

        self.XML_Element_Count_check()


    def XML_Element_Count_check(self):
        doc = ET.parse(self.ProjectFile)
        root = doc.getroot()
        WatchPoint=[];Texture=[];SoilDepth=[];LandCover=[];FlowControlGrid = []
        # SUbWatershedSettings 숫자 확인 나중에 파싱에 사용
        for element in root.findall('{http://tempuri.org/GRMProject.xsd}SubWatershedSettings'):
            self.SubWatershedSettings_ID.append(element.findtext("{http://tempuri.org/GRMProject.xsd}ID"))
        self.SubWatershedSettings_Count = len(self.SubWatershedSettings_ID)

        for element in root.findall('{http://tempuri.org/GRMProject.xsd}WatchPoints'):
            WatchPoint.append(element.findtext("{http://tempuri.org/GRMProject.xsd}Name"))
        self.SubWatershedSettings_Count = len(WatchPoint)


        for element in root.findall('{http://tempuri.org/GRMProject.xsd}GreenAmptParameter'):
            Texture.append(element.findtext("{http://tempuri.org/GRMProject.xsd}GridValue"))
        self.Texture_Count = len(Texture)


        for element in root.findall('{http://tempuri.org/GRMProject.xsd}SoilDepth'):
            SoilDepth.append(element.findtext("{http://tempuri.org/GRMProject.xsd}GridValue"))
        self.SoilDepth_Count = len(SoilDepth)


        for element in root.findall('{http://tempuri.org/GRMProject.xsd}LandCover'):
            LandCover.append(element.findtext("{http://tempuri.org/GRMProject.xsd}GridValue"))
        self.LandCover_Count = len(LandCover)


        for element in root.findall('{http://tempuri.org/GRMProject.xsd}FlowControlGrid'):
            FlowControlGrid.append(element.findtext("{http://tempuri.org/GRMProject.xsd}ColX"))
        self.FlowControlGrid_Count  = len(FlowControlGrid)

