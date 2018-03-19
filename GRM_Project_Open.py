#-*- coding: utf-8 -*-
'''
작성자: 화상 쪼민혜 작성
작성일:2017/08/31

'''
# 프로젝트 파일 오픈시에 각각의 값을 변수에 셋팅하여 사용 하기
import GRM_GetSet as set
import Util
import ElementTree as ET

_Set =set.ProjectSettings()
_Util =Util.util()

class ProjectSettings():
    def __init__(self,projectfile):
        self.ParsingMXL(projectfile)

    def ParsingMXL(self,filepath):
        doc = ET.parse(filepath)
        root = doc.getroot()
        nsmap = {'': 'http://tempuri.org/GRMProject.xsd'}
        for element in root.findall('ProjectSettings', namespaces=nsmap):
            test=element.findtext('SoilDepthVATFile', namespaces=nsmap)
            _Set.BankSideSlopeLeft_set(test)
            _Util.MessageboxShowInfo("test", test)










    
    
    
    
