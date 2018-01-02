import flopy
import flopy.utils.binaryfile as bf
import os
import numpy as np
from osgeo import gdal
import csv
from scipy import ndimage

class BDflopy:
    def __init__(self, modflowexe, outdir, maindir, outcsv = None, batch = False):
        self.modflowexe = modflowexe
        self.outdir = outdir
        self.maindir = maindir
        self.batch = batch
        self.setVariables(outcsv)

    def setVariables(self, outcsv):
        self.setCSVpath(outcsv)
        self.mf = []
        self.mfnames = ["start", "lo", "mid", "hi"]
        for mfname in self.mfnames:
            self.mf.append(flopy.modflow.Modflow(mfname, exe_name = self.modflowexe))

    def setCSVpath(self, outcsv):
        if outcsv == None:
            self.outcsv = self.outdir + "/summary.csv"
        else:
            self.outcsv = outcsv

    def setPaths(self, startWSE):
        self.indir = self.maindir + "/02_rasIn"
        self.modeldir = self.maindir + "03_out"
        demPaths = []

    def setPathsBatch(self):

    def run(self):


    def runBatch(self):
