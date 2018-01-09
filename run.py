from bdws import * #import BDLoG and BDSWEA classes
from bdflopy import * #import BDflopy class

#######################################################################
###################### TUTORIAL 1 - SINGLE HUC12 ######################
#######################################################################

#NOTE: use ctrl + / to comment/uncomment multiple lines

#run beaver dam location generator (BDLoG)
# print "start"
# basedir = "tutorials/tutorial1" #folder containing inputs, and where output directories will be created
# bratPath = basedir + "/inputs/brat.shp" #shapefile of beaver dam capacities from BRAT
# demPath = basedir + "/inputs/dem.tif" #DEM of study area (ideally clipped to valley-bottom)
# facPath = basedir + "/inputs/fac.tif" #Thresholded flow accumulation raster representing stream network
# outDir = basedir + "/outputs" #directory where BDLoG outputs will be generated
# bratCap = 1.0 #proportion (0-1) of maximum estimted dam capacity (from BRAT) for scenario
#
# model = BDLoG(bratPath, demPath, facPath, outDir, bratCap) #initialize BDLoG, sets varibles and loads inputs
# model.run() #run BDLoG algorithms
# model.close() #close any files left open by BDLoG
# print "bdlog done"
#
# #run surface water storage estimation (BDSWEA)
# fdirPath = basedir + "/inputs/fdir.tif" #flow direction raster
# idPath = basedir + "/outputs/damID.tif" #ouput from BDLoG
# modPoints = basedir + "/outputs/ModeledDamPoints.shp" #output from BDLoG
#
# model = BDSWEA(demPath, fdirPath, facPath, idPath, outDir, modPoints) #initialize BDSWEA object, sets variables and loads inputs
# model.run() #run BDSWEA algorithm
# model.writeModflowFiles() #generate files needed to parameterize MODFLOW
# model.close() #close any files left open by BDLoG
# print "bdswea done"
#
# #run groundwater storage estimation (MODFLOW)
# modflowexe = "C:/WRDAPP/MF2005.1_11/bin/mf2005" #path to MODFLOW-2005 executable
# indir = basedir + "/inputs" #location of input raste files
# modeldir = "tutorials/tutorial1/outputs" #BDSWEA output directory
# outdir = basedir + "/modflow" #directory to output MODFLOW results
# demfilename = "dem.tif" #name of input DEM
# hkfn = "/inputs/ksat.tif" #horizontal ksat in micrometers per second
# vkfn = "/inputs/kv.tif" #vertical ksat in micrometers per second
# fracfn = "/inputs/fc.tif" #field capacity as percentage
# kconv = 0.000001 #conversion of hkfn and vkfn to meters per second
# fconv = 0.01 #conversion of fracfn to a proportion
# gwmodel = BDflopy(modflowexe, indir, modeldir, outdir, demfilename) #initialize BDflopy, sets variables and loads inputs
# gwmodel.run(hkfn, vkfn, kconv, fracfn, fconv) #run BDflopy, this will write inputs for MODFLOW and then run MODFLOW
# gwmodel.close() #close any open files
# print "done"

##########################################################################
###################### TUTORIAL 2 - MULTIPLE HUC12s ######################
##########################################################################

#NOTE: use ctrl + / to comment/uncomment multiple lines

basedir = "tutorials/tutorial2" #folder containing inputs, and where output directories will be created
modflowexe = "C:/WRDAPP/MF2005.1_11/bin/mf2005" #path to MODFLOW-2005 executable
bratCap = 1.0 #proportion (0-1) of maximum estimted dam capacity (from BRAT) for scenario
demfilename = "dem.tif" #name of input DEM
indirname = "inputs" #name of directory containing inputs for each HUC12
bratPath = indirname + "/brat.shp"  # shapefile of beaver dam capacities from BRAT
demPath = indirname + "/dem.tif"  # DEM of study area (ideally clipped to valley-bottom)
facPath = indirname + "/fac.tif"  # Thresholded flow accumulation raster representing stream network
outdirname = "outputs"  # directory where BDLoG outputs will be generated
fdirPath = indirname + "/fdir.tif" #flow direction raster
idPath = outdirname + "/damID.tif" #ouput from BDLoG
modPoints = outdirname + "/ModeledDamPoints.shp" #output from BDLoG
hkfn = "inputs/ksat.tif" #horizontal ksat in micrometers per second
vkfn = "inputs/kv.tif" #vertical ksat in micrometers per second
fracfn = "inputs/fc.tif" #field capacity as percentage
kconv = 0.000001 #conversion of hkfn and vkfn to meters per second
fconv = 0.01 #conversion of fracfn to a proportion
cwd = os.getcwd() #get the current working directory

for subdir in os.listdir(basedir): #loop through directories in basedir
    if os.path.exists(basedir + "/" + subdir + "/" + indirname + "/" + demfilename): #make sure the subdirectory contains a inputs directory with a DEM, this will skip over any directories without a DEM inputs
        print "Running BDWS for " + subdir #print name of directory
        os.chdir(cwd + "/" + basedir + "/" + subdir) #change working directory to subdirectory

        #generate beaver dam locations from BRAT
        model = BDLoG(bratPath, demPath, facPath, outdirname, bratCap) #initialize BDLoG, sets varibles and loads inputs
        model.run() #run BDLoG algorithms
        model.close() #close any files left open by BDLoG
        print "bdlog done"

        #run surface water storage estimation (BDSWEA)
        model = BDSWEA(demPath, fdirPath, facPath, idPath, outdirname, modPoints) #initialize BDSWEA object, sets variables and loads inputs
        model.run() #run BDSWEA algorithm
        model.writeModflowFiles() #generate files needed to parameterize MODFLOW
        model.close() #close any files left open by BDLoG
        print "bdswea done"

        #run groundwater storage estimation (MODFLOW)
        indir = "inputs" #location of input raste files
        modeldir = "outputs" #BDSWEA output directory
        outdir = "modflow" #directory to output MODFLOW results

        gwmodel = BDflopy(modflowexe, indir, modeldir, outdir, demfilename) #initialize BDflopy, sets variables and loads inputs
        gwmodel.run(hkfn, vkfn, kconv, fracfn, fconv) #run BDflopy, this will write inputs for MODFLOW and then run MODFLOW
        gwmodel.close() #close any open files
        print os.path.relpath(subdir, basedir)+" done"

        os.chdir(cwd) #change current working directory back to original
    else:
        print "Does not contain DEM " + subdir