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
        if not os.path.isdir(self.outdir):
            os.makedirs(self.outdir)
        self.setVariables(demfilename)
        self.setPaths()

    def createDatasets(self, filelist):
        datasetlist = []
        for file in filelist:
            #create raster dataset
            datasetlist.append(self.driver.Create(file, self.xsize, self.ysize, 1, gdal.GDT_Float32))
            #set projection to match input dem
            datasetlist[-1].SetProjection(self.prj)
            #set geotransform to match input dem
            datasetlist[-1].SetGeoTransform(self.geot)
        return datasetlist

    def createIboundData(self):
        self.iboundData = []
        for i in range(0, len(self.iboundds)):
            ibound = np.zeros(self.wseData[i].shape, dtype = np.int32)
            ibound[self.wseData[i] > self.zbot] = 1
            ibound[self.headData[i] > 0.0] = -1
            ibound[self.wseData[i] < 0.0] = 0
            self.iboundData.append(ibound)
            self.iboundds[i].GetRasterBand(1).WriteArray(ibound)

    def createMODFLOWDatasets(self):
        #create starting head datasets
        self.sheadds = self.createDatasets(self.sheadPaths)
        #create ending head datasets
        self.eheadds = self.createDatasets(self.eheadPaths)
        #create ibound datasets
        self.iboundds = self.createDatasets(self.iboundPaths)

    def createStartingHeadData(self):
        self.sheadData = []
        for i in range(0, len(self.sheadds)):
            self.headData[i][self.headData[i] <np.nanmin(self.wseData[i])] = self.stats[0]
            data = np.where(self.headData[i] < self.stats[0], self.wseData[i], self.headData[i])
            self.sheadds[i].GetRasterBand(1).WriteArray(data)
            self.sheadds[i].GetRasterBand(1).FlushCache()
            self.sheadData.append(data)
            self.sheadds[i] = None

    def loadData(self, filelist):
        datalist = []
        for file in filelist:
            ds = gdal.Open(file)
            datalist.append(ds.GetRasterBand(1).ReadAsArray())
            ds = None
        return datalist

    def loadBDSWEAData(self):
        # initial DEM and water surface elevation from BDSWEA
        self.wseData = self.loadData(self.wsePaths)
        #set bottom of the model domain
        self.zbot = self.wseData[0] - 10.0
        # head data from BDSWEA
        self.headData = self.loadData(self.headPaths)
        # pond depths from BDSWEA
        self.pondData = self.loadData(self.pondPaths)

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
        self.stats = demds.GetRasterBand(1).GetStatistics(0, 1)
        demds = None
        nlay = 1
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
            self.eheadPaths.append(self.outdir + "/ehead_" + name + ".tif")
        #files for starting head
        self.sheadPaths = []
        for name in self.mfnames:
            self.sheadPaths.append(self.outdir + "/shead_" + name + ".tif")

    def setIBoundPaths(self):
        self.iboundPaths = []
        for name in self.mfnames:
            self.iboundPaths.append(self.outdir + "/ibound_" + name + ".tif")

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
        self.loadBDSWEAData()
        self.createMODFLOWDatasets()
        self.createIboundData()
        self.createStartingHeadData()
