# -*- coding: utf-8 -*-
from math import ceil

from qgis.core import *
from qgis.gui import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
import utils
import numpy as np

def get_flow_layer(fd_layer,canvas,stream_layer):
    asc_file_fd = fd_layer.dataProvider().dataSourceUri()
    ascii_grid_fd = np.loadtxt(asc_file_fd, skiprows=6)  # skip 6 . caution!

    asc_file_st = stream_layer.dataProvider().dataSourceUri()
    ascii_grid_st = np.loadtxt(asc_file_st, skiprows=6)  # skip 6 . caution!

    xmin, ymin, xmax, ymax = fd_layer.extent().toRectF().getCoords()
    crs = fd_layer.crs().toWkt()
    point_layer = QgsVectorLayer('Point?crs=' + crs, 'Arrow', 'memory')
    point_provider = point_layer.dataProvider()

    resV = point_provider.addAttributes([QgsField("cellvalue", QVariant.Int)])
    resS = point_provider.addAttributes([QgsField("stream", QVariant.Int)])

    gridWidth = fd_layer.rasterUnitsPerPixelX()
    gridHeight = fd_layer.rasterUnitsPerPixelY()

    rows = ceil((ymax - ymin) / gridHeight)
    cols = ceil((xmax - xmin) / gridWidth)

    point_layer.startEditing()  # if omitted , setAttributes has no effect.

    strFDType='b'    #Reference : GRM Manual page 25 . 2018.3
    
    if strFDType == 'a':
        MyDirections = {1: 0, 2: 45, 4: 90, 8: 135, 16: 180, 32: 225, 64: 270, 128: 315}
    elif strFDType == 'b':
        MyDirections = {128: 0, 1: 45, 2: 90, 4: 135, 8: 180, 16: 225, 32: 270, 64: 315} 	#HyGIS(O)
    elif strFDType == 'c':
        MyDirections = {64: 0, 128: 45, 1: 90, 2: 135, 4: 180, 8: 225, 16: 270, 32: 315} 	#HyGIS(x). TOPAZ
    elif strFDType == 'd':
        MyDirections = {3: 0, 2: 45, 1: 90, 8: 135, 7: 180, 6: 225, 5: 270, 4: 315}	#TauDEM        
    else:
        print "FD Code is Wrong!"
        return 

    # strStylePath = "C:\GRM\sample\data\FD_Style_Template_v3.qml"  # We Will change the path to relative path
    strStylePath = os.path.dirname(os.path.realpath(__file__))
    strStylePath = strStylePath[:-6] + "DLL\FD_Style_Template_v3.qml"  # We Will change the path to relative path



    point_layer.loadNamedStyle(strStylePath)

    for i in range(int(cols)):
        for j in range(int(rows)):
            direction = get_direction(i, rows-j-1 , ascii_grid_fd,MyDirections)
            if not direction==None :
					ptCellCenter = QgsPoint(xmin+ i *gridWidth+gridWidth/2.0,ymin + j*gridHeight+gridHeight/2.0)
					feat = QgsFeature()
					feat.setGeometry(QgsGeometry().fromPoint(ptCellCenter))
					streamTag=0
					if ascii_grid_st[rows-j-1,i]>0 : streamTag=1
					feat.setAttributes([direction,streamTag])
					point_provider.addFeatures([feat])

    point_layer.commitChanges()

    # symbol_layer = QgsMarkerSymbolV2.createSimple({'name': 'arrow', 'color': 'blue', 'size': '15', 'size_unit': 'mm'})
    # symbol_layer.setDataDefinedAngle(QgsDataDefined("cellvalue"))
    # renderer = QgsSingleSymbolRendererV2(symbol_layer)
    # point_layer.setRendererV2(renderer)

    point_layer.updateExtents()

    point_layer.triggerRepaint()

    return point_layer

def get_direction(x, y, ascii_grid,directions):
    value = None
    try:
        value = ascii_grid[y][x]  # order is [y][x]. top to bottom, zero base
        direction = directions.get(value)
        return direction

    except IndexError:
        return "Intentional except"


