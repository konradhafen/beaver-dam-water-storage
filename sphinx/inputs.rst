Preparing input data
====================

General guidelines
------------------

Adherence to the following guidelines will greatly improve your experience while using BDWS.

1. All geographic layers must have a projected coordinate system with linear units represented in meters (to be safe use a NAD83 UTM projection).
2. All input rasters must be concurrent (same extent and cell resolution) with the input DEM. Problems will arise if input rasters differ in projection, cell resolution, the number of columns, or the number of rows.
3. Features of input line shapefiles (from BRAT) must be single-part. :code:`BDLoG` will not place dam locations on multipart features.
4. When creating dam capacity estimates, follow `BRAT <http://brat.joewheaton.org/home>`_ directions exactly. Use of `pyBRAT <http://brat.joewheaton.org/home/documentation/manual-implementation/the-beaver-restoration-assessment-tool-brat---v-2-0>`_ is recommended (ArcGIS is required for pyBRAT)
5. Computation time will be decreased if all inputs are clipped to the valley-bottom extent. The `V-BET tool <http://etal.joewheaton.org/nhd-network-builder-and-vbet>`_ can be used to generate valley-bottom polygons.

