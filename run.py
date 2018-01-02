from bdflopy import BDflopy
#run beaver dam location generator (BDLoG)
#run surface water storage estimation (BDSWEA)
#run groundwater storage estimation (MODFLOW)
modflowexe = 'C:/WRDAPP/MF2005.1_11/bin/mf2005'
maindir = "C:/temp/templefork"
indir = maindir + "/02_rasIn"
modeldir = maindir + "/03_out_100"
outdir = maindir + "/test"
demfilename = "dem_vbfac.tif"
gwmodel = BDflopy(modflowexe, indir, modeldir, outdir, demfilename)
gwmodel.run()