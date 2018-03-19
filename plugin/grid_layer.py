# -*- coding: utf-8 -*-
from math import ceil

from qgis.core import *
from qgis.gui import *
from PyQt4.QtGui import *

def get_point_layer(map_layer, canvas):

    xmin, ymin, xmax, ymax = map_layer.extent().toRectF().getCoords()
    crs = map_layer.crs().toWkt()
    point_layer = QgsVectorLayer('Polygon?crs=' + crs, 'pixels', 'memory')
    point_provider = point_layer.dataProvider()

    gridWidth =map_layer.rasterUnitsPerPixelX()       #2017.11.1 원영진 수정
    gridHeight = map_layer.rasterUnitsPerPixelY()     #2017.11.1 원영진 수정

    rows = ceil((ymax-ymin)/gridHeight)
    cols = ceil((xmax-xmin)/gridWidth)
    ringXleftOrigin = xmin
    ringXrightOrigin = xmin + gridWidth
    ringYtopOrigin = ymax
    ringYbottomOrigin = ymax-gridHeight
    for i in range(int(cols)):
        ringYtop = ringYtopOrigin
        ringYbottom =ringYbottomOrigin
        for j in range(int(rows)):
            poly = [QgsPoint(ringXleftOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYtop)] 
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry().fromPolygon([poly]))
            point_provider.addFeatures([feat])
            point_layer.updateExtents()

            ringYtop = ringYtop - gridHeight
            ringYbottom = ringYbottom - gridHeight
        ringXleftOrigin = ringXleftOrigin + gridWidth
        ringXrightOrigin = ringXrightOrigin + gridWidth


    myRenderer = point_layer.rendererV2()
    if point_layer.geometryType() == QGis.Polygon:
        # mySymbol1 = QgsFillSymbolV2.createSimple({'color':'255,0,0,0'})

        # 2017-12-07 박 두께 및 색상 변경
        properties = {'color': '255,0,0,0','width_border': '0.09' , 'color_border': '0,0,0,127'}
        mySymbol1 = QgsFillSymbolV2.createSimple(properties)

    myRenderer.setSymbol(mySymbol1)
    point_layer.triggerRepaint()

    return point_layer