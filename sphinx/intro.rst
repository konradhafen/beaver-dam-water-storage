What is BDWS?
=============

Beaver Dam Water Storage (BDWS) is a collection of Python classes for estimating surface water and groundwater stored
by beaver dams. BDWS uses beaver dam capacity estimates from the Beaver Restoration Assesment Tool
`(BRAT) <http://brat.joewheaton.org>`_ to place beaver dams along stream reaches, flow direction algebra to determine the area
inundated by a dam, and `MODFLOW-2005 <https://water.usgs.gov/ogw/modflow/mf2005.html>`_ to model potential changes to
groundwater tables from beaver dam construction. BDWS is comprised of three classes. :code:`BDLoG` (Beaver Dam Location
Generator), which generates beaver dam locations along a stream network using BRAT outputs. :code:`BDSWEA` (Beaver Dam
Surface Water Estimation Algorithm), which estimates the amount of water a beaver dam of a given height at a given
location could potentially store. :code:`BDflopy` (Beaver Dam flopy), which uses the existing
`FloPy <https://modflowpy.github.io/flopydoc/>`_ python module to automatically parameterize and run MODFLOW-2005 to
estimate changes to groundwater storage resulting from beaver dam construction.
