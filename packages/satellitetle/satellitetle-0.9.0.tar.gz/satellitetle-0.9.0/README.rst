============
satellitetle
============

The python package satellitetle_ provides functions to fetch TLEs from various
online sources (currently CelesTrak (SatNOGS), CalPoly and AMSAT) and allows
using custom ones or Space-Track.org.

It was forked from the python package orbit_.

.. _satellitetle: https://gitlab.com/librespacefoundation/python-satellitetle
.. _orbit: http://github.com/seanherron/orbit


Usage
-----

Fetch TLEs for a single satellite from Celestrak:
::

 from satellite_tle import fetch_tle_from_celestrak

 norad_id_iss = 25544 # ISS (ZARYA)
 print(fetch_tle_from_celestrak(norad_id_iss))

Fetch a large set of TLEs for a list of satllites from all available sources:
::

 from satellite_tle import fetch_tles

 norad_ids = [25544, # ISS (ZARYA)
              4298,  # QIKCOM-1
              40379] # GRIFEX

 # Uses default sources
 tles = fetch_tles(norad_ids)

 for norad_id, (source, tle) in tles.items():
     print('{:5d} {:23s}: {:23s}'.format(norad_id, tle[0], source))

 sources = [
     ('CalPoly','http://mstl.atl.calpoly.edu/~ops/keps/kepler.txt'),
     ('Celestrak (active)','https://www.celestrak.com/NORAD/elements/active.txt')
 ]

 # Uses custom sources
 tles = fetch_tles(norad_ids, sources=sources)

 for norad_id, (source, tle) in tles.items():
     print('{:5d} {:23s}: {:23s}'.format(norad_id, tle[0], source))

 spacetrack_config= {
     'identity': 'my_username',
     'password': 'my_secret_password'
 }

 # Uses default sources and Space-Track.org
 tles = fetch_tles(norad_ids, spacetrack_config=spacetrack_config)

 for norad_id, (source, tle) in tles.items():
     print('{:5d} {:23s}: {:23s}'.format(norad_id, tle[0], source))

 # Uses only Space-Track.org
 tles = fetch_tles(norad_ids, sources=[], spacetrack_config=spacetrack_config)

 for norad_id, (source, tle) in tles.items():
     print('{:5d} {:23s}: {:23s}'.format(norad_id, tle[0], source))

 # Uses custom sources and Space-Track.org
 tles = fetch_tles(norad_ids, sources=sources, spacetrack_config=spacetrack_config)

 for norad_id, (source, tle) in tles.items():
     print('{:5d} {:23s}: {:23s}'.format(norad_id, tle[0], source))

NOTE: `fetch_tles` downloads the TLE sets from all known sources, so it should
only be used when fetching TLEs for a large set of satellites.

License
-------

MIT
