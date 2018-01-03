import flopy
import flopy.utils.binaryfile as bf
import os
import numpy as np
from osgeo import gdal
import csv
from scipy import ndimage

class BDflopy:
    def __init__(self, modflowexe, indir, modeldir, outdir, demfilename):
        """
        Initialize BDflopy class
        :param modflowexe: Path to MODFLOW executable file.
        :param indir: Path to directory of raster inputs for BDSWEA.
        :param modeldir: Path to directory of outputs from BDSWEA.
        :param outdir: Path to directory where output files will be genearted.
        :param demfilename: Name of DEM file in the input directory (e.g. 'dem.tif')
        """
        self.modflowexe = modflowexe
        self.indir = indir
        self.modeldir = modeldir
        self.outdir = outdir
        if not os.path.isdir(self.outdir):
            os.makedirs(self.outdir)
        self.setVariables(demfilename)
        self.setPaths()

    def createDatasets(self, filelist):
        """
        Create GDAL raster datasets
        :param filelist: List of paths where raster datasets will be created.
        :return: List of GDAL datasets
        """
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
        """
        Create ibound arrays for MODFLOW parameterization
        :return: None
        """
        self.iboundData = []
        for i in range(0, len(self.iboundds)):
            ibound = np.zeros(self.wseData[i].shape, dtype = np.int32)
            ibound[self.wseData[i] > self.zbot] = 1
            ibound[self.headData[i] > 0.0] = -1
            ibound[self.wseData[i] < 0.0] = 0
            self.iboundData.append(ibound)
            self.iboundds[i].GetRasterBand(1).WriteArray(ibound)

    def createModflowDatasets(self):
        """
        Create GDAL raster datasets for MODFLOW inputs and outputs
        :return: None
        """
        #create starting head datasets
        self.sheadds = self.createDatasets(self.sheadPaths)
        #create ending head datasets
        self.eheadds = self.createDatasets(self.eheadPaths)
        #create ibound datasets
        self.iboundds = self.createDatasets(self.iboundPaths)

    def createStartingHeadData(self):
        """
        Calculate starting head arrays
        :return: None
        """
        self.sheadData = []
        for i in range(0, len(self.sheadds)):
            self.headData[i][self.headData[i] <np.nanmin(self.wseData[i])] = self.stats[0]
            data = np.where(self.headData[i] < self.stats[0], self.wseData[i], self.headData[i])
            self.sheadds[i].GetRasterBand(1).WriteArray(data)
            self.sheadds[i].GetRasterBand(1).FlushCache()
            self.sheadData.append(data)
            self.sheadds[i] = None

    def loadData(self, filelist):
        """
        Read data from input rasters as numpy arrays
        :param filelist: List of raster files to read as numpy arrays.
        :return: List of numpy arrays
        """
        datalist = []
        for file in filelist:
            ds = gdal.Open(file)
            datalist.append(ds.GetRasterBand(1).ReadAsArray())
            ds = None
        return datalist

    def loadBdsweaData(self):
        """
        Load data from BDSWEA
        :return: None
        """
        # initial DEM and water surface elevation from BDSWEA
        self.wseData = self.loadData(self.wsePaths)
        #set bottom of the model domain
        self.zbot = self.wseData[0] - 10.0
        # head data from BDSWEA
        self.headData = self.loadData(self.headPaths)
        # pond depths from BDSWEA
        self.pondData = self.loadData(self.pondPaths)

    def setPaths(self):
        """
        Set file paths for input and output data
        :return: None
        """
        self.setWsePaths()
        self.setPondDepthPaths()
        self.setHeadPaths()
        self.setIBoundPaths()

    def setLpfVariables(self, hksat, vksat, por, kconv):
        """
        Set variables required for MODFLOW LPF package
        :param khsat: Horizontal hydraulic conductivity.
        :param kvsat: Vertical hydraulic conductivity.
        :param por: Porosity.
        :param kconv: Factor to convert hksat and vksat to meters per second.
        :return: None
        """
        self.hksat = hksat*kconv
        self.vksat = vksat*kconv
        self.por = por

    def setVariables(self, demfilename):
        """
        Set class variables
        :param demfilename: Name of DEM raster file.
        :return: None
        """
        self.driver = gdal.GetDriverByName('GTiff')
        self.dempath = self.indir + "/" + demfilename
        demds = gdal.Open(self.dempath)
        self.geot = demds.GetGeoTransform()
        self.prj = demds.GetProjection()
        self.xsize = demds.RasterXSize
        self.ysize = demds.RasterYSize
        self.stats = demds.GetRasterBand(1).GetStatistics(0, 1)
        demds = None
        self.nlay = 1
        self.mf = []
        self.mfnames = ["start", "lo", "mid", "hi"]
        for mfname in self.mfnames:
            self.mf.append(flopy.modflow.Modflow(mfname, exe_name = self.modflowexe))

    def setHeadPaths(self):
        """
        Set file names for head data to be read and written
        :return: None
        """
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
        """
        Set file names for output ibound rasters
        :return: None
        """
        self.iboundPaths = []
        for name in self.mfnames:
            self.iboundPaths.append(self.outdir + "/ibound_" + name + ".tif")

    def setPondDepthPaths(self):
        """
        Set file paths for pond depth rasters created by BDSWEA
        :return: None
        """
        self.pondPaths = []
        self.pondPaths.append(self.modeldir + "/depLo.tif")
        self.pondPaths.append(self.modeldir + "/depMid.tif")
        self.pondPaths.append(self.modeldir + "/depHi.tif")

    def setWsePaths(self):
        """
        Set file paths for water surface elevation rasters created by BDSWEA
        :return: None
        """
        self.wsePaths = []
        self.wsePaths.append(self.dempath)
        self.wsePaths.append(self.modeldir + "/WSESurf_lo.tif")
        self.wsePaths.append(self.modeldir + "/WSESurf_mid.tif")
        self.wsePaths.append(self.modeldir + "/WSESurf_hi.tif")

    def writeModflowInput(self):
        """
        Add MODFLOW packages and write input files for baseline, low dam height, median dam height, and high dam height scenarios
        :return: None
        """
        os.chdir(self.outdir)
        for i in range(0, len(self.mf)):
            flopy.modflow.ModflowDis(self.mf[i], self.nlay, self.ysize, self.xsize, delr = self.geot[1],
                                     delc = abs(self.geot[5]), top = self.wseData[i], botm = self.zbot,
                                     itmuni = 1, lenuni = 2)
            flopy.modflow.ModflowBas(self.mf[i], ibound = self.iboundData[i], strt = self.sheadData[i])
            flopy.modflow.ModflowLpf(self.mf[i], hk = self.hksat, vka = self.vksat)
            flopy.modflow.ModflowOc(self.mf[i])
            flopy.modflow.ModflowPcg(self.mf[i])
            self.mf[i].write_input()
            print self.mfnames[i] + " input written"

    def runModflow(self):
        """
        Run MODFLOW for baseline, low dam height, median dam height, and high dam height scenarios
        :return: None
        """
        for i in range(0, len(self.mf)):
            success, buff = self.mf[i].run_model()
            print self.mfnames[i] + " model done"

    def run(self, hksat, vksat, por = 1.0, kconv = 1.0):
        """
        Run MODFLOW to calculate water surface elevation changes from beaver dam construction
        :param hksat: Horizontal saturated hydraulic conductivity value(s). Single value or numpy array concurrent with input DEM.
        :param vksat: Vertical saturated hydraulic conductivity value(s). Single value or numpy array concurrent with input DEM.
        :param por: Porosity value(s). Single value or numpy array concurrent with input DEM. Default = 1.0.
        :param kconv: Factor to convert khsat and kvsat to meters per second. Default = 1.0.
        :return: None
        """
        self.setLpfVariables(hksat, vksat, por, kconv)
        self.loadBdsweaData()
        self.createModflowDatasets()
        self.createIboundData()
        self.createStartingHeadData()
        self.writeModflowInput()
        self.runModflow()
