# -*- coding: utf-8 -*-

"""
/***************************************************************************
 classe
                                 A QGIS plugin
 susceptibility
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-07-01
        copyright            : (C) 2021 by Giacomo Titti
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

__author__ = 'Giacomo Titti'
__date__ = '2021-07-01'
__copyright__ = '(C) 2021 by Giacomo Titti'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon
#from .scripts.roc import rocAlgorithm
from .scripts.sz_train_WOE import WOEAlgorithm
from .scripts.sz_train_WOE_cv import WOEcvAlgorithm
from .scripts.sz_train_fr import FRAlgorithm
from .scripts.sz_train_fr_cv import FRcvAlgorithm
from .scripts.sz_train_LR import LRAlgorithm
from .scripts.sz_train_LR_cv import LRcvAlgorithm
from .scripts.sz_train_RF import RFAlgorithm
from .scripts.sz_train_RF_cv import RFcvAlgorithm
from .scripts.sz_train_DT import DTAlgorithm
from .scripts.sz_train_DT_cv import DTcvAlgorithm
from .scripts.sz_train_SVC import SVCAlgorithm
from .scripts.sz_train_SVC_cv import SVCcvAlgorithm
##from .scripts.polytogrid import polytogridAlgorithm
#from .scripts.pointtogrid import pointtogridAlgorithm
from .scripts.lsdanalysis import statistic
#from .scripts.class_counter import classAlgorithm
from .scripts.cleaning import cleankernelAlgorithm
from .scripts.graphs_lsdstats_kernel import statistickernel
from .scripts.randomsampler3 import samplerAlgorithm
from .scripts.stat31 import rasterstatkernelAlgorithm
#from .scripts.statmatrix2 import matrixAlgorithm
from .scripts.classvector import classvAlgorithm
from .scripts.classvectorw import classvAlgorithmW
from .scripts.classcovtxt import classcovtxtAlgorithm
from .scripts.classcovdeciles import classcovdecAlgorithm



class classeProvider(QgsProcessingProvider):

    def __init__(self):
        """
        Default constructor.
        """
        QgsProcessingProvider.__init__(self)

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """

        self.addAlgorithm(WOEAlgorithm())
        self.addAlgorithm(WOEcvAlgorithm())
        self.addAlgorithm(FRAlgorithm())
        self.addAlgorithm(FRcvAlgorithm())
        self.addAlgorithm(LRAlgorithm())
        self.addAlgorithm(LRcvAlgorithm())
        self.addAlgorithm(DTAlgorithm())
        self.addAlgorithm(DTcvAlgorithm())
        self.addAlgorithm(SVCAlgorithm())
        self.addAlgorithm(SVCcvAlgorithm())
        self.addAlgorithm(RFAlgorithm())
        self.addAlgorithm(RFcvAlgorithm())
        self.addAlgorithm(classcovtxtAlgorithm())
        self.addAlgorithm(classcovdecAlgorithm())
        ##self.addAlgorithm(polytogridAlgorithm())
        #self.addAlgorithm(pointtogridAlgorithm())
        self.addAlgorithm(statistic())

        #self.addAlgorithm(classAlgorithm())
        #self.addAlgorithm(rocAlgorithm())
        #self.addAlgorithm(matrixAlgorithm())

        self.addAlgorithm(cleankernelAlgorithm())
        self.addAlgorithm(statistickernel())
        self.addAlgorithm(samplerAlgorithm())
        self.addAlgorithm(rasterstatkernelAlgorithm())
        self.addAlgorithm(classvAlgorithm())
        self.addAlgorithm(classvAlgorithmW())

        # add additional algorithms here
        # self.addAlgorithm(MyOtherAlgorithm())

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'SZ'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('SZ')

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon('icon.svg')

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.name()
