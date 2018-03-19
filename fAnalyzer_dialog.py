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
# from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import *
from PyQt4.QtCore import QFileInfo
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView
import os
import Util
from PyQt4 import QtGui, uic
import sys, random
import numpy as np
# import pyqtgraph as pg



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'fAnalyzer.ui'))

_layerPath=""
_util = Util.util()
class FAnalyzerDialog(QtGui.QDialog, FORM_CLASS):
    plot1= None
    def __init__(self, parent=None):
        """Constructor."""
        super(FAnalyzerDialog, self).__init__(parent)
        self.setupUi(self)
        url = QUrl('http://hydroradar.hermesys.co.kr/info.html?sitecode=add&fid=basin_merge.14')
        self.webView.load(url)


        scene = QGraphicsScene()

        families = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        total = 0
        set_angle = 0
        count1 = 0
        colours = []
        total = sum(families)

        for count in range(len(families)):
            number = []
            for count in range(3):
                number.append(random.randrange(0, 255))
            colours.append(QColor(number[0], number[1], number[2]))

        for family in families:
            # Max span is 5760, so we have to calculate corresponding span angle
            angle = round(float(family * 5760) / total)
            ellipse = QGraphicsEllipseItem(0, 0, 400, 400)
            ellipse.setPos(0, 0)
            ellipse.setStartAngle(set_angle)
            ellipse.setSpanAngle(angle)
            ellipse.setBrush(colours[count1])
            set_angle += angle
            count1 += 1
            scene.addItem(ellipse)

        self.graphicsView.setScene(scene)
















