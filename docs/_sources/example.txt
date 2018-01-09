Tutorials
=========

General usage
-------------


At the end of the general usage section: Mention some python IDEs and how to start a project in pycharm.

Output files
------------

BDLoG generates the following files:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`ModeledDamPoints.shp`
    A shapefile containing generated beaver dam locations and information about each dam. This file is updated with estimated area and volume of resulting ponds by :code:`BDSWEA`.

    **Attributes**

    - `damType`: If the dam is primary or secondary. Primary dams are taller than secondary, this classification determines which distirbution is used to model dam heights
    - `ht_lo`: The 0.025 quantile of the values selected from the dam height distribution. Modeled as the low dam height scenario.
    - `ht_mid`: The 0.5 quantile of the values selected from the dam height distribution. Modeled as the median dam height scenario.
    - `ht_hi`: The 0.975 quantile of the values selected from the dam height distribution. Modeled as the high dam height scenario.
    - `area_*`: Area of the pond created by modeling the dam under a given height scenario.
    - `vol_*`: Volume of the pond created by modeling the dam under a given height scenario.
    - `Other fields`: For use in adjusting dam heights to fit within the prediction intervals of an empirical model. This is not yet implemented in the python code version.

`damID.tif`
    Rasterized locations of generated beaver dams. Each beaver dam location is represented by a single cell with a number corresponding to the FID in `ModeledDamPoints.shp`.

BDSWEA generates the following files:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`depLo.tif, depMid.tif, depHi.tif`
    Depths of modeded beaver ponds for low, median, and high dam heights.

`htAbove.tif`
    The height of cell above the dam it drains to. Used for determining pond dephts.

`pondID.tif`
    FID of the dam a cell drains to. Used to calculate area and volume of modeled ponds.

`WSESurf_lo.tif, WSESurf_mid.tif, WSESurf_hi.tif`
    The sum of the input DEM and each pond depth raster. Used to parameterize the top of the MODFLOW modeling domain.

`head_start.tif, head_lo.tif, head_mid.tif, head_hi.tif`
    The intersection of the rasterized stream network and each WSESurf_*.tif file. This represents the water surface elevation of the stream and beaver dams. Used for MODFLOW parameterization.

BDflopy generates the following files:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`start.*, lo.*, mid.*, hi.*`
    Input files written by :code:`flopy` as inputs to MODFLOW, or output files written by MODFLOW.

`ibound_start.tif, ibound_lo.tif, ibound_mid.tif, ibound_hi.tif`
    Definitions of the model domain (active, inactive, and constant head boundaries) for each MODFLOW simulation.

`shead_start.tif, shead_lo.tif, shead_mid.tif, shead_hi.tif`
    Starting hydraulic head values for each MODFLOW simulation.

`ehead_start.tif, ehead_lo.tif, ehead_mid.tif, ehead_hi.tif`
    Modeled hydraulic head values (water table elevation) for each MODFLOW simulation.

`hdch_lo.tif, hdch_mid.tif, hdch_hi.tif`
    Estimated change in groundwater elevations from construction of beaver dams with low, median and height heights. Obtained by subtracting `ehead_start.tif` from water table elevations modeled with beaver pond influence.

`hdch_lo_frac.tif, hdch_mid_frac.tif, hdch_hi_frac.tif`
    `hdch_*.tif` multiplied by the water holding capacity of the soil (e.g. field capacity or porosity).

Tutorial 1: Single HUC12
------------------------

This tutorial gives an example of writing a script to use BDWS to estimate water that could be stored by beaver dams in
the Rock Creek watershed of northern Utah.
This tutorial assumes the user has downloaded the entire repository and maintained the respository file structure.
Code is available in the file `run.py`.

If you are using `run.py` begin by uncommenting code for Tutorial 1 and commenting code for Tutorial 2.
Use ctrl + / to comment all selected lines of code.

Import :code:`BDLoG`, :code:`BDSWEA`, and :code:`BDflopy` classes.

.. code-block:: python

    from bdws import *
    from bdflopy import *

Set paths to input files. If you have setup a pycharm project in the same directory as the repository you can use the
file paths exactly as shown below.

