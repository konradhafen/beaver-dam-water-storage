from osgeo import gdal, ogr
import numpy as np
import math

class BDLoG:
    def __init__(self, brat, dem , fac, outDir, bratCap, stat = None):
        self.bratPath = brat
        self.demPath = dem
        self.facPath = fac
        self.outDir = outDir
        self.bratCap = bratCap
        self.statPath = stat

    def setVariables(self):
        self.driverShp = ogr.GetDriverByName("Esri Shapefile")
        self.bratDS = ogr.Open(self.bratPath, 1)
        self.bratLyr = self.bratDS.GetLayer()
        self.nFeat = self.bratLyr.GetFeatureCount()
        self.demDS = gdal.Open(self.demPath)
        self.dem = self.demDS.GetRasterBand(1).ReadAsArray()
        self.facDS = gdal.Open(self.facPath)
        self.fac = self.facDS.GetRasterBand(1).ReadAsArray()
        self.geot = self.demDS.GetGeoTransform()
        self.outDS = self.driverShp.CreateDataSource(self.outDir + "/ModeledDamPoints.shp")
        self.outLyr = self.outDS.CreateLayer("ModeledDamPoints",  self.bratLyr.GetSpatialRef(), geom_type=ogr.wkbPoint)
        self.capRank = np.empty([self.nFeat,3])

    def createFields(self):
        field = ogr.FieldDefn("brat_ID", ogr.OFTInteger)
        self.outLyr.CreateField(field)
        field.SetName("endx")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("endy")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("az_us")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("g_elev")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("slope")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_max")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("damType")
        field.SetType(ogr.OFTString)
        self.outLyr.CreateField(field)
        field.SetName("ht_lo")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_mid")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_hi")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_lo_mod")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_mid_mod")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_hi_mod")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("area_lo")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("area_mid")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("area_hi")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_lo")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_mid")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_hi")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_lo_lp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_mid_lp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_hi_lp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_lo_mp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_mid_mp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_hi_mp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_lo_up")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_mid_up")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_hi_up")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("diff_lo")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("diff_mid")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("diff_hi")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("type")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)

    def setBratFields(self):
        if self.bratLyr.FindFieldIndex("totdams", 1) >= 0:
            self.bratLyr.DeleteField(self.bratLyr.FindFieldIndex("totdams", 1))
        if self.bratLyr.FindFieldIndex("totcomp", 1) >= 0:
            self.bratLyr.DeleteField(self.bratLyr.FindFieldIndex("totcomp", 1))
        field = ogr.FieldDefn("totdams", ogr.OFTInteger)
        self.bratLyr.CreateField(field)
        field = ogr.FieldDefn("totcomp", ogr.OFTInteger)
        self.bratLyr.CreateField(field)

    def sortByCapacity(self):
        for i in range(0, self.nFeat):
            feature = self.bratLyr.GetFeature(i)
            cap = feature.GetFieldAsDouble("oCC_EX")
            geom = feature.GetGeometryRef()
            #self.capRank holds 3 variables: FID, BRAT capacity (dams/km), and number of dams to be modeled for scenario(capacity scenario * BRAT capacity)
            self.capRank[i,0] = feature.GetFID()
            self.capRank[i,1] = cap
            self.capRank[i,2] = math.ceil(geom.Length() * (cap/1000.0))
        self.capRank = self.capRank[self.capRank[:,1].argsort()[::-1]]
        self.modCap = math.ceil(self.bratCap * np.sum(self.capRank[:,2]))

    def calculateDamsPerReach(self):
        self.setBratFields()
        go = True
        totalDams = 0

        while go:
            i = 0
            while i < self.nFeat and go:
                bratFeat = self.bratLyr.GetFeature(self.capRank[i,0])
                exDams = bratFeat.GetFieldAsInteger("totdams")
                exComp = bratFeat.GetFieldAsInteger("totcomp")

                #number of dams for BRAT segment randomly selected from empricial complex size distribution
                damCount = math.ceil(np.random.lognormal(1.5515, 0.724))
                if damCount > 0:
                    if damCount > self.capRank[i,2]:
                        damCount = self.capRank[i,2]
                    if (totalDams + damCount) > self.modCap:
                        damCount = math.ceil(self.modCap - totalDams)
                    bratFeat.SetField("totdams", exDams + damCount)
                    if damCount > 0:
                        bratFeat.SetField("totcomp", exComp + 1)
                    self.bratLyr.SetFeature(bratFeat)
                totalDams += damCount
                i += 1

                if totalDams >= math.ceil(self.modCap):
                    go = False

    def createDams(self):
        #place dams on brat lines
        i = 0
        while i < self.nFeat:
            bratFt = self.bratLyr.GetFeature(self.capRank[i, 0])
            bratLine = bratFt.GetGeometryRef()
            length = bratLine.Length()
            #read number of dams and dam complexes from shapefile field
            nDamCt = bratFt.GetFieldAsInteger("totdams")
            nCompCt = bratFt.GetFieldAsInteger("totcomp")
            spacing = 0.0
            if nDamCt > 0:
                spacing = length / (nDamCt * 1.0)

            #create a point for each dam to be modeled
            nDamRm = nDamCt
            nCompRm = nCompCt
            for j in range(0, nDamCt):
                #determine if dam is primary or secondary and create height distribution
                damFeat = ogr.Feature(self.outLyr.GetLayerDefn())
                rnum = np.random.random()
                if rnum < ((nCompRm*1.0)/(nDamRm*1.0)) or nDamCt == 1:
                    htDist = np.random.lognormal(0.22, 0.36, 30)
                    damType = "primary"
                    nCompRm -= 1
                else:
                    htDist = np.random.lognormal(-0.21, 0.39, 30)
                    damType = "secondary"

                nDamRm -= 1
                #location of dam on stream segment
                pointDist = length - (spacing * (j * 1.0))
                damPoint = bratLine.Value(pointDist)
                #set any field values here
                damFeat = self.setDamFieldValues(damFeat, damType)
                #set dam heights
                damFeat = self.setDamHeights(damFeat, np.percentile(htDist, 2.5), np.median(htDist), np.percentile(htDist, 97.5))
                damFeat.SetGeometry(damPoint)
                self.outLyr.CreateFeature(damFeat)
                damFeat = None

            i += 1
            bratFt = None

    def getCellAddressOfPoint(self, x, y):
        col = math.floor((x - self.geot[0]) / self.geot[1])
        row = math.floor((self.geot[3] - y) / abs(self.geot[5]))
        address = np.array([row, col])
        return address

    def getCoordinatesOfCellAddress(self, row, col):
        x = self.geot[0] + (col * self.geot[1]) + (0.5 * self.geot[1])
        y = self.geot[3] + (row * self.geot[5]) + (0.5 * self.geot[5])
        coords = np.array([x, y])
        return coords

    def getStreamCellAddresses(self):
        # example fac layer, where 1 indicates stream cell
        # fac = np.array([[0, 0, 1, 0, 0],
        #                 [0, 0, 1, 0, 0],
        #                 [0, 0, 1, 0, 0],
        #                 [0, 0, 1, 0, 0],
        #                 [0, 0, 1, 0, 0]]
        #                )
        # get list of all stream cells will be a 2 row by X column array
        # streamcells = np.where(fac > 0)
        # swap axes so it becomes a X row by 2 column array with columns being row and column of cell address
        # streamlist = np.swapaxes(streamcells, 0, 1)

        fac = self.facDS.GetRasterBand(1).ReadAsArray()
        streamcells = np.swapaxes(np.where(fac > 0), 0, 1)
        return streamcells

    def moveDamsToFAC(self):
        streamcells = self.getStreamCellAddresses()
        nDams = self.outLyr.GetFeatureCount()
        i=0

        while i < nDams:
            print str(i) + " of " + str(nDams)
            damFt = self.outLyr.GetFeature(i)
            damPt = damFt.GetGeometryRef()
            damAddress = self.getCellAddressOfPoint(damPt.GetX(), damPt.GetY())
            #distance from stream cells to dam point
            dist = np.sum((streamcells - damAddress)**2, axis = 1)
            #index of closest stream cell
            #
            #Maybe put in a check so if distance is too far it deletes the dam
            #
            index = np.where(dist == min(dist))
            #change cell address of dam to closest stream cell
            damAddress = streamcells[index[0][0]]
            #delete stream cell so each dam is located in a different cell
            streamcells = np.delete(streamcells, index, axis = 0)
            damCoords = self.getCoordinatesOfCellAddress(damAddress[0], damAddress[1])
            # damPt.SetX(damCoords[0])
            # damPt.SetY(damCoords[1])
            ptwkt = "POINT(%f %f)" %  (damCoords[0], damCoords[1])
            damPt = ogr.CreateGeometryFromWkt(ptwkt)
            #damPt.AddPoint(damCoords[0], damCoords[1])
            damFt.SetGeometryDirectly(damPt)
            self.outLyr.SetFeature(damFt)
            i += 1

    def setDamFieldValues(self, feat, damType):
        feat.SetField("damType", damType)
        return feat

    def setDamHeights(self, feat, low, mid, high):
        feat.SetField("ht_lo", low)
        feat.SetField("ht_mid", mid)
        feat.SetField("ht_hi", high)
        feat.SetField("ht_lo_mod", low)
        feat.SetField("ht_mid_mod", mid)
        feat.SetField("ht_hi_mod", high)
        #feat.SetField("ht_max", max)
        return feat

    def generateDamLocationsFromBRAT(self):
        self.setVariables()
        self.createFields()
        self.sortByCapacity()
        self.calculateDamsPerReach()
        self.createDams()
        self.moveDamsToFAC()

    def close(self):
        self.bratDS = None
        self.bratLyr = None
        self.demDS = None
        self.facDS = None
        self.outDS = None
        self.outLyr = None

