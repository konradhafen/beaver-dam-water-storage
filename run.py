from bdflopy import BDflopy
from bdws import *
import time
#run beaver dam location generator (BDLoG)
print "start"
start = time.time()

basedir = "C:/temp/test"
bratPath = basedir + "/01_shpIn/brat_cap_20170224.shp"
demPath = basedir + "/02_rasIn/dem_vbfac.tif"
facPath = basedir + "/02_rasIn/fac_01km_vbfac.tif"
outDir = basedir + "/out"

model = BDLoG(bratPath, demPath, facPath, outDir, 1.0)
#model.generateDamLocationsFromBRAT()
model.run()
model.close()
print "bdlog done"
end = time.time()
print (end - start)

#run surface water storage estimation (BDSWEA)
# basedir = "/home/konrad/crap"
basedir = "C:/temp/test"
demPath = basedir + "/02_rasIn/dem_vbfac.tif"
fdirPath = basedir + "/02_rasIn/fdird_vbfac.tif"
facPath = basedir + "/02_rasIn/fac_01km_vbfac.tif"
idPath = basedir + "/out/damID.tif"
modPoints = basedir + "/out/ModeledDamPoints.shp"
outDir = basedir + "/out"

model = BDSWEA(demPath, fdirPath, facPath, idPath, outDir, modPoints)
model.run()
model.writeModflowFiles()
model.close()
end = time.time()
print "bdswea done"
print (end - start)

#run groundwater storage estimation (MODFLOW)
modflowexe = "C:/WRDAPP/MF2005.1_11/bin/mf2005"
indir = basedir + "/02_rasIn"
modeldir = outDir
outdir = basedir + "/modflow"
demfilename = "dem_vbfac.tif"
gwmodel = BDflopy(modflowexe, indir, modeldir, outdir, demfilename)
gwmodel.run(0.0001, 0.0001)
gwmodel.close()
end = time.time()
print "done"
print (end - start)