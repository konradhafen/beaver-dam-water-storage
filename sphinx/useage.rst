How to use BDWS
===============

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