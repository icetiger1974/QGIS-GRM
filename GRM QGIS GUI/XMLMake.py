# -*- coding: utf-8 -*-

import os
import sys
from ElementTree import Element, ElementTree , SubElement, dump, parse, tostring

class make:
    def __init__(self):
       self.ProjectFile = ""

    # New Project 시에 GMP 파일 생성 하기
    def Make_GMP_File(self,save_gmp_path):
        GRMProject = Element("GRMProject")
        GRMProject.set("xmlns", "http://tempuri.org/GRMProject.xsd")
        ProjectSettings = SubElement(GRMProject, "ProjectSettings")
        SubElement(ProjectSettings, 'ProjectFile').text = save_gmp_path
        SubElement(ProjectSettings, 'GRMSimulationType').text = 'SingleEvent'
        SubElement(ProjectSettings, 'WatershedFile')
        SubElement(ProjectSettings, 'SlopeFile')
        SubElement(ProjectSettings, 'FlowDirectionFile')
        SubElement(ProjectSettings, 'FlowAccumFile')
        SubElement(ProjectSettings, 'StreamFile')
        SubElement(ProjectSettings, 'ChannelWidthFile')
        SubElement(ProjectSettings, 'InitialSoilSaturationRatioFile')
        SubElement(ProjectSettings, 'LandCoverDataType').text = 'File'
        SubElement(ProjectSettings, 'LandCoverFile')
        SubElement(ProjectSettings, 'LandCoverVATFile')
        SubElement(ProjectSettings, 'ConstantRoughnessCoeff')
        SubElement(ProjectSettings, 'ConstantImperviousRatio')
        SubElement(ProjectSettings, 'SoilTextureDataType').text = 'File'
        SubElement(ProjectSettings, 'SoilTextureFile')
        SubElement(ProjectSettings, 'SoilTextureVATFile')
        SubElement(ProjectSettings, 'ConstantSoilPorosity')
        SubElement(ProjectSettings, 'ConstantSoilEffPorosity')
        SubElement(ProjectSettings, 'ConstantSoilWettingFrontSuctionHead')
        SubElement(ProjectSettings, 'ConstantSoilHydraulicConductivity')
        SubElement(ProjectSettings, 'SoilDepthDataType').text = 'File'
        SubElement(ProjectSettings, 'SoilDepthFile')
        SubElement(ProjectSettings, 'SoilDepthVATFile')
        SubElement(ProjectSettings, 'ConstantSoilDepth')
        SubElement(ProjectSettings, 'InitialChannelFlowFile')
        SubElement(ProjectSettings, 'RainfallDataType').text = 'TextFileASCgrid'
        SubElement(ProjectSettings, 'RainfallInterval')
        SubElement(ProjectSettings, 'RainfallDataFile')
        SubElement(ProjectSettings, 'FlowDirectionType').text = 'StartsFromE_TauDEM'
        SubElement(ProjectSettings, 'GridCellSize')
        SubElement(ProjectSettings, 'IsParallel').text = 'true'
        SubElement(ProjectSettings, 'MaxDegreeOfParallelism').text = '-1'
        SubElement(ProjectSettings, 'SimulStartingTime').text = '0'
        SubElement(ProjectSettings, 'ComputationalTimeStep')
        SubElement(ProjectSettings, 'IsFixedTimeStep').text = 'false'
        SubElement(ProjectSettings, 'SimulationDuration')
        SubElement(ProjectSettings, 'OutputTimeStep')
        SubElement(ProjectSettings, 'SimulateInfiltration').text = 'true'
        SubElement(ProjectSettings, 'SimulateSubsurfaceFlow').text = 'true'
        SubElement(ProjectSettings, 'SimulateBaseFlow').text = 'true'
        SubElement(ProjectSettings, 'SimulateFlowControl').text = 'true'
        SubElement(ProjectSettings, 'CrossSectionType').text = 'CSSingle'
        SubElement(ProjectSettings, 'SingleCSChannelWidthType').text = 'CWGemeration'
        SubElement(ProjectSettings, 'ChannelWidthEQc').text = '1.698'
        SubElement(ProjectSettings, 'ChannelWidthEQd').text = '0.318'
        SubElement(ProjectSettings, 'ChannelWidthEQe').text = '0.5'
        SubElement(ProjectSettings, 'ChannelWidthMostDownStream')
        SubElement(ProjectSettings, 'LowerRegionHeight')
        SubElement(ProjectSettings, 'LowerRegionBaseWidth')
        SubElement(ProjectSettings, 'UpperRegionBaseWidth')
        SubElement(ProjectSettings, 'CompoundCSIniFlowDepth')
        SubElement(ProjectSettings, 'CompoundCSChannelWidthLimit')
        SubElement(ProjectSettings, 'BankSideSlopeRight').text = '1.5'
        SubElement(ProjectSettings, 'BankSideSlopeLeft').text = '1.5'
        SubElement(ProjectSettings, 'MakeIMGFile').text = 'false'
        SubElement(ProjectSettings, 'MakeASCFile').text = 'false'
        SubElement(ProjectSettings, 'MakeSoilSaturationDistFile').text = 'true'
        SubElement(ProjectSettings, 'MakeRfDistFile').text = 'true'
        SubElement(ProjectSettings, 'MakeRFaccDistFile').text = 'true'
        SubElement(ProjectSettings, 'MakeFlowDistFile').text = 'true'
        SubElement(ProjectSettings, 'PrintOption').text = 'All'
        SubElement(ProjectSettings, 'WriteLog').text = 'false'
        SubElement(ProjectSettings, 'AboutThisProject')
        SubElement(ProjectSettings, 'AboutWatershed')
        SubElement(ProjectSettings, 'AboutLandCoverMap')
        SubElement(ProjectSettings, 'AboutSoilMap')
        SubElement(ProjectSettings, 'AboutSoilDepthMap')
        SubElement(ProjectSettings, 'AboutRainfall')
        SubElement(ProjectSettings, 'ProjectSavedTime')
        SubElement(ProjectSettings, 'ComputerName')
        SubElement(ProjectSettings, 'ComputerUserName')
        SubElement(ProjectSettings, 'GRMVersion')
        ElementTree(GRMProject).write(save_gmp_path, encoding="utf-8", xml_declaration=True)


