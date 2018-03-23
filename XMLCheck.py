# -*- coding: utf-8 -*-

import sys
import os
import os.path
from subprocess import Popen
import Util
import ElementTree as ET
import System
import GRM_Plugin_dockwidget as GRM

import clr
DllPath = os.path.dirname(os.path.realpath(__file__)) + "\DLL\GRMCore.dll"
clr.AddReference(DllPath)
import GRMCore
from GRMCore import GRMProject




_util = Util.util()
class xmls:
    def __init__(self):
        self.ProjectFile = ""

    def  Check_Gmp_xml(self,filepath):
        self.ProjectFile = filepath
        # xml 요소 값을 배열에 넣음
        self.Set_XML_element()
        self.Set_XML_element_SubWatershed()
        self.Set_XML_element_WatchPoints()
        self.Set_XML_element_FlowControlGrid()
        self.Set_XML_element_GreenAmptParameter()
        self.Set_XML_element_SoilDepth()
        self.Set_XML_element_LandCover()

        # xml 파싱
        doc = ET.parse(self.ProjectFile)
        root = doc.getroot()


        GRMProject = ET.Element("GRMProject")
        GRMProject.set("xmlns", "http://tempuri.org/GRMProject.xsd")

        ProjectSettings = ET.SubElement(GRMProject, "ProjectSettings")
        for i in range(0, len(self.XML_element)):
            for element in root.findall('{http://tempuri.org/GRMProject.xsd}ProjectSettings'):
                Datavalue = element.findtext("{http://tempuri.org/GRMProject.xsd}" + self.XML_element[i])
                if self.XML_element[i] == "GRMSimulationType" and (Datavalue == "" or  Datavalue == None):
                    Datavalue = "SingleEvent"
                if self.XML_element[i] == "LandCoverDataType" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "File"
                if self.XML_element[i] == "SoilTextureDataType" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "File"
                if self.XML_element[i] == "SoilDepthDataType" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "File"
                if self.XML_element[i] == "RainfallDataType" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "TextFileASCgrid"
                if self.XML_element[i] == "FlowDirectionType" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "StartsFromE_TauDEM"
                if self.XML_element[i] == "IsParallel" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "true"
                if self.XML_element[i] == "MaxDegreeOfParallelism" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "-1"
                if self.XML_element[i] == "SimulStartingTime" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "0"
                if self.XML_element[i] == "IsFixedTimeStep" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "false"
                if self.XML_element[i] == "'SimulateInfiltration'" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "true"
                if self.XML_element[i] == "SimulateSubsurfaceFlow" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "true"
                if self.XML_element[i] == "SimulateBaseFlow" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "true"
                if self.XML_element[i] == "SimulateFlowControl" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "true"
                if self.XML_element[i] == "CrossSectionType" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "CSSingle"
                if self.XML_element[i] == "SingleCSChannelWidthType" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "CWGemeration"
                if self.XML_element[i] == "BankSideSlopeRight" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "1.5"
                if self.XML_element[i] == "BankSideSlopeLeft" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "1.5"
                if self.XML_element[i] == "MakeIMGFile" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "false"
                if self.XML_element[i] == "MakeASCFile" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "false"
                if self.XML_element[i] == "MakeSoilSaturationDistFile" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "true"
                if self.XML_element[i] == "MakeRfDistFile" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "true"
                if self.XML_element[i] == "MakeRFaccDistFile" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "true"
                if self.XML_element[i] == "MakeFlowDistFile" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "true"
                if self.XML_element[i] == "PrintOption" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "All"
                if self.XML_element[i] == "WriteLog" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "false"
            ET.SubElement(ProjectSettings, self.XML_element[i]).text = Datavalue


        GRM._SubWatershedCount = 0
        for element in root.findall('{http://tempuri.org/GRMProject.xsd}SubWatershedSettings'):
            SubWatershedSettings = ET.SubElement(GRMProject, "SubWatershedSettings")
            for i in range(0, len(self.XML_element_SubWatershed)):
                Datavalue = element.findtext("{http://tempuri.org/GRMProject.xsd}" + self.XML_element_SubWatershed[i])
                if self.XML_element_SubWatershed[i] == "IniSaturation" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "1"
                elif self.XML_element_SubWatershed[i] == "MinSlopeOF" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "0.0001"
                elif self.XML_element_SubWatershed[i] == "MinSlopeChBed" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "0.0001"
                elif self.XML_element_SubWatershed[i] == "MinChBaseWidth" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "00"
                elif self.XML_element_SubWatershed[i] == "ChRoughness" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "0.045"
                elif self.XML_element_SubWatershed[i] == "DryStreamOrder" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "0"
                elif self.XML_element_SubWatershed[i] == "IniFlow" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "0"
                elif self.XML_element_SubWatershed[i] == "UnsaturatedKType" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "Linear"
                elif self.XML_element_SubWatershed[i] == "CoefUnsaturatedK" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "0.2"
                elif self.XML_element_SubWatershed[i] == "CalCoefLCRoughness" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "1"
                elif self.XML_element_SubWatershed[i] == "CalCoefPorosity" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "1"
                elif self.XML_element_SubWatershed[i] == "CalCoefWFSuctionHead" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "1"
                elif self.XML_element_SubWatershed[i] == "CalCoefHydraulicK" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "1"
                elif self.XML_element_SubWatershed[i] == "CalCoefSoilDepth" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "1"
                if self.XML_element_SubWatershed[i] == "UserSet" and (Datavalue == "" or Datavalue == None):
                    Datavalue = "false"
                ET.SubElement(SubWatershedSettings, self.XML_element_SubWatershed[i]).text = Datavalue
            GRM._SubWatershedCount =GRM._SubWatershedCount +1
        GRM._WatchPointCount=0
        for element in root.findall('{http://tempuri.org/GRMProject.xsd}WatchPoints'):
            WatchPoints = ET.SubElement(GRMProject, "WatchPoints")
            for i in range(0, len(self.XML_element_WatchPoints)):
                Datavalue = element.findtext("{http://tempuri.org/GRMProject.xsd}" + self.XML_element_WatchPoints[i])
                if self.XML_element_WatchPoints[i] == "Name" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_WatchPoints[i] == "ColX" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_WatchPoints[i] == "RowY" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                ET.SubElement(WatchPoints, self.XML_element_WatchPoints[i]).text = Datavalue
            GRM._WatchPointCount = GRM._WatchPointCount+1

        GRM._FlowControlCount=0
        for element in root.findall('{http://tempuri.org/GRMProject.xsd}FlowControlGrid'):
            FlowControlGrid = ET.SubElement(GRMProject, "FlowControlGrid")
            for i in range(0, len(self.XML_element_FlowControlGrid)):
                Datavalue = element.findtext("{http://tempuri.org/GRMProject.xsd}" + self.XML_element_FlowControlGrid[i])
                if self.XML_element_FlowControlGrid[i] == "ColX" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_FlowControlGrid[i] == "RowY" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_FlowControlGrid[i] == "Name" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_FlowControlGrid[i] == "ControlType" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_FlowControlGrid[i] == "DT" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_FlowControlGrid[i] == "FlowDataFile" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_FlowControlGrid[i] == "IniStorage" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_FlowControlGrid[i] == "MaxStorage" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_FlowControlGrid[i] == "MaxStorageR" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_FlowControlGrid[i] == "ROType" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_FlowControlGrid[i] == "ROConstQ" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_FlowControlGrid[i] == "ROConstQDuration" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                ET.SubElement(FlowControlGrid, self.XML_element_FlowControlGrid[i]).text = Datavalue
            GRM._FlowControlCount = GRM._FlowControlCount + 1

        GRM._GreenAmptCount=0
        for element in root.findall('{http://tempuri.org/GRMProject.xsd}GreenAmptParameter'):
            GreenAmptParameter = ET.SubElement(GRMProject, "GreenAmptParameter")
            for i in range(0, len(self.XML_element_GreenAmptParameter)):
                Datavalue = element.findtext("{http://tempuri.org/GRMProject.xsd}" + self.XML_element_GreenAmptParameter[i])
                if self.XML_element_GreenAmptParameter[i] == "GridValue" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_GreenAmptParameter[i] == "USERSoil" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_GreenAmptParameter[i] == "GRMCode" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_GreenAmptParameter[i] == "GRMTextureE" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_GreenAmptParameter[i] == "GRMTextureK" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_GreenAmptParameter[i] == "Porosity" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_GreenAmptParameter[i] == "EffectivePorosity" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_GreenAmptParameter[i] == "WFSoilSuctionHead" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_GreenAmptParameter[i] == "HydraulicConductivity" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                ET.SubElement(GreenAmptParameter, self.XML_element_GreenAmptParameter[i]).text = Datavalue
            GRM._GreenAmptCount = GRM._GreenAmptCount + 1

        GRM._SoilDepthCount=0
        for element in root.findall('{http://tempuri.org/GRMProject.xsd}SoilDepth'):
            SoilDepth = ET.SubElement(GRMProject, "SoilDepth")
            for i in range(0, len(self.XML_element_SoilDepth)):
                if self.XML_element_SoilDepth[i] =="SoilDeptht":
                    Datavalue = element.findtext("{http://tempuri.org/GRMProject.xsd}SoilDepth")

                else:
                    Datavalue = element.findtext("{http://tempuri.org/GRMProject.xsd}" + self.XML_element_SoilDepth[i])

                if self.XML_element_SoilDepth[i] == "GridValue" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_SoilDepth[i] == "UserDepthClass" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_SoilDepth[i] == "GRMCode" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_SoilDepth[i] == "SoilDepthClassE" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_SoilDepth[i] == "SoilDepthClassK" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_SoilDepth[i] == "SoilDeptht" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                ET.SubElement(SoilDepth, self.XML_element_SoilDepth[i]).text = Datavalue
            GRM._SoilDepthCount = GRM._SoilDepthCount + 1

        GRM._LandCoverCount=0
        for element in root.findall('{http://tempuri.org/GRMProject.xsd}LandCover'):
            LandCover = ET.SubElement(GRMProject, "LandCover")
            for i in range(0, len(self.XML_element_LandCover)):
                Datavalue = element.findtext("{http://tempuri.org/GRMProject.xsd}" + self.XML_element_LandCover[i])
                if self.XML_element_LandCover[i] == "GridValue" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_LandCover[i] == "UserLandCover" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_LandCover[i] == "GRMCode" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_LandCover[i] == "GRMLandCoverE" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_LandCover[i] == "GRMLandCoverK" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_LandCover[i] == "RoughnessCoefficient" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                if self.XML_element_LandCover[i] == "ImperviousRatio" and (Datavalue == "" or Datavalue == None):
                    Datavalue = ""
                ET.SubElement(LandCover, self.XML_element_LandCover[i]).text = Datavalue
            GRM._LandCoverCount = GRM._LandCoverCount + 1

        ET.ElementTree(GRMProject).write(self.ProjectFile, encoding="utf-8", xml_declaration=True)

        with open(self.ProjectFile, 'r') as f:
            content = f.read()
            result = content.replace("SoilDeptht","SoilDepth")

        f = open(self.ProjectFile, 'w')
        f.write(result)
        f.close()

        ## 줄바꿈과 뛰어쓰기 부분
        #def indent(elem, level=0):
        #    i = "\n" + level * "  "
        #    j = "\n" + (level - 1) * "  "
        #    if len(elem):
        #        if not elem.text or not elem.text.strip():
        #            elem.text = i + "  "
        #        if not elem.tail or not elem.tail.strip():
        #            elem.tail = i
        #        for subelem in elem:
        #            indent(subelem, level + 1)
        #        if not elem.tail or not elem.tail.strip():
        #            elem.tail = i
        #    else:
        #        if level and (not elem.tail or not elem.tail.strip()):
        #            elem.tail = i
        #    return elem

        ## 저장된 파일 다시 불러와서 줄바꿈과 정렬 하기
        #doc = ET.parse(self.ProjectFile)
        #root = doc.getroot()
        #ET.register_namespace("", "http://tempuri.org/GRMProject.xsd")
        #indent(root)
        #doc.write(self.ProjectFile, encoding="utf-8", xml_declaration=True)
        ds = GRMCore.GRMProject()
        ds.ReadXml(self.ProjectFile)
        ds.WriteXml(self.ProjectFile)
        ds.Dispose()

    def Set_XML_element(self):
        self.XML_element = []
        self.XML_element.append('ProjectFile')
        self.XML_element.append('GRMSimulationType')
        self.XML_element.append('WatershedFile')
        self.XML_element.append('SlopeFile')
        self.XML_element.append('FlowDirectionFile')
        self.XML_element.append('FlowAccumFile')
        self.XML_element.append('StreamFile')
        self.XML_element.append('ChannelWidthFile')
        self.XML_element.append('InitialSoilSaturationRatioFile')
        self.XML_element.append('LandCoverDataType')
        self.XML_element.append('LandCoverFile')
        self.XML_element.append('LandCoverVATFile')
        self.XML_element.append('ConstantRoughnessCoeff')
        self.XML_element.append('ConstantImperviousRatio')
        self.XML_element.append('SoilTextureDataType')
        self.XML_element.append('SoilTextureFile')
        self.XML_element.append('SoilTextureVATFile')
        self.XML_element.append('ConstantSoilPorosity')
        self.XML_element.append('ConstantSoilEffPorosity')
        self.XML_element.append('ConstantSoilWettingFrontSuctionHead')
        self.XML_element.append('ConstantSoilHydraulicConductivity')
        self.XML_element.append('SoilDepthDataType')
        self.XML_element.append('SoilDepthFile')
        self.XML_element.append('SoilDepthVATFile')
        self.XML_element.append('ConstantSoilDepth')
        self.XML_element.append('InitialChannelFlowFile')
        self.XML_element.append('RainfallDataType')
        self.XML_element.append('RainfallInterval')
        self.XML_element.append('RainfallDataFile')
        self.XML_element.append('FlowDirectionType')
        self.XML_element.append('GridCellSize')
        self.XML_element.append('IsParallel')
        self.XML_element.append('MaxDegreeOfParallelism')
        self.XML_element.append('SimulStartingTime')
        self.XML_element.append('ComputationalTimeStep')
        self.XML_element.append('IsFixedTimeStep')
        self.XML_element.append('SimulationDuration')
        self.XML_element.append('OutputTimeStep')
        self.XML_element.append('SimulateInfiltration')
        self.XML_element.append('SimulateSubsurfaceFlow')
        self.XML_element.append('SimulateBaseFlow')
        self.XML_element.append('SimulateFlowControl')
        self.XML_element.append('CrossSectionType')
        self.XML_element.append('SingleCSChannelWidthType')
        self.XML_element.append('ChannelWidthEQc')
        self.XML_element.append('ChannelWidthEQd')
        self.XML_element.append('ChannelWidthEQe')
        self.XML_element.append('ChannelWidthMostDownStream')
        self.XML_element.append('LowerRegionHeight')
        self.XML_element.append('LowerRegionBaseWidth')
        self.XML_element.append('UpperRegionBaseWidth')
        self.XML_element.append('CompoundCSIniFlowDepth')
        self.XML_element.append('CompoundCSChannelWidthLimit')
        self.XML_element.append('BankSideSlopeRight')
        self.XML_element.append('BankSideSlopeLeft')
        self.XML_element.append('MakeIMGFile')
        self.XML_element.append('MakeASCFile')
        self.XML_element.append('MakeSoilSaturationDistFile')
        self.XML_element.append('MakeRfDistFile')
        self.XML_element.append('MakeRFaccDistFile')
        self.XML_element.append('MakeFlowDistFile')
        self.XML_element.append('PrintOption')
        self.XML_element.append('WriteLog')
        self.XML_element.append('AboutThisProject')
        self.XML_element.append('AboutWatershed')
        self.XML_element.append('AboutLandCoverMap')
        self.XML_element.append('AboutSoilMap')
        self.XML_element.append('AboutSoilDepthMap')
        self.XML_element.append('AboutRainfall')
        self.XML_element.append('ProjectSavedTime')
        self.XML_element.append('ComputerName')
        self.XML_element.append('ComputerUserName')
        self.XML_element.append('GRMVersion')

    def Set_XML_element_SubWatershed(self):
        self.XML_element_SubWatershed = []
        self.XML_element_SubWatershed.append('ID')
        self.XML_element_SubWatershed.append('IniSaturation')
        self.XML_element_SubWatershed.append('MinSlopeOF')
        self.XML_element_SubWatershed.append('MinSlopeChBed')
        self.XML_element_SubWatershed.append('MinChBaseWidth')
        self.XML_element_SubWatershed.append('ChRoughness')
        self.XML_element_SubWatershed.append('DryStreamOrder')
        self.XML_element_SubWatershed.append('IniFlow')
        self.XML_element_SubWatershed.append('UnsaturatedKType')
        self.XML_element_SubWatershed.append('CoefUnsaturatedK')
        self.XML_element_SubWatershed.append('CalCoefLCRoughness')
        self.XML_element_SubWatershed.append('CalCoefPorosity')
        self.XML_element_SubWatershed.append('CalCoefWFSuctionHead')
        self.XML_element_SubWatershed.append('CalCoefHydraulicK')
        self.XML_element_SubWatershed.append('CalCoefSoilDepth')
        self.XML_element_SubWatershed.append('UserSet')

    def Set_XML_element_WatchPoints(self):
        self.XML_element_WatchPoints = []
        self.XML_element_WatchPoints.append('Name')
        self.XML_element_WatchPoints.append('ColX')
        self.XML_element_WatchPoints.append('RowY')

    def Set_XML_element_FlowControlGrid(self):
        self.XML_element_FlowControlGrid = []
        self.XML_element_FlowControlGrid.append('ColX')
        self.XML_element_FlowControlGrid.append('RowY')
        self.XML_element_FlowControlGrid.append('Name')
        self.XML_element_FlowControlGrid.append('ControlType')
        self.XML_element_FlowControlGrid.append('DT')
        self.XML_element_FlowControlGrid.append('FlowDataFile')
        self.XML_element_FlowControlGrid.append('IniStorage')
        self.XML_element_FlowControlGrid.append('MaxStorage')
        self.XML_element_FlowControlGrid.append('MaxStorageR')
        self.XML_element_FlowControlGrid.append('ROType')
        self.XML_element_FlowControlGrid.append('ROConstQ')
        self.XML_element_FlowControlGrid.append('ROConstQDuration')

    def Set_XML_element_GreenAmptParameter(self):
        self.XML_element_GreenAmptParameter = []
        self.XML_element_GreenAmptParameter.append('GridValue')
        self.XML_element_GreenAmptParameter.append('USERSoil')
        self.XML_element_GreenAmptParameter.append('GRMCode')
        self.XML_element_GreenAmptParameter.append('GRMTextureE')
        self.XML_element_GreenAmptParameter.append('GRMTextureK')
        self.XML_element_GreenAmptParameter.append('Porosity')
        self.XML_element_GreenAmptParameter.append('EffectivePorosity')
        self.XML_element_GreenAmptParameter.append('WFSoilSuctionHead')
        self.XML_element_GreenAmptParameter.append('HydraulicConductivity')

    def Set_XML_element_SoilDepth(self):
        self.XML_element_SoilDepth = []
        self.XML_element_SoilDepth.append('GridValue')
        self.XML_element_SoilDepth.append('UserDepthClass')
        self.XML_element_SoilDepth.append('GRMCode')
        self.XML_element_SoilDepth.append('SoilDepthClassE')
        self.XML_element_SoilDepth.append('SoilDepthClassK')
        # python 버그???  SoilDepth 상위 태그와 subelement 이름이 같으면 값이 안들어감
        # 그래서 이름 다르게 넣고 나중에 Replace
        self.XML_element_SoilDepth.append('SoilDeptht')

        # self.XML_element_SoilDepth.append('SoilDepth')

    def Set_XML_element_LandCover(self):
        self.XML_element_LandCover=[]
        self.XML_element_LandCover.append('GridValue')
        self.XML_element_LandCover.append('UserLandCover')
        self.XML_element_LandCover.append('GRMCode')
        self.XML_element_LandCover.append('GRMLandCoverE')
        self.XML_element_LandCover.append('GRMLandCoverK')
        self.XML_element_LandCover.append('RoughnessCoefficient')
        self.XML_element_LandCover.append('ImperviousRatio')

