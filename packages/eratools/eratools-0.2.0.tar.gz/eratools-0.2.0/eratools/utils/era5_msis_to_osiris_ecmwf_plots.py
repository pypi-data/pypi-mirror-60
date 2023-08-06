import xarray as xr
import os
import datetime as dt

from scipy.interpolate import interp1d
from scipy.io import loadmat  # this is the SciPy module that loads mat-files
import pandas as pd


scandb = loadmat('/media/odp/OsirisConfigurationDatabase/flightduration/scandatabase/matlabscandatabase.mat')
mdata = scandb['scandatabase']
mdtype = mdata.dtype  # dtypes of structures are "unsized objects"
ndata = {n: mdata[n][0, 0] for n in mdtype.names}
df = pd.DataFrame.from_dict({k: ndata[k].flatten() for k in ndata}).set_index('scannum')
df.index.name = 'ScanNo'
scandb = xr.Dataset.from_dataframe(df)
scandb = scandb.rename({'mjd': 'MJD'})

path = '/media/valhalla/data/OSIRIS/50722/'
starttime = dt.datetime(2019, 9, 1).timestamp()

files = [file for file in os.scandir(path)
         if file.name.endswith('.h5') and file.name.startswith('OSIRIS_L2_') and file.stat().st_mtime > starttime]

d = {}
for scan in db20.ScanNo.where(db20.sza < 89.7, drop=True)[:10]:
    try:
        spect = open_level1_spectrograph(scan)
        print(f'{scan}')
        d[scan] = [db20.sel(ScanNo=scan).longitude.item(), db20.sel(ScanNo=scan).latitude.item()]
    except:
        pass


import msise00
from osirisl1services.readlevel1 import open_level1_ecmwf
from osirisl1services.services import get_orbit_number
from astropy.time import Time
from osirisl1services.pyhdfadapter import HDF4VS
import datetime as dt
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

vs = HDF4VS('/media/valhalla/utls_backups/Level1/orbit/disk3/37400/se1_9241.ecm')
lats = vs['Osiris ECMWF']['latitude']
lons = vs['Osiris ECMWF']['longitude']
mjds = vs['Osiris ECMWF']['mjd']
int_msis90_density = np.array([vs['R8:R8:00221']['Array'][i[0]] for i in vs['Osiris ECMWF']['Density']])
int_msis90_temperature = np.array([vs['R8:R8:00221']['Array'][i[0]] for i in vs['Osiris ECMWF']['Temperature']])
int_msis90_pressure = int_msis90_density * int_msis90_temperature * 1.3806503e-19

res = []
for (lat, lon, mjd) in zip(lats, lons, mjds):
    t = Time(mjd, format='mjd')
    msis = msise00.run(time=t.datetime, altkm=np.arange(0, 110.5, .5), glat=lat, glon=lon)
    res.append(msis.squeeze())

res = xr.concat(res, dim='time')
res['temperature_int_msis90'] = xr.DataArray(int_msis90_temperature, dims=('time', 'alt_km'))
res['nd_int_msis90'] = xr.DataArray(int_msis90_density, dims=('time', 'alt_km'))
res['pressure_int_msis90'] = xr.DataArray(int_msis90_pressure, dims=('time', 'alt_km'))
res = res.where(res.lat >= -90., drop=True)
res['nd'] = (res.Total * 287.058 * 1e-2 / 1.3806503e-19)

# res.Total.plot(x='time', norm=LogNorm())

from eratools.accessor import ERAML
# era5 = xr.open_dataset('/media/ecmwf/2008/01/ERA5_ml_20080105.nc')
era5 = xr.open_dataset('/home/chris/ERA5_ml_20080105.nc')

def era5_pres_temp_nd_for_points(time, lat, lon, alt_grid):
    pres, temp, nd = [], [], []
    for (time, lat, lon, timei, lati, loni) in zip(time, lat, lon,
            np.searchsorted(era5.time.values, time) - 1,
            600 - np.searchsorted(era5.latitude.values[::-1], lat),
            np.searchsorted(era5.longitude.values, lon) - 1):
        era5i = era5.isel(time=slice(timei, timei + 2), latitude=slice(lati, lati + 2), longitude=slice(loni, loni + 2))
        era5i.era.extend()
        pres.append(era5i.era.pressureonalt(lat, lon, time, alt_grid))
        temp.append(era5i.era.temperatureonalt(lat, lon, time, alt_grid))
    pres = np.array(pres)
    temp = np.array(temp)
    nd = pres / temp / 1.3806503e-19
    # return np.array(nd)
    return pres, temp, nd

