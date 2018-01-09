Tutorials
=========

General usage
-------------


At the end of the general usage section: Mention some python IDEs and how to start a project in pycharm.

Tutorial 1: Single HUC12
------------------------

This tutorial assumes the user has downloaded the entire repository and maintained the respository file structure.
Code is available in the file `run.py`.

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
    outDir = basedir + "/out"

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
    idPath = basedir + "/out/damID.tif" #ouput from BDLoG
    modPoints = basedir + "/out/ModeledDamPoints.shp" #output from BDLoG

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
location thatn this path indicates. Also, the :code:`hkfn`, :code:`vkfn`, and :code:`fracfn` can be represented by a
raster, numpy array, or single value.

.. code-block:: python

    modflowexe = "C:/WRDAPP/MF2005.1_11/bin/mf2005" #path to MODFLOW-2005 executable
    indir = basedir + "/inputs" #location of input raste files
    modeldir = "tutorials/tutorial1/out" #BDSWEA output directory
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