.. code-block:: python

    basedir = "tutorials/tutorial1" #folder containing inputs, and where output directories will be created
    bratPath = basedir + "/inputs/brat.shp" #shapefile of beaver dam capacities from BRAT
    demPath = basedir + "/inputs/dem.tif" #DEM of study area (ideally clipped to valley-bottom)
    facPath = basedir + "/inputs/fac.tif" #Thresholded flow accumulation raster representing stream network
    outDir = basedir + "/outputs"

Set proportion of BRAT capacity at which to place dams. For the given study area, a value of 1.0 will sum the total
number of dams estimated by BRAT and place them on the stream network. A value of 0.5 will place half of the total
number of dams estimated by BRAT on the stream network.

.. code-block:: python

    bratCap = 1.0 #proportion (0-1) of maximum estimted dam capacity (from BRAT) for scenario

Now we'll initialize :code:`BDLoG` and call the run function, which will automatically run the dam placement algorithm and
create the necessary outputs to run :code:`BDSWEA`.

.. code-block:: python

    model = BDLoG(bratPath, demPath, facPath, outDir, bratCap) #initialize BDLoG, sets varibles and loads inputs
    model.run() #run BDLoG algorithms
    model.close() #close any files left open by BDLoG

Set paths to files needed by :code:`BDSWEA` that we have not already specified. Namely, a flow direction raster, the shapefile
of dam locations and dam attributes created by :code:`BDLoG`, and a raster marking the location of dams created by
:code:`BDLoG`.

.. code-block:: python

    fdirPath = basedir + "/inputs/fdir.tif" #flow direction raster
    idPath = basedir + "/outputs/damID.tif" #ouput from BDLoG
    modPoints = basedir + "/outputs/ModeledDamPoints.shp" #output from BDLoG

We're now set to intialize the :code:`BDSWEA` class and run the algorithm to calculate beaver pond surface water storage.

.. code-block:: python

    model = BDSWEA(demPath, fdirPath, facPath, idPath, outDir, modPoints) #initialize BDSWEA object, sets variables and loads inputs
    model.run() #run BDSWEA algorithm

Before we close the :code:`BDSWEA` object let's also print the raster files we will need to automatically parameterize MODFLOW
for calculation of changes to groundwater storage. Then close the :code:`BDSWEA` object.

.. code-block:: python

    model.writeModflowFiles() #generate files needed to parameterize MODFLOW
    model.close() #close any files left open by BDLoG

Now set the file paths and variables necessary to parameterize and run MODFLOW-2005 using :code:`BDflopy`. **Note:** the
:code:`modflowexe` parameter may need to be changed if your MODFLOW-2005 executable file (.exe) is in a different
location than this path indicates. Also, the :code:`hkfn`, :code:`vkfn`, and :code:`fracfn` parameters can be represented by a
raster, numpy array, or single value.

.. code-block:: python

    modflowexe = "C:/WRDAPP/MF2005.1_11/bin/mf2005" #path to MODFLOW-2005 executable
    indir = basedir + "/inputs" #location of input raste files
    modeldir = "tutorials/tutorial1/outputs" #BDSWEA output directory
    outdir = basedir + "/modflow" #directory to output MODFLOW results
    demfilename = "dem.tif" #name of input DEM
    hkfn = "/inputs/ksat.tif" #horizontal ksat in micrometers per second
    vkfn = "/inputs/kv.tif" #vertical ksat in micrometers per second
    fracfn = "/inputs/fc.tif" #field capacity as percentage
    kconv = 0.000001 #conversion of hkfn and vkfn to meters per second
    fconv = 0.01 #conversion of fracfn to a proportion

With this information we are ready to parameterize and run MODFLOW-2005 with :code:`BDflopy`. This is done by
initializing and running a :code:`BDflopy` object. **Note:** writing MODFLOW inputs will take a fair amount of time,
depending on the size of the area you are modeling and your machine's hardware. If you are running this from the
pycharm IDE you will see printed messages indicating when inputs for a MODFLOW run have been completed. You will also
likely see output from MODFLOW itself after all MODFLOW inputs have been written and the MODFLOW runs.

