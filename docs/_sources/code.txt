Code Description
==================

BDLoG Class
-----------

Generate beaver dam locations and beaver dam heights along a stream network according to beaver dam capacities estimated by the Beaver Restoration Assessment Tool (BRAT). Information about BRAT is available at http://brat.joewheaton.org/home.

.. autoclass:: bdws.BDLoG
    :members:

BDSWEA Class
------------

Estimate the surface storage of beaver ponds at locations created from the BDLoG class.

.. autoclass:: bdws.BDSWEA
    :members:

BDflopy Class
-------------

Use MODFLOW-2005 to estimate the change in groundwater storage resulting from the construction of beaver dams.

.. autoclass:: bdflopy.BDflopy
    :members:
