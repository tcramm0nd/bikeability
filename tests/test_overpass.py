import pytest
from bikeability import overpass

@pytest.fixture
def example_query():
    return """[out:"json"];area(3600188553)->.a;way[highway=cycleway](area.a);out geom;"""

@pytest.fixture
def bike_query():
    return ['way[highway=cycleway](area.a);', 'Pittsburgh']

# @pytest.fixture
# def 

def test_query_builder(example_query):
    built = overpass.API()._query_builder('way[highway=cycleway](area.a);', area_id=188553)
    assert built == example_query
    
def test_get(bike_query):
    results = overpass.API().get('way[highway=cycleway](area.a);', area_id=188553)
    assert len(results) == 326
    assert len(results.columns) == 58
    assert 'geometry' in results.columns

@pytest.mark.parametrize('values,expected',
                         [([{'lat': 40.46761, 'lon': -79.9281859}, {'lat': 40.4672051, 'lon': -79.9284323}], 49.580459793082234),
                          ([{'lat': 40.46761, 'lon': -79.9281859}], 0)])
def test_coords(values, expected):
    assert overpass.length(values) == expected
    

    

    
