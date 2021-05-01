import logging
import time

import requests

class API():
    ENDPOINT = 'https://overpass-api.de/api/interpreter'
    TIME_OUT = 25
    OUTPUT = 'json'
    VERBOSITY = 'geom'
    DEBUG = True
    
    def __init__(self, **kwargs):
        # Logging setup
        if self.DEBUG:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        
        self.endpoint = kwargs.get("endpoint", self.ENDPOINT)
        self.time_out = kwargs.get('endpoint', self.TIME_OUT)
        
        self.attempts = 0
        self.total_time = 0
        self.total_entries_retrieved = 0
        
    def get(self, search_terms, df=True,**kwargs):
        self.output = kwargs.get("output", self.OUTPUT)
        self.verbosity = kwargs.get("verbosity", self.VERBOSITY)
        
        self.bounds = self._get_bounds(kwargs)
        params ={'data': self._query_builder(search_terms, self.bounds)}
        data = self._get(params)

        return data
        
        
    def _get(self, params):
        start = time.perf_counter()
        attempts = 1

        try:
            r = requests.get(self.endpoint, params)
        except requests.exceptions.RequestException as error:
            raise SystemExit(error)
        
        if r.status_code == 429:
            time.sleep(self.attempts/2)
            data = self._get(params)
            attempts += 1
        elif r.status_code != 200:
            print(f'failed with {r.status_code}')
        else:
            data = r.json()['elements']
        
        stop = time.perf_counter()
        
        debug = f'\nRetrieved {len(data)} entries from area: {self.bounds}\n\tTime: {stop-start:0.2f} seconds\n\tAttempts: {attempts}'
        logging.debug(debug)
        
        return data
            
    def _query_builder(self, search_terms, area_id):

        output = f"""[out:"{self.output}"];"""
        area_id = 3600000000 + area_id
        area = f'''area({area_id})->.a;'''
        verbosity = f'''out {self. verbosity};'''
        return output + area + search_terms + verbosity
    
    def _get_bounds(self, kwargs):
        
        city = kwargs.get('city', None)
        admin_level = kwargs.get('admin_level', None)
        area_query = kwargs.get('area_query', None)
        area_id = kwargs.get('area_id', None)
        
        if area_id:
            return area_id
        elif city:
            if admin_level:
                return city + admin_level
            else:
                return city
        elif area_query:
            return area_query
        else:
            raise KeyError                