class BDSWEA:
    def __init__(self, dem, fdir, id, outDir, modPoints):
        self.outDir = outDir
        self.setConstants()
        self.setVars(dem, fdir, id, modPoints)
        self.createOutputArrays()

    def setConstants(self):
        self.FLOW_DIR_ESRI = np.array([32, 64, 128, 16, 0, 1, 8, 4, 2])
        self.FLOW_DIR_TAUDEM = np.array([4, 3, 2, 5, 0, 1, 6, 7, 8])
        self.ROW_OFFSET = np.array([-1, -1, -1, 0, 0, 0, 1, 1, 1])
        self.COL_OFFSET = np.array([-1, 0, 1, -1, 0, 1, -1, 0, 1])
        self.MAX_POND_AREA = 2000000 #in square meters
        self.MAX_HEIGHT = 5.0 #in meters

    def setVars(self, dem, fdir, id, shp):
        self.count = 0
        self.demDS = gdal.Open(dem)
        self.dem = self.demDS.GetRasterBand(1).ReadAsArray()
        self.fdirDS = gdal.Open(fdir)
        self.fdir = self.fdirDS.GetRasterBand(1).ReadAsArray()
        self.idDS = gdal.Open(id)
        self.id = self.idDS.GetRasterBand(1).ReadAsArray()
        self.pointDS = ogr.Open(shp)
        self.points = self.pointDS.GetLayer()
        self.nPoints = self.points.GetFeatureCount
        self.geot = self.demDS.GetGeoTransform()
        self.MAX_COUNT = math.ceil(self.MAX_POND_AREA / abs(self.geot[1] * self.geot[5]) / 1)
        self.driverTiff = gdal.GetDriverByName("GTiff")
        max = np.max(self.fdir)
        if max > 8:
            self.FLOW_DIR = self.FLOW_DIR_ESRI
        else:
            self.FLOW_DIR = self.FLOW_DIR_TAUDEM

    def createOutputArrays(self):
        self.idOut = np.copy(self.id)
        self.htOut = np.empty(shape=[self.dem.shape[0], self.dem.shape[1]])
        self.htOut.fill(-9999.0)
        self.depLo = np.empty(shape=[self.dem.shape[0], self.dem.shape[1]])
        self.depLo.fill(-9999.0)
        self.depMid = np.empty(shape=[self.dem.shape[0], self.dem.shape[1]])
        self.depMid.fill(-9999.0)
        self.depHi = np.empty(shape=[self.dem.shape[0], self.dem.shape[1]])
        self.depHi.fill(-9999.0)

    def setArraysTest(self, fdir, dem, id):
        self.fdir = fdir
        self.dem = dem
        self.id = id
        self.htOut.fill(-9999.0)
        self.idOut = self.id

    def getDamId(self):
        return self.id

    def getDEM(self):
        return self.dem

    def getFlowDirection(self):
        return self.fdir

    def getHeightAbove(self):
        return self.htOut

    def getPondID(self):
        return self.idOut

    def drainsToMe(self, index, fdir):
        if index == 4:
            return False
        elif index == 0 and fdir == self.FLOW_DIR[8]:
            return True
        elif index == 1 and fdir == self.FLOW_DIR[7]:
            return True
        elif index == 2 and fdir == self.FLOW_DIR[6]:
            return True
        elif index == 3 and fdir == self.FLOW_DIR[5]:
            return True
        elif index == 5 and fdir == self.FLOW_DIR[3]:
            return True
        elif index == 6 and fdir == self.FLOW_DIR[2]:
            return True
        elif index == 7 and fdir == self.FLOW_DIR[1]:
            return True
        elif index == 8 and fdir == self.FLOW_DIR[0]:
            return True
        else:
            return False

    def backwardHAND(self, startX, startY, startE, pondID):
        if startX > 0 and startY > 0 and startX < self.demDS.RasterXSize-1 and startY < self.demDS.RasterYSize-1:
            demWin = self.dem[startY - 1:startY + 2, startX - 1:startX + 2].reshape(1, 9)
            fdirWin = self.fdir[startY - 1:startY + 2, startX - 1:startX + 2].reshape(1, 9)
            for i in range(0,9):
                newX = startX
                newY = startY
                htAbove = demWin[0, i] - startE

                if (self.drainsToMe(i, fdirWin[0,i]) and htAbove < self.MAX_HEIGHT and htAbove > -10.0) and self.count < self.MAX_COUNT:
                    newX += self.COL_OFFSET[i]
                    newY += self.ROW_OFFSET[i]
                    htOld = self.htOut[newY, newX]

                    if (htOld >= htAbove or htOld == -9999.0):
                        self.idOut[newY, newX] = pondID
                        self.htOut[newY, newX] = htAbove
                        self.count += 1

                        self.backwardHAND(newX, newY, startE, pondID)

    def heightAboveDams(self):
        for i in range(1, self.fdir.shape[0]):
            for j in range(1, self.fdir.shape[1]):
                idVal = self.id[i,j]

                if idVal >= 0:
                    demVal = self.dem[i,j]
                    self.count = 0
                    self.backwardHAND(j, i, demVal, idVal)

    def calculateWaterDepth(self):
        self.dem[self.dem == -9999.0] = np.nan
        self.htOut[self.htOut == -9999.0] = np.nan
        for i in range(0, self.points.GetFeatureCount()):
            feature = self.points.GetFeature(i)
            self.depLo[self.idOut == i] = feature.GetFieldAsDouble("ht_lo_mod") - self.htOut[self.idOut == i]
            self.depMid[self.idOut == i] = feature.GetFieldAsDouble("ht_mid_mod") - self.htOut[self.idOut == i]
            self.depHi[self.idOut == i] = feature.GetFieldAsDouble("ht_hi_mod") - self.htOut[self.idOut == i]

        self.dem[self.dem == np.nan] = -9999.0
        self.htOut[self.htOut == np.nan] = -9999.0
        self.depLo[self.depLo == np.nan] = -9999.0
        self.depMid[self.depLo == np.nan] = -9999.0
        self.depHi[self.depLo == np.nan] = -9999.0

    def saveOutputs(self):
        self.outIdDS = self.driverTiff.Create(self.outDir + "/pondID.tif", xsize = self.demDS.RasterXSize, ysize = self.demDS.RasterYSize,
                                              bands = 1, eType = gdal.GDT_Float32)
        self.outIdDS.SetGeoTransform(self.geot)
        self.outHtDS = self.driverTiff.Create(self.outDir + "/htAbove.tif", xsize=self.demDS.RasterXSize,
                                              ysize=self.demDS.RasterYSize,
                                              bands=1, eType=gdal.GDT_Float32)
        self.outHtDS.SetGeoTransform(self.geot)
        self.depLoDS = self.driverTiff.Create(self.outDir + "/depLo.tif", xsize=self.demDS.RasterXSize,
                                              ysize=self.demDS.RasterYSize,
                                              bands=1, eType=gdal.GDT_Float32)
        self.depLoDS.SetGeoTransform(self.geot)
        self.depMidDS = self.driverTiff.Create(self.outDir + "/depMid.tif", xsize=self.demDS.RasterXSize,
                                              ysize=self.demDS.RasterYSize,
                                              bands=1, eType=gdal.GDT_Float32)
        self.depMidDS.SetGeoTransform(self.geot)
        self.depHiDS = self.driverTiff.Create(self.outDir + "/depHi.tif", xsize=self.demDS.RasterXSize,
                                              ysize=self.demDS.RasterYSize,
                                              bands=1, eType=gdal.GDT_Float32)
        self.depHiDS.SetGeoTransform(self.geot)

        self.outIdDS.GetRasterBand(1).WriteArray(self.idOut)
        self.outIdDS.GetRasterBand(1).SetNoDataValue(-9999.0)
        self.outHtDS.GetRasterBand(1).WriteArray(self.htOut)
        self.outHtDS.GetRasterBand(1).SetNoDataValue(-9999.0)
        self.depLo[self.depLo <= 0.0] = -9999.0
        self.depLoDS.GetRasterBand(1).WriteArray(self.depLo)
        self.depLoDS.GetRasterBand(1).SetNoDataValue(-9999.0)
        self.depMid[self.depMid <= 0.0] = -9999.0
        self.depMidDS.GetRasterBand(1).WriteArray(self.depLo)
        self.depMidDS.GetRasterBand(1).SetNoDataValue(-9999.0)
        self.depHi[self.depHi <= 0.0] = -9999.0
        self.depHiDS.GetRasterBand(1).WriteArray(self.depLo)
        self.depHiDS.GetRasterBand(1).SetNoDataValue(-9999.0)

    def run(self):
        self.heightAboveDams()
        self.calculateWaterDepth()
        self.saveOutputs()

    def close(self):
        self.demDS = None
        self.fdirDS = None
        self.idDS = None
        self.pointDS = None
        self.points = None
        self.depLoDS = None
        self.depMidDS = None
        self.depHiDS = None