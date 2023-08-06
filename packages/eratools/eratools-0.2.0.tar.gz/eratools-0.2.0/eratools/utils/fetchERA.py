import sys
import os
import re
import datetime as dt
from contextlib import redirect_stdout
from collections import ChainMap
import xarray as xr
from tempfile import NamedTemporaryFile
from cdsapi import Client
import logging


era5_path = os.environ['ERA5_DATA_DIR']

client = Client()

default_era5 = {
    'stream': 'oper',
    'step': '0',
    'type': 'an',
    'levtype': 'ml',
    'format': 'netcdf',
    'class': 'ea',
    'levelist': '1/to/137',
    'time': '00/to/23/by/1',
    'grid': '0.3/0.3'}


class ECMWFio:
    def __init__(self):
        self.terminal = sys.stdout

    def write(self, message):
        self.terminal.write(message)
        if re.match('ERROR Reason:  Expected \d+, got'):
            raise Exception('ECMWF: EXPECT was provided')

    def flush(self):
        pass


# The geopotential is static in ERA5. Use a cached version to avoid downloading it repeatedly.
if os.path.exists(os.path.join(era5_path, 'z.nc')):
    geopotential = xr.open_dataarray(os.path.join(era5_path, 'z.nc')).to_dataset()
else:
    with NamedTemporaryFile(suffix='.nc') as geotmpfile:
        georequest = dict(ChainMap({'date': '2010-01-01', 'param': '129', 'levelist': '1', 'time': '00'}, default_era5))
        client.retrieve('reanalysis-era5-complete', georequest, geotmpfile.name)
        geopotential = xr.open_dataset(geotmpfile.name).squeeze(dim=['time'], drop=True)


def retrieve_ml_single_and_multi_level_for_day(date, single=(152,), multi=(130, 133)):
    ds = geopotential
    # Retrieve (and merge) the single level params to the geopotential
    request = ChainMap({'date': f'{date}'}, default_era5)
    for param in single:
        with NamedTemporaryFile(suffix='.nc') as tmpfile:
            kwargs = dict(ChainMap({'param': str(param), 'levelist': '1'}, request))
            client.retrieve('reanalysis-era5-complete', kwargs, tmpfile.name)
            ds = ds.merge(xr.open_dataset(tmpfile.name))
    # Retrieve the multilevel params
    for param in multi:
        with NamedTemporaryFile(suffix='.nc') as tmpfile:
            kwargs = dict(ChainMap({'param': str(param)}, request))
            client.retrieve('reanalysis-era5-complete', kwargs, tmpfile.name)
            ds = ds.merge(xr.open_dataset(tmpfile.name, chunks={'level': 1}))
    return ds


def retrieve_pl_for_day(date, variable=['geopotential', 'temperature']):
    ds = geopotential
    # Retrieve (and merge) the single level params to the geopotential
    request = ChainMap({'date': f'{date}', 'product_type': 'reanalysis', 'variable': variable}, default_era5)
    with NamedTemporaryFile(suffix='.nc') as tmpfile:
        kwargs = dict(ChainMap({'levelist': 'all'}, request))
        client.retrieve('reanalysis-era5-pressure-levels', kwargs, tmpfile.name)
        ds = xr.open_dataset(tmpfile.name)
    return ds


def daterange(d1, d2):
    return (d1 + dt.timedelta(days=i) for i in range((d2 - d1).days))


def retrieve_days(startdate, enddate, level_type='ml'):
    assert level_type in ('al', 'pl'), "level_type must be 'ml' for model level or 'pl' for pressure level"
    for today in daterange(startdate, enddate):
        path = os.path.join(era5_path, f'{today.year}', f'{today.month:02}')
        filename = f'ERA5_{level_type}_{today.year}{today.month:02}{today.day:02}.nc'
        file = os.path.join(path, filename)
        if not os.path.exists(path):
            os.makedirs(path)
        if os.path.exists(file):
            if os.path.getsize(file) == 0:
                os.remove(file)
            else:
                continue
        print('###########################')
        print('get ERA data for', today)
        print('###########################')
        try:
            with redirect_stdout(ECMWFio()):
                if level_type == 'ml':
                    ret = retrieve_ml_single_and_multi_level_for_day(today)
                elif level_type == 'pl':
                    ret = retrieve_pl_for_day(today)
                ret.to_netcdf(file)
        except Exception as e:
            print('There was an ECMWF Data Server exception')
            print(type(e))
            print(e)
            quit()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    retrieve_days(dt.date(2019, 7, 1), dt.date(2019, 9, 1))
