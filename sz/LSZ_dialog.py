# -*- coding: utf-8 -*-
"""
/***************************************************************************
 modelDialog
                                 A QGIS plugin
 Landslide Susceptibility Zoning
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-06-22
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Giacomo Titti CNR-IRPI
        email                : giacomotitti@gmail.com
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

from qgis.PyQt.QtCore import pyqtSlot,  Qt,  QUrl,  QFileInfo
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from qgis.core import *
from qgis.PyQt import uic
from qgis.PyQt import QtNetwork
from qgis.PyQt.QtGui import QIntValidator
from qgis.PyQt.QtWidgets import *
from qgis.utils import iface

import json
import os
import processing
import datetime
import tempfile
import math

from qgis.analysis import QgsZonalStatistics
from PyQt5 import QtGui, QtWidgets, uic, QtCore
from PyQt5.QtCore import pyqtSignal
from collections import OrderedDict

from qgis.core import Qgis, QgsFeedback, QgsGeometry, QgsWkbTypes, QgsRasterLayer, QgsProject, QgsVectorLayer, QgsRectangle, QgsCoordinateReferenceSystem,QgsExpressionContextUtils,QgsMapLayer
from qgis.gui import QgsFileWidget, QgsMapTool, QgsRubberBand, QgsProjectionSelectionWidget
from qgis.core import QgsProcessing

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterExtent
import processing
from qgis import gui

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'LSZ_dialog_base.ui'))

class modelDialog(QtWidgets.QDialog, FORM_CLASS):
    closingPlugin = pyqtSignal()
    def __init__(self, parent=None):
        """Constructor."""
        super(modelDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface

        self.comboExtentChoiche = comboExtent(self)
        self.comboExtentChoiche.setObjectName("extent_choice")
        self.gridLayout_2.addWidget(self.comboExtentChoiche, 43, 2, 1, 1)

        self.crsChoice = QgsProjectionSelectionWidget()
        self.crsChoice.setObjectName("crs_choice")
        self.gridLayout_2.addWidget(self.crsChoice, 59, 2, 1, 1)

        self.comboExtentChoiche.setCurrentIndex(0)
        self.crsChoice.setCrs(QgsCoordinateReferenceSystem('EPSG:3857'))

        self.ext=self.comboExtentChoiche.currentExtent()
        self.mMapLayerComboBox_2.setFilters(QgsMapLayerProxyModel.PointLayer)

        self.checkBox.setEnabled(True)
        self.checkBox.setChecked(True)
        self.mMapLayerComboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.checkBox.toggled.connect(self.mMapLayerComboBox.setEnabled)

        self.mMapLayerComboBox_4.setFilters(QgsMapLayerProxyModel.RasterLayer)

        self.checkBox_6.setEnabled(True)
        self.checkBox_6.setChecked(True)
        self.mMapLayerComboBox_6.setFilters(QgsMapLayerProxyModel.RasterLayer)

        self.checkBox_6.toggled.connect(self.mMapLayerComboBox_6.setEnabled)
        self.checkBox_6.toggled.connect(self.lineEdit_7.setEnabled)
        self.checkBox_6.toggled.connect(self.pushButton_7.setEnabled)

        self.checkBox_8.setEnabled(True)
        self.checkBox_8.setChecked(True)
        self.mMapLayerComboBox_8.setFilters(QgsMapLayerProxyModel.RasterLayer)

        self.checkBox_8.toggled.connect(self.mMapLayerComboBox_8.setEnabled)
        self.checkBox_8.toggled.connect(self.lineEdit_8.setEnabled)
        self.checkBox_8.toggled.connect(self.pushButton_8.setEnabled)

        self.checkBox_10.setEnabled(True)
        self.checkBox_10.setChecked(True)
        self.mMapLayerComboBox_10.setFilters(QgsMapLayerProxyModel.RasterLayer)

        self.checkBox_10.toggled.connect(self.mMapLayerComboBox_10.setEnabled)
        self.checkBox_10.toggled.connect(self.lineEdit_9.setEnabled)
        self.checkBox_10.toggled.connect(self.pushButton_9.setEnabled)

        self.checkBox_2.setEnabled(True)
        self.checkBox_2.setChecked(False)
        self.lineEdit_16.setEnabled(False)
        self.pushButton_12.setEnabled(False)
        self.checkBox_2.toggled.connect(self.lineEdit_16.setEnabled)
        self.checkBox_2.toggled.connect(self.pushButton_12.setEnabled)

class comboExtent(QtWidgets.QComboBox):

    def __init__(self, parentModule, parent=None):
        super(comboExtent, self).__init__(parent)
        self.iface = parentModule.iface
        self.contextMapTool = selectExtentMapTool(self)
        self.activated.connect(self.checkItem)
        self.addItem("CANVAS EXTENT",'C')

    def showPopup(self):
        self.clear()
        self.addItem("CANVAS EXTENT",'C')
        for id,layer in QgsProject.instance().mapLayers().items():
            self.addItem("%s [%s]" % (layer.name(),layer.crs().authid()), layer)
        super(comboExtent, self).showPopup()

    def currentExtent(self):
        if self.currentData() == 'S':
            return self.selectedExtent
        elif self.currentData() == 'C':
            return self.iface.mapCanvas().extent()
        else:
            return self.currentData().extent()

    def checkItem(self):
        self.contextMapTool.reset()
        if self.currentData() == 'S':
            self.iface.mapCanvas().setMapTool(self.contextMapTool)

class selectExtentMapTool(QgsMapTool):

    def __init__(self, parentObj):
        self.parentObj = parentObj
        self.iface = parentObj.iface
        QgsMapTool.__init__(self, self.iface.mapCanvas())
        self.contextShape = QgsRubberBand(self.iface.mapCanvas(),QgsWkbTypes.LineGeometry )
        self.contextShape.setWidth( 1 )
        self.contextShape.setColor(QtCore.Qt.red)
        self.pressed = False

    def canvasPressEvent(self, event):
        self.pressed = True
        self.pressx = event.pos().x()
        self.pressy = event.pos().y()
        self.movex = event.pos().x()
        self.movey = event.pos().y()
        self.PressedPoint = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(self.pressx, self.pressy)

    def canvasMoveEvent(self, event):
        if self.pressed:
            x = event.pos().x()
            y = event.pos().y()
            movedPoint = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(x, y)
            self.contextShape.reset()
            self.contextgeom = QgsGeometry.fromRect(QgsRectangle(self.PressedPoint,movedPoint)).convertToType(QgsWkbTypes.LineGeometry)
            self.contextShape.setToGeometry(self.contextgeom)

    def canvasReleaseEvent(self, event):
        if self.pressed:
            x = event.pos().x()
            y = event.pos().y()
            releasedPoint = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(x, y)
            self.pressed = False
            self.parentObj.selectedExtent = QgsRectangle(self.PressedPoint,releasedPoint)
            self.parentObj.iface.mapCanvas().setMapTool(None)

    def reset(self):
        self.contextShape.reset()
