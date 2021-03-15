# MPhys-Project
Code created for my MPhys Project at the University of Edinburgh. I am using optimisation methods to 'tune' uncertain aerosol parameters in a climate model.

This repository contains:

### obs.py
This Python code was used to analyse satellite data. It was run in a directory containing subsets of NASA's Aqua MODIS Level-3 Monthly Cloud Properties (available at https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5111/CLDPROP_M3_MODIS_Aqua/), and CERES Energy Balanced and Filled version 4.1 (available at https://ceres-tool.larc.nasa.gov/ord-tool/jsp/EBAFTOA41Selection.jsp) datasets. It calculates large-scale regional averages of various observations: cloud effective radius, top-of-atmosphere (TOA) shortwave (SW) radiation flux, TOA longwave (LW) flux, TOA clear-sky SW and LW fluxes, and global mean TOA net flux over a period of five years.

### obs_sim.py
This Python code was used to process output from the HadAM3 climate model in order to calculate averages of simulated versions of the observations listed above.

