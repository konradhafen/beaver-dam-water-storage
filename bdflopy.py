import flopy
import flopy.utils.binaryfile as bf
import os
import numpy as np
from osgeo import gdal
import csv
from scipy import ndimage

class BDflopy:
    def __init__(self, modflowexe, indir, modeldir, outdir, demfilename):
        self.modflowexe = modflowexe
        self.indir = indir
        self.modeldir = modeldir
        self.outdir = outdir
        self.setVariables()
        self.setPaths()

    def loadData(self):
        self.wseData = []
        for file in self.wsePaths:
            ds = gdal.Open(file)
            self.wseData.append(ds.GetRasterBand(1).ReadAsArray())
        #head data from BDSWEA
        self.headData = []
        for file in self.headPaths:
            ds = gdal.Open(file)
            self.headData.append(ds.GetRasterBand(1).ReadAsArray())
        #pond depths from BDSWEA
        self.pondData = []
        for file in self.pondPaths:
            ds = gdal.Open(file)
            self.pondData.append(ds.GetRasterBand(1).ReadAsArray())

    def createDatasets(self):

    def setPaths(self):
        self.setWSEPaths()
        self.setPondDepthPaths()
        self.setHeadPaths()
        self.setIBoundPaths()

    def setVariables(self, demfilename):
        self.driver = gdal.GetDriverByName('GTiff')
        self.dempath = self.indir + "/" + demfilename
        demds = gdal.Open(self.dempath)
        self.geot = demds.GetGeoTransform()
        self.prj = demds.GetProjection()
        self.xsize = demds.RasterXSize
        self.ysize = demds.RasterYSize
        demds = None
        self.mf = []
        self.mfnames = ["start", "lo", "mid", "hi"]
        for mfname in self.mfnames:
            self.mf.append(flopy.modflow.Modflow(mfname, exe_name = self.modflowexe))

    def setHeadPaths(self):
        #head files from BDSWEA
        self.headPaths = []
        for name in self.mfnames:
            self.headPaths.append(self.modeldir + "/head_" + name + ".tif")
        #files for ending/modeled head
        self.eheadPaths = []
        for name in self.mfnames:
            self.headPaths.append(self.modeldir + "/ehead_" + name + ".tif")
        #files for starting head
        self.sheadPaths = []
        for name in self.mfnames:
            self.headPaths.append(self.modeldir + "/shead_" + name + ".tif")

    def setIBoundPaths(self):
        self.iboundPaths = []
        for name in self.mfnames:
            self.headPaths.append(self.modeldir + "/ibound_" + name + ".tif")

    def setPondDepthPaths(self):
        self.pondPaths = []
        self.pondPaths.append(self.modeldir + "/depLo.tif")
        self.pondPaths.append(self.modeldir + "/depMid.tif")
        self.pondPaths.append(self.modeldir + "/depHi.tif")

    def setWSEPaths(self):
        self.wsePaths = []
        self.wsePaths.append(self.dempath)
        self.wsePaths.append(self.modeldir + "/WSESurf_lo.tif")
        self.wsePaths.append(self.modeldir + "/WSESurf_mid.tif")
        self.wsePaths.append(self.modeldir + "/WSESurf_hi.tif")

    def run(self):