alts_era5 = np.arange(0, 80, .5)

pressure_era5, temperature_era5, nd_era5 = (x.assign_coords({'alt_km': alts_era5}) for x in xr.apply_ufunc(
    era5_pres_temp_nd_for_points, res.time, res.lat, res.lon,
    input_core_dims=(['time'], ['time'], ['time']),
    output_core_dims=[('time', 'alt_km'), ('time', 'alt_km'), ('time', 'alt_km')],
    kwargs={'alt_grid': 1000. * alts_era5}))

pressure_era5.name = 'pressure_era5'
temperature_era5.name = 'temperature_era5'
nd_era5.name = 'nd_era5'

res = xr.merge((res, pressure_era5, temperature_era5, nd_era5))


from osirisl1services.readlevel1 import open_level1_attitude, open_level1_spectrograph
for orbit in range(100371, 140000):
    try:
        att = open_level1_attitude(orbit, load_pointing=True)
        break
    except:
        continue


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
    return era5.load()

era5 = load_era5_data(att.StartMJD.min().item(), att.EndMJD.max().item())


def era5_pres_temp_nd_for_point(time, lat, lon, alt_grid):
    timei = np.searchsorted(era5.time.values, time) - 1
    lati = 600 - np.searchsorted(era5.latitude.values[::-1], lat)
    loni = np.searchsorted(era5.longitude.values, lon) - 1
    era5i = era5.isel(time=slice(timei, timei + 2), latitude=slice(lati, lati + 2), longitude=slice(loni, loni + 2))
    era5i.era.extend()
    pres = era5i.era.pressureonalt(lat, lon, time, alt_grid)
    temp = era5i.era.temperatureonalt(lat, lon, time, alt_grid)
    nd = pres / temp / 1.3806503e-19
    # return np.array(nd)
    return temp, nd

from pyhdf.HDF import *
from pyhdf.VS import *

# Open HDF file and initialize the VS interface
hdf = HDF(os.path.join(os.environ['ODINORBITDIR'], 'disk3', f'{orbit // 100:03}00', f'se2_{orbit:04x}.ecm'),
        HC.WRITE | HC.CREATE)
vs = hdf.vstart()

