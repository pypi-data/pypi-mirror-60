"""Geopotential Functions on WGS84 Reference Ellipsoid

This module contains code for converting Geopotential to Geometric and vice-versa on the WGS84 reference ellipsoid

"""
from numpy import sqrt, cos, sin, deg2rad


Rmax_WGS84 = 6378137
Rmin_WGS84 = Rmax_WGS84 * (1 - 1/298.257223563)


def _geoid_radius(latitude: float) -> float:
    """Calculates the GEOID radius at a given latitude

    Parameters
    ----------
    latitude : float
        Latitude (degrees)

    Returns
    -------
    R : float
        GEOID Radius (meters)
    """
    lat = deg2rad(latitude)
    return sqrt(1/(cos(lat) ** 2 / Rmax_WGS84 ** 2 + sin(lat) ** 2 / Rmin_WGS84 ** 2))


def geometric2geopotential(z: float, latitude: float) -> float:
    """Converts geometric height to geopoential height

    Parameters
    ----------
    z : float
        Geometric height (meters)
    latitude : float
        Latitude (degrees)

    Returns
    -------
    h : float
        Geopotential Height (meters) above the reference ellipsoid
    """
    twolat = deg2rad(2 * latitude)
    g = 9.80616 * (1 - 0.002637*cos(twolat) + 0.0000059*cos(twolat)**2)
    re = _geoid_radius(latitude)
    return z * g * re / (re + z)


def geopotential2geometric(h: float, latitude: float) -> float:
    """Converts geopoential height to geometric height

    Parameters
    ----------
    h : float
        Geopotential height (meters)
    latitude : float
        Latitude (degrees)

    Returns
    -------
    z : float
        Geometric Height (meters) above the reference ellipsoid
    """
    twolat = deg2rad(2 * latitude)
    g = 9.80616 * (1 - 0.002637*cos(twolat) + 0.0000059*cos(twolat)**2)
    re = _geoid_radius(latitude)
    return h * re / (g * re - h)
