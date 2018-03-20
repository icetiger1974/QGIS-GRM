#-*- coding: utf-8 -*-
'''
작성자: 화상 쪼민혜 작성
작성일:2017/08/31

'''

import ElementTree as ET
import Util

_util= Util.util()

class ProjectSettings():
    def __init__(self,path):
        doc = ET.parse(path)
        root = doc.getroot()
        for element in root.findall('{http://tempuri.org/GRMProject.xsd}ProjectSettings'):
            self.ProjectFile_set( element.findtext('{http://tempuri.org/GRMProject.xsd}ProjectFile'))
            self.GRMStaticDB_set(element.findtext('{http://tempuri.org/GRMProject.xsd}GRMStaticDB'))
            self.GRMSimulationType_set(element.findtext('{http://tempuri.org/GRMProject.xsd}GRMSimulationType'))
            self.WatershedFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}WatershedFile'))
            self.SlopeFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SlopeFile'))
            self.FlowDirectionFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}FlowDirectionFile'))
            self.FlowAccumFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}FlowAccumFile'))
            self.StreamFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}StreamFile'))
            self.ChannelWidthFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}ChannelWidthFile '))
            self.LandCoverDataType_set(element.findtext('{http://tempuri.org/GRMProject.xsd}LandCoverDataType'))
            self.LandCoverFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}LandCoverFile'))
            self.LandCoverVATFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}LandCoverVATFile'))
            self.SoilTextureDataType_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SoilTextureDataType'))
            self.SoilTextureFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SoilTextureFile'))
            self.SoilTextureVATFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SoilTextureVATFile'))
            self.SoilDepthDataType_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SoilDepthDataType'))
            self.SoilDepthFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SoilDepthFile'))
            self.SoilDepthVATFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SoilDepthVATFile'))
            self.RainfallDataType_set(element.findtext('{http://tempuri.org/GRMProject.xsd}RainfallDataType'))
            self.RainfallInterval_set(element.findtext('{http://tempuri.org/GRMProject.xsd}RainfallInterval'))
            self.RainfallDuration_set(element.findtext('{http://tempuri.org/GRMProject.xsd}RainfallDuration'))
            self.RainfallDataFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}RainfallDataFile'))
            self.FlowDirectionType_set(element.findtext('{http://tempuri.org/GRMProject.xsd}FlowDirectionType'))
            self.GridCellSize_set(element.findtext('{http://tempuri.org/GRMProject.xsd}GridCellSize'))
            self.IsParallel_set(element.findtext('{http://tempuri.org/GRMProject.xsd}IsParallel'))
            self.ComputationalTimeStep_set(element.findtext('{http://tempuri.org/GRMProject.xsd}ComputationalTimeStep'))
            self.IsFixedTimeStep_set(element.findtext('{http://tempuri.org/GRMProject.xsd}IsFixedTimeStep'))
            self.SimulationDuration_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SimulationDuration'))
            self.OutputTimeStep_set(element.findtext('{http://tempuri.org/GRMProject.xsd}OutputTimeStep'))
            self.SimulateInfiltration_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SimulateInfiltration'))
            self.SimulateSubsurfaceFlow_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SimulateSubsurfaceFlow'))
            self.SimulateBaseFlow_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SimulateBaseFlow'))
            self.SimulateFlowControl_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SimulateFlowControl'))
            self.WatchPointCount_set(element.findtext('{http://tempuri.org/GRMProject.xsd}WatchPointCount'))
            self.CrossSectionType_set(element.findtext('{http://tempuri.org/GRMProject.xsd}CrossSectionType'))
            self.SingleCSChannelWidthType_set(element.findtext('{http://tempuri.org/GRMProject.xsd}SingleCSChannelWidthType'))
            self.ChannelWidthEQc_set(element.findtext('{http://tempuri.org/GRMProject.xsd}ChannelWidthEQc'))
            self.ChannelWidthEQd_set(element.findtext('{http://tempuri.org/GRMProject.xsd}ChannelWidthEQd'))
            self.ChannelWidthEQe_set(element.findtext('{http://tempuri.org/GRMProject.xsd}ChannelWidthEQe'))
            self.ChannelWidthMostDownStream_set(element.findtext('{http://tempuri.org/GRMProject.xsd}ChannelWidthMostDownStream'))
            self.LowerRegionHeight_set(element.findtext('{http://tempuri.org/GRMProject.xsd}LowerRegionHeight'))
            self.LowerRegionBaseWidth_set(element.findtext('{http://tempuri.org/GRMProject.xsd}LowerRegionBaseWidth'))
            self.UpperRegionBaseWidth_set(element.findtext('{http://tempuri.org/GRMProject.xsd}UpperRegionBaseWidth'))
            self.CompoundCSIniFlowDepth_set(element.findtext('{http://tempuri.org/GRMProject.xsd}CompoundCSIniFlowDepth'))
            self.CompoundCSChannelWidthLimit_set(element.findtext('{http://tempuri.org/GRMProject.xsd}CompoundCSChannelWidthLimit'))
            self.BankSideSlopeRight_set(element.findtext('{http://tempuri.org/GRMProject.xsd}BankSideSlopeRight'))
            self.BankSideSlopeLeft_set(element.findtext('{http://tempuri.org/GRMProject.xsd}BankSideSlopeLeft'))
            self.FlowAccumulationMax_set(element.findtext('{http://tempuri.org/GRMProject.xsd}FlowAccumulationMax'))
            self.MakeIMGFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}MakeIMGFile'))
            self.MakeASCFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}MakeASCFile'))
            self.MakeSoilSaturationDistFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}MakeSoilSaturationDistFile'))
            self.MakeRfDistFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}MakeRfDistFile'))
            self.MakeRFaccDistFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}MakeRFaccDistFile'))
            self.MakeFlowDistFile_set(element.findtext('{http://tempuri.org/GRMProject.xsd}MakeFlowDistFile'))
            self.MakeOutputDischargeOnly_set(element.findtext('{http://tempuri.org/GRMProject.xsd}MakeOutputDischargeOnly'))
            self.ProjectSavedTime_set(element.findtext('{http://tempuri.org/GRMProject.xsd}ProjectSavedTime'))
            self.ComputerName_set(element.findtext('{http://tempuri.org/GRMProject.xsd}ComputerName'))
            self.ComputerUserName_set(element.findtext('{http://tempuri.org/GRMProject.xsd}ComputerUserName'))
            self.GRMVersion_set(element.findtext('{http://tempuri.org/GRMProject.xsd}GRMVersion'))


    def ProjectFile_set(self,value) :
        global ProjectFile
        self.ProjectFile = value
    def ProjectFile_get(self):
        return self.ProjectFile

    def GRMStaticDB_set(self,value) :
        self.GRMStaticDB= value
    def GRMStaticDB_get(self):
        return self.GRMStaticDB

    def GRMSimulationType_set(self,value) :
        self.GRMSimulationType= value
    def GRMSimulationType_get(self):
        return self.GRMSimulationType

    def WatershedFile_set(self,value) :
        self.WatershedFile= value
    def WatershedFile_get(self):
        return self.WatershedFile

    def SlopeFile_set(self,value) :
        self.SlopeFile= value
    def SlopeFile_get(self):
        return self.SlopeFile

    def FlowDirectionFile_set(self,value) :
        self.FlowDirectionFile= value
    def FlowDirectionFile_get(self):
        return self.FlowDirectionFile

    def FlowAccumFile_set(self,value) :
        self.FlowAccumFile= value
    def FlowAccumFile_get(self):
        return self.FlowAccumFile

    def StreamFile_set(self,value) :
        self.StreamFile= value
    def StreamFile_get(self):
        return self.StreamFile

    def ChannelWidthFile_set(self,value) :
        self.ChannelWidthFile = value
    def ChannelWidthFile_get(self):
        return self.ChannelWidthFile

    def LandCoverDataType_set(self,value) :
        self.LandCoverDataType= value
    def LandCoverDataType_get(self):
        return self.LandCoverDataType

    def LandCoverFile_set(self,value) :
        self.LandCoverFile= value
    def LandCoverFile_get(self):
        return self.LandCoverFile

    def LandCoverVATFile_set(self,value) :
        self.LandCoverVATFile= value
    def LandCoverVATFile_get(self):
        return self.LandCoverVATFile

    def SoilTextureDataType_set(self,value) :
        self.SoilTextureDataType= value
    def SoilTextureDataType_get(self):
        return self.SoilTextureDataType

    def SoilTextureFile_set(self,value) :
        self.SoilTextureFile= value
    def SoilTextureFile_get(self):
        return self.SoilTextureFile

    def SoilTextureVATFile_set(self,value) :
        self.SoilTextureVATFile= value
    def SoilTextureVATFile_get(self):
        return self.SoilTextureVATFile

    def SoilDepthDataType_set(self,value) :
        self.SoilDepthDataType= value
    def SoilDepthDataType_get(self):
        return self.SoilDepthDataType

    def SoilDepthFile_set(self,value) :
        self.SoilDepthFile= value
    def SoilDepthFile_get(self):
        return self.SoilDepthFile

    def SoilDepthVATFile_set(self,value) :
        self.SoilDepthVATFile= value
    def SoilDepthVATFile_get(self):
        return self.SoilDepthVATFile

    def RainfallDataType_set(self,value) :
        self.RainfallDataType= value
    def RainfallDataType_get(self):
        return self.RainfallDataType

    def RainfallInterval_set(self,value) :
        self.RainfallInterval= value
    def RainfallInterval_get(self):
        return self.RainfallInterval

    def RainfallDuration_set(self,value) :
        self.RainfallDuration= value
    def RainfallDuration_get(self):
        return self.RainfallDuration

    def RainfallDataFile_set(self,value) :
        self.RainfallDataFile= value
    def RainfallDataFile_get(self):
        return self.RainfallDataFile

    def FlowDirectionType_set(self,value) :
        self.FlowDirectionType= value
    def FlowDirectionType_get(self):
        return self.FlowDirectionType

    def GridCellSize_set(self,value) :
        self.GridCellSize= value
    def GridCellSize_get(self):
        return self.GridCellSize

    def IsParallel_set(self,value) :
        self.IsParallel= value
    def IsParallel_get(self):
        return self.IsParallel

    def ComputationalTimeStep_set(self,value) :
        self.ComputationalTimeStep= value
    def ComputationalTimeStep_get(self):
        return self.ComputationalTimeStep

    def IsFixedTimeStep_set(self,value) :
        self.IsFixedTimeStep= value
    def IsFixedTimeStep_get(self):
        return self.IsFixedTimeStep

    def SimulationDuration_set(self,value) :
        self.SimulationDuration= value
    def SimulationDuration_get(self):
        return self.SimulationDuration

    def OutputTimeStep_set(self,value) :
        self.OutputTimeStep= value
    def OutputTimeStep_get(self):
        return self.OutputTimeStep

    def SimulateInfiltration_set(self,value) :
        self.SimulateInfiltration= value
    def SimulateInfiltration_get(self):
        return self.SimulateInfiltration

    def SimulateSubsurfaceFlow_set(self,value) :
        self.SimulateSubsurfaceFlow= value
    def SimulateSubsurfaceFlow_get(self):
        return self.SimulateSubsurfaceFlow

    def SimulateBaseFlow_set(self,value) :
        self.SimulateBaseFlow= value
    def SimulateBaseFlow_get(self):
        return self.SimulateBaseFlow

    def SimulateFlowControl_set(self,value) :
        self.SimulateFlowControl= value
    def SimulateFlowControl_get(self):
        return self.SimulateFlowControl

    def WatchPointCount_set(self,value) :
        self.WatchPointCount= value
    def WatchPointCount_get(self):
        return self.WatchPointCount

    def CrossSectionType_set(self,value) :
        self.CrossSectionType= value
    def CrossSectionType_get(self):
        return self.CrossSectionType

    def SingleCSChannelWidthType_set(self,value) :
        self.SingleCSChannelWidthType= value
    def SingleCSChannelWidthType_get(self):
        return self.SingleCSChannelWidthType

    def ChannelWidthEQc_set(self,value) :
        self.ChannelWidthEQc= value
    def ChannelWidthEQc_get(self):
        return self.ChannelWidthEQc

    def ChannelWidthEQd_set(self,value) :
        self.ChannelWidthEQd= value
    def ChannelWidthEQd_get(self):
        return self.ChannelWidthEQd

    def ChannelWidthEQe_set(self,value) :
        self.ChannelWidthEQe= value
    def ChannelWidthEQe_get(self):
        return self.ChannelWidthEQe

    def ChannelWidthMostDownStream_set(self,value) :
        self.ChannelWidthMostDownStream= value
    def ChannelWidthMostDownStream_get(self):
        return self.ChannelWidthMostDownStream

    def LowerRegionHeight_set(self,value) :
        self.LowerRegionHeight= value
    def LowerRegionHeight_get(self):
        return self.LowerRegionHeight

    def LowerRegionBaseWidth_set(self,value) :
        self.LowerRegionBaseWidth= value
    def LowerRegionBaseWidth_get(self):
        return self.LowerRegionBaseWidth

    def UpperRegionBaseWidth_set(self,value) :
        self.UpperRegionBaseWidth= value
    def UpperRegionBaseWidth_get(self):
        return self.UpperRegionBaseWidth

    def CompoundCSIniFlowDepth_set(self,value) :
        self.CompoundCSIniFlowDepth= value
    def CompoundCSIniFlowDepth_get(self):
        return self.CompoundCSIniFlowDepth

    def CompoundCSChannelWidthLimit_set(self,value) :
        self.CompoundCSChannelWidthLimit= value
    def CompoundCSChannelWidthLimit_get(self):
        return self.CompoundCSChannelWidthLimit

    def BankSideSlopeRight_set(self,value) :
        self.BankSideSlopeRight= value
    def BankSideSlopeRight_get(self):
        return self.BankSideSlopeRight

    def BankSideSlopeLeft_set(self,value) :
        self.BankSideSlopeLeft= value
    def BankSideSlopeLeft_get(self):
        return self.BankSideSlopeLeft

    def FlowAccumulationMax_set(self,value) :
        self.FlowAccumulationMax= value
    def FlowAccumulationMax_get(self):
        return self.FlowAccumulationMax

    def MakeIMGFile_set(self,value) :
        self.MakeIMGFile= value
    def MakeIMGFile_get(self):
        return self.MakeIMGFile

    def MakeASCFile_set(self,value) :
        self.MakeASCFile= value
    def MakeASCFile_get(self):
        return self.MakeASCFile

    def MakeSoilSaturationDistFile_set(self,value) :
        self.MakeSoilSaturationDistFile= value
    def MakeSoilSaturationDistFile_get(self):
        return self.MakeSoilSaturationDistFile

    def MakeRfDistFile_set(self,value) :
        self.MakeRfDistFile= value
    def MakeRfDistFile_get(self):
        return self.MakeRfDistFile

    def MakeRFaccDistFile_set(self,value) :
        self.MakeRFaccDistFile= value
    def MakeRFaccDistFile_get(self):
        return self.MakeRFaccDistFile

    def MakeFlowDistFile_set(self,value) :
        self.MakeFlowDistFile= value
    def MakeFlowDistFile_get(self):
        return self.MakeFlowDistFile

    def MakeOutputDischargeOnly_set(self,value) :
        self.MakeOutputDischargeOnly= value
    def MakeOutputDischargeOnly_get(self):
        return self.MakeOutputDischargeOnly

    def ProjectSavedTime_set(self,value) :
        self.ProjectSavedTime= value
    def ProjectSavedTime_get(self):
        return self.ProjectSavedTime

    def ComputerName_set(self,value) :
        self.ComputerName= value
    def ComputerName_get(self):
        return self.ComputerName

    def ComputerUserName_set(self,value) :
        self.ComputerUserName= value
    def ComputerUserName_get(self):
        return self.ComputerUserName

    def GRMVersion_set(self,value) :
        self.GRMVersion= value
    def GRMVersion_get(self):
        return self.GRMVersion

