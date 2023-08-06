import os
import msise00
from astropy.time import Time
import datetime as dt
import xarray as xr
import numpy as np
from scipy.interpolate import interp1d
from pyhdf.HDF import *
from pyhdf.VS import *
from osirisl1services.readlevel1 import open_level1_attitude, open_level1_spectrograph
from osirisl1services.services import Level1Services
from eratools.accessor import ERAML


def load_era5_data(mjd_start, mjd_end):
    t_start = Time(mjd_start, format='mjd').datetime - dt.timedelta(hours=1)
    t_end = Time(mjd_end, format='mjd').datetime + dt.timedelta(hours=1)
    if t_start.date() == t_end.date():
        era5 = xr.open_dataset(os.path.join(os.environ['ERA5_DATA_DIR'], f'{t_start.year}', f'{t_start.month:02}',
                                            f'ERA5_ml_{t_start.year}{t_start.month:02}{t_start.day:02}.nc'))
    else:
        era5 = xr.open_mfdataset([os.path.join(os.environ['ERA5_DATA_DIR'], f'{t_start.year}', f'{t_start.month:02}',
                                               f'ERA5_ml_{t_start.year}{t_start.month:02}{t_start.day:02}.nc'),
                                  os.path.join(os.environ['ERA5_DATA_DIR'], f'{t_end.year}', f'{t_end.month:02}',
                                               f'ERA5_ml_{t_end.year}{t_end.month:02}{t_end.day:02}.nc')],
                                 concat_dim='time')
    era5 = era5.sel(time=slice(t_start, t_end))
    return era5


def era5_pres_temp_nd_for_point(time, lat, lon, alt_grid):
    timei = np.searchsorted(era5.time.values, time) - 1
    lati = 600 - np.searchsorted(era5.latitude.values[::-1], lat)
    loni = np.searchsorted(era5.longitude.values, lon) - 1
    era5i = era5.isel(time=slice(timei, timei + 2), latitude=slice(lati, lati + 2), longitude=slice(loni, loni + 2))
    era5i.era.extend()
    pres = era5i.era.pressureonalt(lat, lon, time, alt_grid)
    temp = era5i.era.temperatureonalt(lat, lon, time, alt_grid)
    nd = pres / temp / 1.3806503e-19
    return temp, nd

# for orbit in range(100371, 140000):
for orbit in range(100780, 140000):
    try:
        att = open_level1_attitude(orbit, load_pointing=True)
        print(f'Processing orbit {orbit}')
        era5 = None

        hdf = HDF(os.path.join(os.environ['ODINORBITDIR'], 'disk3', f'{orbit // 100:03}00', f'se2_{orbit:04x}.ecm'),
                  HC.WRITE | HC.CREATE | HC.TRUNC)

        vs = hdf.vstart()
        vd_info = vs.create('Osiris ECMWF',
                            (('mjdofscan', HC.FLOAT64, 1),
                             ('mjdofendscan', HC.FLOAT64, 1),
                             ('mjd', HC.FLOAT64, 1),
                             ('latitude', HC.FLOAT64, 1),
                             ('longitude', HC.FLOAT64, 1),
                             ('ecmwf_minalt', HC.FLOAT64, 1),
                             ('ecmwf_maxalt', HC.FLOAT64, 1),
                             ('ScanNumber', HC.UINT32, 1),
                             ('NumAltitudes', HC.INT32, 1),
                             ('altitudes', HC.UINT32, 4),
                             ('Density', HC.UINT32, 4),
                             ('Temperature', HC.UINT32, 4)))

        vd_data = vs.create('R8:R8:00221', (('crosscheck', HC.UINT32, 1), ('Array', HC.FLOAT64, 221)))

        i = 0
        for scan, info in att.groupby('ScanNumber'):
            try:
                spect = open_level1_spectrograph(scan, valid=False)
            except:
                continue
            print(f'{scan}')
            if era5 is None:
                era5 = load_era5_data(att.StartMJD.min().item(), att.EndMJD.max().item())
            alts = spect.l1.altitude.values
            mjd = interp1d(alts, spect.mjd.values)(30000).item()
            t = Time(mjd, format='mjd')
            latitude = spect.l1.latitude.interp(mjd=mjd).item()
            longitude = spect.l1.longitude.interp(mjd=mjd).item()
            temperature_era5, nd_era5\
                = era5_pres_temp_nd_for_point(t.datetime64, latitude, longitude % 360, np.arange(0., 80000., 500.))
            msis = msise00.run(time=t.datetime, altkm=np.arange(0, 110.5, .5), glat=latitude, glon=longitude).squeeze()
            msis['nd'] = (msis.Total * 287.058 * 1e-2 / 1.3806503e-19)
            msis['temperature_era5'] = xr.DataArray(temperature_era5, coords=[('alt_km', np.arange(0., 80., .5))])
            msis['nd_era5'] = xr.DataArray(nd_era5, coords=[('alt_km', np.arange(0., 80., .5))])
            msis.temperature_era5.loc[{'alt_km': slice(90, None)}] = msis.Tn.loc[{'alt_km': slice(90, None)}]
            msis['temperature_era5'] = msis.temperature_era5.interpolate_na(dim='alt_km')
            msis['temperature_era5'] = xr.where(msis.temperature_era5.isnull(), msis.Tn, msis.temperature_era5)
            msis.nd_era5.loc[{'alt_km': slice(90, None)}] = msis.nd.loc[{'alt_km': slice(90, None)}]
            msis['nd_era5'] = np.exp(np.log(msis.nd_era5).interpolate_na(dim='alt_km'))
            msis['nd_era5'] = xr.where(msis.nd_era5.isnull(), msis.nd, msis.nd_era5)
            vd_info.write(((info.StartMJD.item(), info.EndMJD.item(), mjd, latitude, longitude, 0., 100000., int(scan), 221,
                            [3 * i, 221, 1, 5000 + i], [3 * i + 1, 221, 1, 5000 + 3 * i + 1],
                            [3 * i + 2, 221, 1, 5000 + 3 * i + 2]),))
            vd_data.write(((5000 + 3 * i, list(np.arange(0.0, 110500.0, 500.0))),
                           (5000 + 3 * i + 1, list(msis.nd_era5.values)),
                           (5000 + 3 * i + 2, list(msis.temperature_era5.values))))
            i += 1

        vd_info.detach()  # "close" the vdata
        vd_data.detach()

        vs.end()  # terminate the vdata interface
        hdf.close()

    except:
        continue