# Create vdata and define its structure
vd_info = vs.create(  # create a new vdata
    'Osiris ECMWF',  # name of the vdata
    # fields of the vdata follow
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

vd_data = vs.create(  # create a new vdata
    'R8:R8:00221',  # name of the vdata
    # fields of the vdata follow
    (('crosscheck', HC.UINT32, 1),
     ('Array', HC.FLOAT64, 221)))


i = 0
for scan, info in att.groupby('ScanNumber'):
    try:
        spect = open_level1_spectrograph(scan, valid=False)
    except:
        continue
    print(f'{scan}')
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
# res.temperature_era5.plot(x='time', figsize=(6, 6), vmin=140, vmax=320)
# xr.where(res.temperature_era5.isnull(), res.Tn, res.temperature_era5).plot(x='time', figsize=(6, 6), vmin=140, vmax=320)
# res.Tn.plot(x='time', figsize=(6, 6), vmin=140, vmax=320)
# res.temperature_int_msis90.plot(x='time', figsize=(6, 6), vmin=140, vmax=320)
# (xr.where(res.temperature_era5.isnull(), res.Tn, res.temperature_era5) - res.temperature_int_msis90).plot(x='time', figsize=(6, 6))
#
# from matplotlib.colors import LogNorm, SymLogNorm
#
# # res.nd_era5.plot(x='time', figsize=(6, 6), norm=LogNorm(vmin=1e14, vmax=4e19))
# xr.where(res.nd_era5.isnull(), res.nd, res.nd_era5).plot(x='time', figsize=(6, 6), norm=LogNorm(vmin=1e14, vmax=4e19))
# # res.nd.plot(x='time', figsize=(6, 6), norm=LogNorm(vmin=1e14, vmax=4e19))
# res.nd_int_msis90.plot(x='time', figsize=(6, 6), norm=LogNorm(vmin=1e14, vmax=4e19))
# (xr.where(res.nd_era5.isnull(), res.nd, res.nd_era5) / res.nd_int_msis90).plot(x='time', figsize=(6, 6), vmin=0.9, vmax=1.1)

res.temperature_era5.loc[{'alt_km': slice(90, None)}] = res.Tn.loc[{'alt_km': slice(90, None)}]
res['temperature_era5'] = res.temperature_era5.interpolate_na(dim='alt_km')
res['temperature_era5'] = xr.where(res.temperature_era5.isnull(), res.Tn, res.temperature_era5)

res.nd_era5.loc[{'alt_km': slice(90, None)}] = res.nd.loc[{'alt_km': slice(90, None)}]
res['nd_era5'] = res.nd_era5.interpolate_na(dim='alt_km')
res['nd_era5'] = xr.where(res.nd_era5.isnull(), res.nd, res.nd_era5)



time_indices = np.searchsorted(era5.time.values, res.time) - 1
lat_indices = 600 - np.searchsorted(era5.latitude.values[::-1], res.lat)
lon_indices = np.searchsorted(era5.longitude.values, res.lon) - 1


fig_a, ax_a = plt.subplots(ncols=2)
fig_b, ax_b = plt.subplots(ncols=2)
for (time, lat, lon, time_index, lat_index, lon_index,
     im_nd, im_temp, m0_nd, m0_temp) \
        in zip(res.time.values, res.lat.values, res.lon.values,
               time_indices, lat_indices, lon_indices,
               int_msis90_density, int_msis90_temperature,
               res.Total.values * 287.058 * 1e-2 / 1.3806503e-19, res.Tn.values):
    sub = era5.isel(time=slice(time_index, time_index + 2),
                    latitude=slice(lat_index, lat_index + 2),
                    longitude=slice(lon_index, lon_index + 2))
    sub.era.extend()
    pres = sub.era.pressureonalt(lat, lon, time, np.arange(0, 110500, 500))
    temp = sub.era.temperatureonalt(lat, lon, time, np.arange(0, 110500, 500))
    nd = pres / temp / 1.3806503e-19

    ax_a[0].set_prop_cycle(None)
    ax_a[0].plot(nd / im_nd, np.arange(0, 110.5, .5), alpha=0.4)
    ax_a[0].plot(m0_nd / im_nd, np.arange(0, 110.5, .5), alpha=0.4)
    ax_a[1].set_prop_cycle(None)
    ax_a[1].plot(temp - im_temp, np.arange(0., 110.5, .5), alpha=0.4)
    ax_a[1].plot(m0_temp - im_temp, np.arange(0., 110.5, .5), alpha=0.4)

    ax_b[0].set_prop_cycle(None)
    ax_b[0].semilogx(nd, np.arange(0, 110.5, .5), alpha=0.4)
    ax_b[0].semilogx(m0_nd, np.arange(0, 110.5, .5), alpha=0.4)
    ax_b[0].semilogx(im_nd, np.arange(0, 110.5, .5), alpha=0.4)
    ax_b[1].set_prop_cycle(None)
    ax_b[1].plot(temp, np.arange(0., 110.5, .5), alpha=0.4)
    ax_b[1].plot(m0_temp, np.arange(0., 110.5, .5), alpha=0.4)
    ax_b[1].plot(im_temp, np.arange(0., 110.5, .5), alpha=0.4)

fig_a.suptitle('Comparisons with Current ERA-Interim / MSIS90 Profiles')
ax_a[0].set_title('Number Density')
ax_a[0].set_xlabel('Ratio')
ax_a[0].set_ylabel('Altitude [km]')
ax_a[1].set_title('Temperature')
ax_a[1].set_xlabel('Difference')
ax_a[0].legend(['ERA5', 'MSISE00'])
fig_a.savefig('/home/chris/OSIRIS_nd_temp_comparisons.png', dpi=300)

fig_b.suptitle('Current ERA-Interim / MSIS90 Profiles and ERA5 and MSISE00 Profiles')
ax_b[0].set_xlabel('Number Density')
ax_b[0].set_ylabel('Altitude [km]')
ax_b[1].set_xlabel('Temperature')
ax_b[0].legend(['ERA5', 'MSISE00', 'Current'])
fig_b.savefig('/home/chris/OSIRIS_nd_temp_profiles.png', dpi=300)