class SubWatershedSettings():
    def  ID_set(self,value):
        self.ID=value
    def  ID_get(self):
        return self.ID

    def  IniSaturation_set(self,value):
        self.IniSaturation=value
    def  IniSaturation_get(self):
        return self.IniSaturation

    def  MinSlopeOF_set(self,value):
        self.MinSlopeOF=value
    def  MinSlopeOF_get(self):
        return self.MinSlopeOF

    def  MinSlopeChBed_set(self,value):
        self.MinSlopeChBed=value
    def  MinSlopeChBed_get(self):
        return self.MinSlopeChBed

    def  MinChBaseWidth_set(self,value):
        self.MinChBaseWidth=value
    def  MinChBaseWidth_get(self):
        return self.MinChBaseWidth

    def  ChRoughness_set(self,value):
        self.ChRoughness=value
    def  ChRoughness_get(self):
        return self.ChRoughness

    def  DryStreamOrder_set(self,value):
        self.DryStreamOrder=value
    def  DryStreamOrder_get(self):
        return self.DryStreamOrder

    def  IniFlow_set(self,value):
        self.IniFlow=value
    def  IniFlow_get(self):
        return self.IniFlow

    def  CalCoefLCRoughness_set(self,value):
        self.CalCoefLCRoughness=value
    def  CalCoefLCRoughness_get(self):
        return self.CalCoefLCRoughness

    def  CalCoefPorosity_set(self,value):
        self.CalCoefPorosity=value
    def  CalCoefPorosity_get(self):
        return self.CalCoefPorosity

    def  CalCoefWFSuctionHead_set(self,value):
        self.CalCoefWFSuctionHead=value
    def  CalCoefWFSuctionHead_get(self):
        return self.CalCoefWFSuctionHead

    def  CalCoefHydraulicK_set(self,value):
        self.CalCoefHydraulicK=value
    def  CalCoefHydraulicK_get(self):
        return self.CalCoefHydraulicK

    def  CalCoefSoilDepth_set(self,value):
        self.CalCoefSoilDepth=value
    def  CalCoefSoilDepth_get(self):
        return self.CalCoefSoilDepth

    def  UserSet_set(self,value):
        self.UserSet=value
    def  UserSet_get(self):
        return self.UserSet
    
class WatchPoints():
    def CVID_set(self,value):
        self.CVID=value
    def CVID_get(self):
        return self.CVID

    def Name_set(self,value):
        self.Name=value
    def Name_get(self):
        return self.Name

    def FlowAccumulation_set(self,value):
        self.FlowAccumulation=value
    def FlowAccumulation_get(self):
        return self.FlowAccumulation

    def CellType_set(self,value):
        self.CellType=value
    def CellType_get(self):
        return self.CellType

    def ColX_set(self,value):
        self.ColX=value
    def ColX_get(self):
        return self.ColX

    def RowY_set(self,value):
        self.RowY=value
    def RowY_get(self):
        return self.RowY
    
    
    
    
    
    
