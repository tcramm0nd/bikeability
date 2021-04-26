import geojson
import pandas as pd
import requests
from geopy.distance import distance
import time
    
class API():
    ENDPOINT = 'https://overpass-api.de/api/interpreter'
    TIME_OUT = 25
    OUTPUT = 'json'
    VERBOSITY = 'geom'
    
    def __init__(self, **kwargs):
        self.endpoint = kwargs.get("endpoint", self.ENDPOINT)
        self.time_out = kwargs.get('endpoint', self.TIME_OUT)
        
        self.attempts = 0
        self.total_time = 0
        self.total_entries_retrieved = 0
        
    def get(self, search_terms, df=True,**kwargs):
        self.output = kwargs.get("output", self.OUTPUT)
        self.verbosity = kwargs.get("verbosity", self.VERBOSITY)
        
        # build a hierarchy and selection method to return the bounds/area to 
        # search within
        city = kwargs.get('city', None)
        admin_level = kwargs.get('admin_level', None)
        area_query = kwargs.get('area_query', None)
        area_id = kwargs.get('area_id', None)

        params ={'data': self._query_builder(search_terms, area_id)}
        
        start = time.perf_counter()
        
        data = self._get(params)
        
        stop = time.perf_counter()
        
        self.total_time += (stop - start)
        self.total_entries_retrieved += len(data)
        
        print(f'Retrieved {len(data)} entries from area: {area_id}\n\tTime: {stop-start:0.2f} seconds\n\tAttempts: {self.attempts}')
        self.attempts = 0
        
        if df:
            return pd.json_normalize(data)
        else:
            return data
        
        
    def _get(self, params):
        self.attempts += 1
        try:
            r = requests.get(self.endpoint, params)
        except requests.exceptions.RequestException as error:
            raise SystemExit(error)
        
        if r.status_code == 429:
            time.sleep(self.attempts/2)
            data = self._get(params)
        elif r.status_code != 200:
            print(f'failed with {r.status_code}')
        else:
            data = r.json()['elements']   
            
        return data
            
    # def _query_builder(self, search_terms, area_query=None, area_id=None, city=None, admin_level=None):

    #     output = f"""[out:"{self.output}"];"""
    #     if area_query:
    #         area = area_query
    #     elif area_id:
    #         area_id = 3600000000 + area_id
    #         area = f'''area({area_id})->.a;'''
    #     elif city and admin_level:
    #         area = f'''area["name"="{city}"]["admin_level"="{admin_level}"]->.a;'''
    #     elif city and not admin_level:
    #         area = f'''area["name"="{city}"]->.a;'''
    #     else:
    #         raise Exception('No search bounding box supplied')
    #     verbosity = f'''out {self. verbosity};'''
    #     return output + area + search_terms + verbosity
            
    def _query_builder(self, search_terms, area_id):

        output = f"""[out:"{self.output}"];"""
        area_id = 3600000000 + area_id
        area = f'''area({area_id})->.a;'''
        verbosity = f'''out {self. verbosity};'''
        return output + area + search_terms + verbosity            
            
def length(geometry):
    if len(geometry) < 2:
        return 0
    else:
        coords = [(c['lat'], c['lon']) for c in geometry]
        length = 0
        for i in range(0,len(coords)-1):
            length += distance(coords[i], coords[i+1]).m
        return length

def check_bounds(min_lat, min_lon, max_lat, max_lon):
    d = distance((min_lat, min_lon), (max_lat, max_lon)).km
    print(d)
    if  d > 100:
        print('City is incorrect, please provide more details')




most_populous_cities = {'New York': 175905,
                        'Los Angeles': 207359,
                        'Chicago': 122604,
                        'Houston': 2688911,
                        'Phoenix': 111257,
                        'Philadelphia': 188022,
                        'San Antonio': 253556,
                        'San Diego': 253832,
                        'Dalls': 6571629,
                        'San Jose': 112143
                        }

top_cycling_cities = {'Seattle':237385,
                      'San Francisco': 111968,
                      'Fort Collins': 112524,
                      'Minneapolis': 136712,
                      'Portland': 186579,
                      'Chicago': 122604,
                      'Eugene': 186706,
                      'Madison': 3352040,
                      'New York': 175905,
                      'Cambridge': 1933745
                      }

cycle_query = """(way[highway=cycleway](area.a);way[cycleway=lane](area.a);
                   way[cycleway=asl](area.a);way[cycleway=bike_box](area.a);
                   way[cycleway=crossing](area.a);way[cycleway=opposite_lane](area.a);
                   way[cycleway=opposite_track](area.a);way[cycleway=separate](area.a);
                   way[cycleway=sidepath](area.a);way[cycleway=track](area.a);
                   way[bicycle=designated](area.a);way[bicycle=yes](area.a);
                   way[bicycle_road=yes](area.a);
                   );"""