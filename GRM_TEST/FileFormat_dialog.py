# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FlatDialog
                                 A QGIS plugin
 Flat
                             -------------------
        begin                : 2017-04-26
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
from PyQt4 import QtGui, uic
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QFileInfo


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'FileFormat_dialog_base.ui'))


class FileFormat(QtGui.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(FileFormat, self).__init__(parent)

        self.setupUi(self)
        self.txtFileFormat.setEnabled(False)
        text = "data1\ndata2\ndata3\ndata4\ndata5\n.\n.\n.\n.\nNo characters are inclued.\nOnly numberic data vlue is listed for one column"
        self.txtFileFormat.setText(text)




