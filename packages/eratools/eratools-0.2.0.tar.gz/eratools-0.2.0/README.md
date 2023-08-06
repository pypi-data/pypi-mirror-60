[![xarray](http://img.shields.io/badge/powered%20by-xarray-blue.svg?style=flat)](http://http://xarray.pydata.org/en/stable/)

# eratools

### A package that extends xarray with functionality to work with ECMWF ERA data. 

## Introduction
`eratools` loads [ECMWF](https://www.ecmwf.int/) ERA5 or ERA-Interim data files that contain model level data of temperature, relative humidity, surface pressure, and surface geopotential.
It uses these variables to calculate pressure and temperature data on pressure levels and altitude levels.

Also included is a utility for downloading daily files of ERA5 or ERA-Interim data. 

## Further reading
* ECMWF IFS dosumentation [Cy38r1 Part III](https://www.ecmwf.int/sites/default/files/elibrary/2013/9244-part-iii-dynamics-and-numerical-procedures.pdf)
* ECMWF referenced [paper](http://journals.ametsoc.org/doi/abs/10.1175/1520-0493%281981%29109%3C0758:AEAAMC%3E2.0.CO;2)
* Example [code](https://confluence.ecmwf.int/x/u8RCBQ) on ECMWF's wiki

## Installation

To create a conda environmen and install run:
```
conda env create -f environment.yml
source activate eratools
pip install eratools
```

### Optional Dependencies

If you wish to use the ERA downloading utilities, you will need to follow the instructions [here](https://confluence.ecmwf.int/display/WEBAPI/Access+ECMWF+Public+Datasets)

## Supported Products
* ERA5
* ERA-Interim