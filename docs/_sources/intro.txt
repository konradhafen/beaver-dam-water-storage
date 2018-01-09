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

Products
========

Publications
------------

Hafen, K. 2017. To what extent might beaver dam building buffer water storage losses associated with a declining snowpack? Master's Thesis. Utah State University, Logan, Utah. https://digitalcommons.usu.edu/etd/6503/.

Presentations
-------------

Hafen, K., and J. M. Wheaton. 2017. Could beaver dams buffer a declining snowpack? Society of Wetland Scientists Pacific Northwest Chapter Meeting. Kelso, Washington. September 26.
`Slides <https://docs.google.com/presentation/d/141XedAGbuG7foso-tV6LOS5rT3RdpNE_akrNhYz3Sj4/edit?usp=sharing>`_.

Wheaton, J. M., K. Hafen, W. W. Macfarlane, and N. Bouwes. 2017. Could beaver compete with a declining snowpack? American Water Resources Association Meeting. Snowbird, Utah. May. doi: 10.13140/RG.2.2.32406.86089.
`Slides <https://www.researchgate.net/publication/318351273_Could_beaver_compete_with_a_declining_snowpack>`_.

Hafen, K. 2017. To what extent might beaver dam building buffer water storage losses associated with a declining snowpack? Thesis Defense. Logan, Utah. April 21.
`Slides <https://docs.google.com/presentation/d/1kQZ21aLvOxW3n7COvL8z3HYixUsiVAexQXGjzn1BhjE/edit?usp=sharing>`_.