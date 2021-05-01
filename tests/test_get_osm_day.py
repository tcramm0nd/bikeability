import pytest
from bikeability import _get_osm_data

def test_bike_init():
    bike_test = _get_osm_data.OSM_retriever('bikes', 'Pittsburgh')
    