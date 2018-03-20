# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GRM
                                 A QGIS plugin
 GRM Plugin
                             -------------------
        begin                : 2017-05-11
        copyright            : (C) 2017 by Hermesys
        email                : shpark@hermesys.co.kr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GRM class from file GRM.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .GRM_Plugin import GRM
    return GRM(iface)
