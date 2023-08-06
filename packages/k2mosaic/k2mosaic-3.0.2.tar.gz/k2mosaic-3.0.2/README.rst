K2mosaic: Mosaic Kepler Pixel Data
==================================

**Mosaic Target Pixel Files (TPFs)
obtained by NASA's Kepler/K2 missions
into CCD-sized images and movies.**

.. image:: http://img.shields.io/pypi/v/k2mosaic.svg
    :target: https://pypi.python.org/pypi/k2mosaic/
    :alt: PyPI

.. image:: http://img.shields.io/travis/KeplerGO/k2mosaic/master.svg
    :target: http://travis-ci.org/KeplerGO/k2mosaic
    :alt: Travis status

.. image:: http://img.shields.io/badge/license-MIT-blue.svg
    :target: https://github.com/KeplerGO/k2mosaic/blob/master/LICENSE
    :alt: MIT license

.. image:: https://zenodo.org/badge/52581319.svg
   :target: https://zenodo.org/badge/latestdoi/52581319
   :alt: Zenodo DOI

K2mosaic is a command-line tool which allows the
postage stamp-sized pixel masks obtained by
`NASA's Kepler and K2 missions <http://keplerscience.nasa.gov>`_
to be stitched together into CCD-sized mosaics and movies.
The principal use is to take a set of *Target Pixel Files* (TPF)
and turn them into more traditional FITS image files --
one per CCD channel and per cadence.
K2mosaic can also be used
to create fancy animations from these mosaics.

The need for this tool arises from the fact
that the analysis of certain Kepler/K2 targets,
such as clusters and asteroids,
is more easily performed on mosaicked data.
Moreover such mosaics are useful to reveal the context
of single-star observations,
e.g. they enable users to check for the presence of instrumental noise
or nearby bright objects.

Documentation
-------------

Read the docs and see usage examples at `k2mosaic.geert.io <http://k2mosaic.geert.io>`_.


Attribution
-----------

Created by Geert Barentsen at the NASA Kepler/K2 Guest Observer Office.

If this tool aided your research, please cite it.
Please get in touch before submitting your paper
so I can request an entry in the Astrophysics Source Code Library (ASCL).

