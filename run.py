from bdflopy import BDflopy
from bdws import *
import time
#run beaver dam location generator (BDLoG)
#run surface water storage estimation (BDSWEA)
# basedir = "/home/konrad/crap"
basedir = "C:/crap"
demPath = basedir + "/02_rasIn/fil10m_vb.tif"
fdirPath = basedir + "/02_rasIn/fdir10m_vb.tif"
idPath = basedir + "/03_out/damID.tif"
modPoints = basedir + "/03_out/ModeledDamPoints.shp"
outDir = basedir

print "start"
start = time.time()
model = BDSWEA(demPath, fdirPath, idPath, outDir, modPoints)
model.run()
model.close()
end = time.time()
print "end"
print (end - start)

#run groundwater storage estimation (MODFLOW)
# modflowexe = "C:/WRDAPP/MF2005.1_11/bin/mf2005"
# maindir = "C:/temp/templefork"
# indir = maindir + "/02_rasIn"
# modeldir = maindir + "/03_out_100"
# outdir = maindir + "/test"
# demfilename = "dem_vbfac.tif"
# gwmodel = BDflopy(modflowexe, indir, modeldir, outdir, demfilename)
# gwmodel.run(0.0001, 0.0001)
# gwmodel.close()