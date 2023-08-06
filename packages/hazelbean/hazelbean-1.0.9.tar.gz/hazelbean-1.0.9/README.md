# Hazelbean
A collection of geospatial processing tools based on gdal, numpy, scipy, cython, pygeoprocessing, taskgraph, natcap.invest, geopandas and many others to assist in common spatial analysis tasks in sustainability science, ecosystem service assessment, global integrated modelling assessment,  natural capital accounting, and/or calculable general equilibrium modelling.

Hazelbean started as a personal research package of scripts for Justin Johnson and is not supported for broad release. However, hazelbean underlies several experimental software releases, including some from the Natural Capital Project, and thus it is available via "pip install hazelbean". Note that hazelbean only provides a Python 3.6, 64 bit, Windows version, however with the exception of precompiled cython files, it should be cross-platform and cross-version. The precompiled files are only loaded as needed.


## Installation

Pip installing Hazelbean will attempt to install required libraries, but many of these must be compiled for your computer. You can solve each one manually for your chosen opperating system, or you can use these Anaconda-based steps here:

- Install Anaconda3 with the newest python version (tested at python 3.6.3)
- Install libraries using conda command: "conda install -c conda-forge geopandas"
- Install libraries using conda command: "conda install -c conda-forge rasterstats"
- Install libraries using conda command: "conda install -c conda-forge netCDF4"
- Install libraries using conda command: "conda install -c conda-forge cartopy"
- Install libraries using conda command: "conda install -c conda-forge xlrd, markdown"
- Install libraries using conda command: "conda install -c conda-forge qtpy, qtawesome"
- Pip install anytree
- Pip install pygeoprocessing
- Pip install taskgraph

And then finally,
- Install hazelbean with "pip install hazelbean"

## More information
See the author's personal webpage, https://justinandrewjohnson.com/ for more details about the underlying research.
