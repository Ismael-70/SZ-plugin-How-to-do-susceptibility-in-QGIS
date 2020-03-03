# -*- coding: utf-8 -*-
"""
/***************************************************************************
 model
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
import numpy as np
from osgeo import gdal,osr
import sys
import math
import csv
from qgis.core import QgsMessageLog
import processing
import os
import ogr

class WoE:
    def iter(self):
        listcause=[]
        listclasses=[]
        if self.Wcause1==None:
            pass
        else:
            listcause.append(self.Wcause1)
            listclasses.append(self.classes1)
        if self.Wcause2==None:
            pass
        else:
            listcause.append(self.Wcause2)
            listclasses.append(self.classes2)
        if self.Wcause3==None:
            pass
        else:
            listcause.append(self.Wcause3)
            listclasses.append(self.classes3)
        if self.Wcause4==None:
            pass
        else:
            listcause.append(self.Wcause4)
            listclasses.append(self.classes4)
        for y in range(self.ii):
            if self.Wcauselista[y]==None:
                pass
            else:
                listcause.append(self.Wcauselista[y])
                listclasses.append(self.classeslista[y])
        #######################################################################
        countcause=len(listcause)######delete empty cause!!!!!!!!!!
        print(listclasses)
        print(listcause)
        if countcause==0:#verify empty row input
            QgsMessageLog.logMessage('Select at least one cause', tag="WoE")
            raise ValueError  # Select at least one cause, see 'WoE' Log Messages Panel
        ####################################translate dem and inventory
        self.newXNumPxl=(np.ceil(abs(self.xmax-self.xmin)/(self.w))-1).astype(int)
        self.newYNumPxl=(np.ceil(abs(self.ymax-self.ymin)/(self.h))-1).astype(int)
        self.xsize=self.newXNumPxl
        self.ysize=self.newYNumPxl
        self.shape=np.array([self.newXNumPxl,self.newYNumPxl])
        self.extent = "%s,%s,%s,%s" % (self.xmin, self.xmax, self.ymin, self.ymax)
        ##############
        self.origine=[self.xmin,self.ymax]
        #######################################inventory from shp to tif
        try:
            dem_datas=self.vector2array(self.inventory,self.w,self.h,self.xmin,self.ymin,self.xmax,self.ymax,self.xsize,self.ysize)
            # write the data to output file
            rf1='/tmp/inv.tif'
            dem_datas1=dem_datas#[::-1]
            w1=self.w
            h1=self.h*(-1)
            self.array2raster(rf1,w1,h1,dem_datas1,self.origine)##########rasterize inventory
            ##################################
            IN1a=rf1
            IN2a='/tmp/invq.tif'
            IN3a=self.fold + '/inventorynxn.tif'
            self.cut(IN1a,IN2a,IN3a)##########traslate inventory
            self.ds15=None
            self.ds15 = gdal.Open(IN3a)
            if self.ds15 is None:#####################verify empty row input
                QgsMessageLog.logMessage("ERROR: can't open raster input", tag="WoE")
                raise ValueError  # can't open raster input, see 'WoE' Log Messages Panel
            ap=self.ds15.GetRasterBand(1)
            NoData=ap.GetNoDataValue()
            invmatrix = np.array(ap.ReadAsArray()).astype('int16')
            bands = self.ds15.RasterCount
            if bands>1:#####################verify bands
                QgsMessageLog.logMessage("ERROR: input rasters shoud be 1-band raster", tag="WoE")
                raise ValueError  # input rasters shoud be 1-band raster, see 'WoE' Log Messages Panel
            #################################dem
        except:
            QgsMessageLog.logMessage("Failure to save sized inventory", tag="WoE")
            raise ValueError  # Failure to save sized inventory, see 'WoE' Log Messages Panel
        ###########################################load inventory
        self.catalog=np.array([])
        self.catalog=invmatrix
        #del valuess
        ###########cause
        for v in range(countcause):
            ds8=gdal.Open(listcause[v],0)
            ds8x = ds8.RasterXSize
            ds8y = ds8.RasterYSize
            gt= ds8.GetGeoTransform()
            causexl = round(gt[0],2)
            causeyt = round(gt[3],2)
            causexr = round(gt[0] + gt[1] * ds8x,2)
            causeyb = round(gt[3] + gt[5] * ds8y,2)
            QgsMessageLog.logMessage(self.extent, tag="WoE")
            if (causexl)>(self.xmin) or (causexr)<(self.xmax) or (causeyb)>(self.ymin) or (causeyt)<(self.ymax):
                QgsMessageLog.logMessage('Cause %s extension cannot satisfy selected extension'%v, tag="WoE")
                raise ValueError  # Cause extension cannot satisfy selected extension, see 'WoE' Log Messages Panel
            if self.w < abs(gt[1]) or self.h < abs(gt[5]):
                        QgsMessageLog.logMessage('Resolution requested is higher than Cause resolution', tag="WoE")
                        raise ValueError  # Resolution requested is higher than Cause resolution, see 'WoE' Log Messages Panel
            ds8=None
        ###################
        Causes={}
        id={}
        Mat={}
        self.Wfs={}
        for i in range(countcause):
            matrix=None
            self.Wcause=None
            self.classes=None
            self.Wcause=listcause[i]
            self.classes=listclasses[i]
            self.Wreclassed=None
            self.Wreclassed=self.fold+'/reclassedcause'+str(i)+'.tif'
            pathszcause=None
            pathszcause=self.fold+'/Wsizedcause'+str(i)+'.tif'
            self.ds2=None
            self.ds2 = gdal.Open(self.Wcause)
            if self.ds2 is None:#####################verify empty row input
                QgsMessageLog.logMessage("ERROR: can't open raster input", tag="WoE")
                raise ValueError  # can't open raster input, see 'WoE' Log Messages Panel
            gt=self.ds2.GetGeoTransform()
            ww=gt[1]
            hh=gt[5]
            a=self.ds2.GetRasterBand(1)
            NoData=a.GetNoDataValue()
            self.RasterInt = np.array(a.ReadAsArray()).astype('int64')
            self.matrix = np.array(a.ReadAsArray()).astype('float32')
            bands = self.ds2.RasterCount
            if bands>1:#####################verify bands
                QgsMessageLog.logMessage("ERROR: input rasters shoud be 1-band raster", tag="WoE")
                raise ValueError  # input rasters shoud be 1-band raster, see 'WoE' Log Messages Panel
            ################################################################
            self.classification()#############
            self.RasterInt1=self.RasterInt#[::-1]
            np.size(self.RasterInt1)
            self.array2raster(pathszcause,ww,hh,self.RasterInt1,self.origine)
            ###################
            IN2='/tmp/causeq'+str(i)+'.tif'
            IN1=pathszcause
            IN3=self.Wreclassed
            self.cut(IN1,IN2,IN3)##############################
            self.matrix=None
            self.RasterInt=None
            self.ds22=None
            self.ds22 = gdal.Open(self.Wreclassed)
            if self.ds22 is None:#####################verify empty row input
                QgsMessageLog.logMessage("ERROR: can't open raster input", tag="WoE")
                raise ValueError  # can't open raster input, see 'WoE' Log Messages Panel
            gt=self.ds22.GetGeoTransform()
            ww=gt[1]
            hh=gt[5]
            aa=self.ds22.GetRasterBand(1)
            NoData=aa.GetNoDataValue()
            self.RasterInt = np.array(aa.ReadAsArray()).astype('int64')
            self.matrix = np.array(aa.ReadAsArray()).astype('float32')
            bands = self.ds22.RasterCount
            if bands>1:#####################verify bands
                QgsMessageLog.logMessage("ERROR: input rasters shoud be 1-band raster", tag="WoE")
                raise ValueError  # input rasters shoud be 1-band raster, see 'WoE' Log Messages Panel
            ####################
            Causes[i]=self.RasterInt
            Mat[i]=self.matrix
            id[i]=np.where(self.RasterInt==-9999)
            ##################################-9999
            self.matrix=None
            self.RasterInt=None
            out_bandC=None
            dataC=None
        for causa in range(countcause):
            self.Raster=np.array([])
            self.Matrix=np.array([])
            self.txtout=None
            self.Weightedcause=None
            self.txtout=self.fold+'/Wftxt'+str(causa)+'.txt'
            self.Weightedcause=self.fold+'/weightedcause'+str(causa)+'.tif'
            self.ds10=None
            self.Raster=Causes[causa]
            self.Matrix=Mat[causa]
            for cc in range(countcause):
                self.Raster[id[cc]]=-9999
                self.Matrix[id[cc]]=-9999
            if self.method==0:
                self.WoE()#################
            elif self.method==1:
                self.FR()##############
            self.Wfs[causa]=self.weighted
            self.saveWf()##################
            self.weighted=np.array([])
        #del self.dem
        del self.catalog
        del Causes
        del Mat
        del id
        del self.Matrix
        del self.Raster

    def classification(self):###############classify causes according to txt classes
        Min={}
        Max={}
        clas={}
        with open(self.classes, 'r') as f:
            c = csv.reader(f,delimiter=' ')
            count=1
            for cond in c:
                b=np.array([])
                b=np.asarray(cond)
                Min[count]=b[0].astype(int)
                Max[count]=b[1].astype(int)
                clas[count]=b[2].astype(int)
                count+=1
        key_max=None
        key_min=None
        key_max = max(Max.keys(), key=(lambda k: Max[k]))
        key_min = min(Min.keys(), key=(lambda k: Min[k]))
        idx=np.where(np.isnan(self.RasterInt))
        self.matrix[idx]=-9999
        self.RasterInt[idx]=-9999
        self.matrix[(self.RasterInt<Min[key_min])]=-9999
        self.RasterInt[(self.RasterInt<Min[key_min])]=-9999
        self.matrix[(self.RasterInt>Max[key_max])]=-9999
        self.RasterInt[(self.RasterInt>Max[key_max])]=-9999
        for i in range(1,count):
            self.matrix[(self.RasterInt>=Min[i])&(self.RasterInt<=Max[i])]=clas[i]
            self.RasterInt[(self.RasterInt>=Min[i])&(self.RasterInt<=Max[i])]=clas[i].astype(int)

    def WoE(self):######################calculate W+,W-,Wf
        ################################################
        idx=[]
        idx1=[]
        idx2=[]
        idx3=[]
        idx=np.where(np.isnan(self.catalog))
        self.catalog[idx]=-9999
        ###############################################
        product=np.array([])
        diff=np.array([])
        product=(self.catalog*self.Raster)
        diff=(self.Raster-product)
        ######################################clean nan values
        idx2=np.where(self.catalog==-9999)
        product[idx2]=-9999
        diff[idx2]=-9999
        diff[idx3]=-9999
        product[self.Raster==-9999]=-9999
        diff[self.Raster==-9999]=-9999
        ############################################
        M=int(np.nanmax(self.Raster))
        countProduct = {}
        countDiff = {}
        for n in range(0,M+1):
            P=np.array([])
            D=np.array([])
            P=np.argwhere(product==float(n))
            PP=float(len(P))
            countProduct[n]=PP
            D=np.argwhere(diff==n)
            DD=float(len(D))
            countDiff[n]=DD
        self.weighted=np.array([])
        self.weighted=self.Matrix
        file = open(self.txtout,'w')#################save W+, W- and Wf
        for i in range(1,M+1):
            Npx1=None
            Npx2=None
            Npx3=None
            Npx4=None
            Wplus=None
            Wminus=None
            Wf=None
            var=[]
            if countProduct[i]==0 or countDiff[i]==0:
                Wf=0.
                Wplus=0.
                Wminus=0.
                Npx1='none'
                Npx2='none'
                Npx3='none'
                Npx4='none'
                var=[i,Npx1,Npx2,Npx3,Npx4,Wplus,Wminus,Wf]
                file.write('class,Npx1,Npx2,Npx3,Npx4,W+,W-,Wf: %s\n' %var)
                self.weighted[self.Raster == i] = 0.
            else:
                Npx1=float(countProduct[i])
                for ii in range(1,M+1):
                    try:
                        Npx2 += float(countProduct[ii])
                    except:
                        Npx2 = float(countProduct[ii])
                Npx2 -= float(countProduct[i])
                Npx3=float(countDiff[i])
                for iii in range(1,M+1):
                    try:
                        Npx4 += float(countDiff[iii])
                    except:
                        Npx4 = float(countDiff[iii])
                Npx4 -= float(countDiff[i])
                #W+ W-
                #Npx1,Npx2,Npx3,Npx4
                if Npx1==0 or Npx3==0:
                    Wplus=0.
                else:
                    Wplus=math.log((Npx1/(Npx1+Npx2))/(Npx3/(Npx3+Npx4)))
                if Npx2==0 or Npx4==0:
                    Wminus=0.
                else:
                    Wminus=math.log((Npx2/(Npx1+Npx2))/(Npx4/(Npx3+Npx4)))
                Wf=Wplus-Wminus
                var=[i,Npx1,Npx2,Npx3,Npx4,Wplus,Wminus,Wf]
                file.write('class,Npx1,Npx2,Npx3,Npx4,W+,W-,Wf: %s\n' %var)#################save W+, W- and Wf
                self.weighted[self.Raster == i] = Wf
        file.close()
        product=np.array([])
        diff=np.array([])

    def FR(self):######################calculate
        ################################################
        idx=[]
        idx1=[]
        idx2=[]
        idx3=[]
        idx=np.where(np.isnan(self.catalog))
        self.catalog[idx]=-9999
        ###############################################
        product=np.array([])
        clas=np.array([])
        product=(self.catalog*self.Raster)
        clas=self.Raster
        ######################################clean nan values
        idx2=np.where(self.catalog==-9999)
        product[idx2]=-9999
        clas[idx2]=-9999
        clas[idx3]=-9999
        product[self.Raster==-9999]=-9999
        clas[self.Raster==-9999]=-9999
        ############################################
        M=int(np.nanmax(self.Raster))
        countProduct = {}
        countClass = {}
        for n in range(0,M+1):#verificare se n parte da 0 oppure da 1. e quindi stabilire il valore minimo delle classi ?????????????????????????
            P=np.array([])
            D=np.array([])
            P=np.argwhere(product==float(n))
            PP=float(len(P))
            print(PP)
            countProduct[n]=PP
            D=np.argwhere(clas==n)
            DD=float(len(D))
            countClass[n]=DD
        self.weighted=np.array([])
        self.weighted=self.Matrix
        file = open(self.txtout,'w')#################save W+, W- and Wf
        for i in range(1,M+1):
            Npx1=None
            Npx2=None
            Npx3=None
            Npx4=None
            Wplus=None
            Wminus=None
            Wf=None
            var=[]
            if countClass[i]==0:#if the class is not present or the landslides are not present then FR=0
                Wf=0.
                Npx1='none'
                Npx2='none'
                Npx3='none'
                Npx4='none'
                #Wplus=0.
                #Wminus=0.
                var=[i,Npx1,Npx2,Npx3,Npx4,Wf]
                file.write('class,Npx1,Npx2,Npx3,Npx4,Wf: %s\n' %var)
                self.weighted[self.Raster == i] = 0.
            else:
                Npx1=float(countProduct[i])
                Npx2=float(countClass[i])
                for ii in range(1,M+1):
                    try:
                        Npx3 += float(countProduct[ii])
                    except:
                        Npx3 = float(countProduct[ii])
                for iii in range(1,M+1):
                    try:
                        Npx4 += float(countClass[iii])
                    except:
                        Npx4 = float(countClass[iii])
                #W+ W-
                #Npx1,Npx2,Npx3,Npx4
                if Npx1==0:
                    Wf=0.
                else:
                    Wf=(np.divide((np.divide(Npx1,Npx2)),(np.divide(Npx3,Npx4))))
                var=[i,Npx1,Npx2,Npx3,Npx4,Wf]
                file.write('class,Npx1,Npx2,Npx3,Npx4,Wf: %s\n' %var)#################save W+, W- and Wf
                self.weighted[self.Raster == i] = float(Wf)
        file.close()
        product=np.array([])
        clas=np.array([])

    def saveWf(self):
        try:
            out_data = None
            # read in data from first band of input raster
            cols = self.xsize
            rows = self.ysize
            self.weighted1=self.weighted#[::-1]
            w2=self.w
            h2=self.h*(-1)
            self.array2raster(self.Weightedcause,w2,h2,self.weighted1,self.origine)

        except:
            QgsMessageLog.logMessage("Failure to set nodata values on raster Wf", tag="WoE")
            raise ValueError  # Failure to set nodata values on raster Wf, see 'WoE' Log Messages Panel

    def sumWf(self):
        self.LSI=sum(self.Wfs.values())
        for iii in self.Wfs:
            idx=[]
            idx9=[]
            self.Wfs[iii]=self.Wfs[iii].astype(int)
            idx=np.where(np.isnan(self.Wfs[iii]))
            self.LSI[idx]=-9999
            self.LSI[self.LSI==-9999]=-9999
            idx9=np.where(self.Wfs[iii]==-9999)
            self.LSI[idx9]=-9999
        del self.Wfs

    def saveLSI(self):
        try:
            w3=self.w
            h3=self.h*(-1)
            self.array2raster(self.LSIout,w3,h3,self.LSI,self.origine)
        except:
            QgsMessageLog.logMessage("ERROR: Failure to set nodata values on raster LSI", tag="WoE")
            raise ValueError  # Failure to set nodata values on raster LSI, see 'WoE' Log Messages Panel

    def array2raster(self,newRasterfn,pixelWidth,pixelHeight,array,oo):
        cr=np.shape(array)
        cols=cr[1]
        rows=cr[0]
        originX = oo[0]
        originY = oo[1]
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(newRasterfn, int(cols), int(rows), 1, gdal.GDT_Float32)
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outband = outRaster.GetRasterBand(1)
        outband.SetNoDataValue(-9999)
        outband.WriteArray(array)
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(int(self.epsg[self.epsg.rfind(':')+1:]))
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()

    def cut(self,in1,in2,in3):
        if self.polynum==1:
            try:
                if os.path.isfile(in2):
                    os.remove(in2)

                os.system('gdal_translate -a_srs '+str(self.epsg)+' -of GTiff -ot Float32 -outsize ' + str(self.newXNumPxl) +' '+ str(self.newYNumPxl) +' -projwin ' +str(self.xmin)+' '+str(self.ymax)+' '+ str(self.xmax) + ' ' + str(self.ymin) + ' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 '+ in1 +' '+in2)

                print('gdal_translate -a_srs '+str(self.epsg)+' -of GTiff -ot Float32 -outsize ' + str(self.newXNumPxl) +' '+ str(self.newYNumPxl) +' -projwin ' +str(self.xmin)+' '+str(self.ymax)+' '+ str(self.xmax) + ' ' + str(self.ymin) + ' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 '+ in1 +' '+in2)
            except:
                QgsMessageLog.logMessage("Failure to save sized /tmp input", tag="WoE")
                raise ValueError  # Failure to save sized /tmp input Log Messages Panel
            try:
                if os.path.isfile(in3):
                    os.remove(in3)

                processing.run('gdal:cliprasterbymasklayer', {'INPUT': in2,'MASK': self.poly, 'NODATA': -9999, 'ALPHA_BAND': False, 'CROP_TO_CUTLINE': False, 'KEEP_RESOLUTION': True, 'MULTITHREADING': True, 'OPTIONS': '', 'DATA_TYPE': 6,'OUTPUT': in3})

            except:
                QgsMessageLog.logMessage("Failure to save clipped input", tag="WoE")
                raise ValueError  # Failure to save sized /tmp input Log Messages Panel
        else:
            try:
                if os.path.isfile(in3):
                    os.remove(in3)
                if os.path.isfile(in2):
                    os.remove(in2)

                os.system('gdalwarp -ot Float32 -q -of GTiff -t_srs '+str(self.epsg)+' -r bilinear '+ in1+' '+in2)

                print('gdalwarp -ot Float32 -q -of GTiff -t_srs '+str(self.epsg)+' -r bilinear '+ in1+' '+in2)

                os.system('gdal_translate -of GTiff -ot Float32 -outsize ' + str(self.newXNumPxl) +' '+ str(self.newYNumPxl) +' -projwin ' +str(self.xmin)+' '+str(self.ymax)+' '+ str(self.xmax) + ' ' + str(self.ymin) + ' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 ' + in2 +' '+in3)

                print('gdal_translate -of GTiff -ot Float32 -outsize ' + str(self.newXNumPxl) +' '+ str(self.newYNumPxl) +' -projwin ' +str(self.xmin)+' '+str(self.ymax)+' '+ str(self.xmax) + ' ' + str(self.ymin) + ' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 ' + in2 +' '+in3)

            except:
                QgsMessageLog.logMessage("Failure to save sized input", tag="WoE")
                raise ValueError  # Failure to save sized /tmp input sized Log Messages Panel


    def vector2array(self,inn,pxlw,pxlh,xm,ym,xM,yM,sizex,sizey):
        driverd = ogr.GetDriverByName('ESRI Shapefile')
        ds9 = driverd.Open(inn)
        layer = ds9.GetLayer()
        count=0
        for feature in layer:
            count+=1
            geom = feature.GetGeometryRef()
            xy=np.array([geom.GetX(),geom.GetY()])
            try:
                XY=np.vstack((XY,xy))
            except:
                XY=xy
        size=np.array([pxlw,pxlh])
        OS=np.array([xm,yM])
        NumPxl=(np.ceil(abs((XY-OS)/size)-1))#from 0 first cell
        valuess=np.zeros((sizey,sizex),dtype='int16')
        #print(XY)
        #print(NumPxl)
        #print(len(NumPxl))
        #print(count)
        try:
            for i in range(count):
                #print(i,'i')
                if XY[i,1]<yM and XY[i,1]>ym and XY[i,0]<xM and XY[i,0]>xm:
                    valuess[NumPxl[i,1].astype(int),NumPxl[i,0].astype(int)]=1
        except:#only 1 feature
            if XY[1]<yM and XY[1]>ym and XY[0]<xM and XY[0]>xm:
                valuess[NumPxl[1].astype(int),NumPxl[0].astype(int)]=1
        fuori = valuess.astype('float32')
        return fuori