.. code-block:: python

    gwmodel = BDflopy(modflowexe, indir, modeldir, outdir, demfilename) #initialize BDflopy, sets variables and loads inputs
    gwmodel.run(hkfn, vkfn, kconv, fracfn, fconv) #run BDflopy, this will write inputs for MODFLOW and then run MODFLOW
    gwmodel.close() #close any open files

Congratulations! You have successfully estimated the amount of surface water and groundwater beaver dams could store!

Tutorial 2: Multiple HUC12s
---------------------------

This tutorial gives an example of how to write a script that uses BDWS to process multiple watersheds.
We process two HUC12 watersheds from northern Utah, Left Hand Fork and Rock Creek.
This tutorial assumes the user has downloaded the entire repository and maintained the respository file structure.
Code is available in the file `run.py`. Note: Tutorial 1 gives detailed directions for implementing each class in BDWS.
Tutorial 2 gives and example of how to batch process watershed with BDWS; refer to Tutorial 1 for specific directions
to call BDWS classes.

If you are using `run.py` begin by uncommenting code for Tutorial 2 and commenting code for Tutorial 1.
Use ctrl + / to comment all selected lines of code.

Prior to batch processing with BDWS, data must be organized as in the `tutorial2` folder. Each directory under the root
directory (e.g. `tutorial2`) must have an inputs directory, all these input directories must have same name. All input
files must also have the same name (e.g. all input DEMs must be named `dem.tif`).

After the :code:`BDLoG`, :code:`BDSWEA`, and :code:`BDflopy` classes are imported, begin by setting directory names, file names,
and variables that will remain constant through the batch processing. We also set a variable for the current working directory.
MODFLOW writes output files to the working directory, knowing the directory in which we start allows us to later change the directory
where MODFLOW files are written. Note: the :code:`basedir` variable is the root directory that contains a folder for each
watershed we will model.

.. code-block:: python

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

Now we loop through all subdirectories under the root directory. For each subdirectory we check to make sure there is an input DEM.
If there is we change the current working directory to the subdirectory.

.. code-block:: python

    for subdir in os.listdir(basedir): #loop through directories in basedir
        if os.path.exists(basedir + "/" + subdir + "/" + indirname + "/" + demfilename): #make sure the subdirectory contains a inputs directory with a DEM, this will skip over any directories without a DEM inputs
            print "Running BDWS for " + subdir #print name of directory
            os.chdir(cwd + "/" + basedir + "/" + subdir) #change working directory to subdirectory

Run :code:`BDLoG`.

.. code-block:: python

    model = BDLoG(bratPath, demPath, facPath, outdirname, bratCap) #initialize BDLoG, sets varibles and loads inputs
    model.run() #run BDLoG algorithms
    model.close() #close any files left open by BDLoG
    print "bdlog done"

Run :code:`BDSWEA`.

.. code-block:: python

    model = BDSWEA(demPath, fdirPath, facPath, idPath, outdirname, modPoints) #initialize BDSWEA object, sets variables and loads inputs
    model.run() #run BDSWEA algorithm
    model.writeModflowFiles() #generate files needed to parameterize MODFLOW
    model.close() #close any files left open by BDLoG
    print "bdswea done"

Adjust file paths for :code:`BDflopy`.

.. code-block:: python

    indir = "inputs" #location of input raste files
    modeldir = "outputs" #BDSWEA output directory
    outdir = "modflow" #directory to output MODFLOW results

Run :code:`BDflopy`.

.. code-block:: python

    gwmodel = BDflopy(modflowexe, indir, modeldir, outdir, demfilename) #initialize BDflopy, sets variables and loads inputs
    gwmodel.run(hkfn, vkfn, kconv, fracfn, fconv) #run BDflopy, this will write inputs for MODFLOW and then run MODFLOW
    gwmodel.close() #close any open files
    print os.path.relpath(subdir, basedir)+" done"

Change the working directory back to the original.

.. code-block:: python

    os.chdir(cwd) #change current working directory back to original

If the subdirectoy does not contain an input DEM print a message.

.. code-block:: python

    else:
        print "Does not contain DEM " + subdir