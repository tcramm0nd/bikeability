from bikeability import overpass
import pandas as pd
import datetime as dt
import csv

                   
cities = {'Seattle':237385,
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


class OSM_retriever():
    road_query = """(
                    way[highway=primary](area.a);
                    way[highway=primary_link](area.a);
                    way[highway=residential](area.a);
                    way[highway=secondary](area.a);
                    way[highway=secondary_link](area.a);
                    way[highway=tertiary](area.a);
                    way[highway=tertiary_link](area.a);
                    way[highway=trunk](area.a);
                    way[highway=trunk_link](area.a);
                    way[highway=unclassified](area.a);
                    
                    );"""
    
    cycle_query = """(way[highway=cycleway](area.a);way[cycleway=lane](area.a);
                   way[cycleway=asl](area.a);way[cycleway=bike_box](area.a);
                   way[cycleway=crossing](area.a);way[cycleway=opposite_lane](area.a);
                   way[cycleway=opposite_track](area.a);way[cycleway=separate](area.a);
                   way[cycleway=sidepath](area.a);way[cycleway=track](area.a);
                   way[bicycle=designated](area.a);way[bicycle=yes](area.a);
                   way[bicycle_road=yes](area.a);
                   );"""
                   
    def __init__(self, query_type, cities, query_format=None):
        self.available_cities = self._load_cities()
        self.query_type = self._get_query(query_type)
        self.cities = self._get_cities(cities)
        self.query_format = self._get_format(query_format)
        
    def get(self):
        api = overpass.API()
        results = {}
        for city, relation_id in self.cities.items():
            df = api.get(self.cycle_query, area_id=relation_id)
            df['city'] = city
            df['length'] = df['geometry'].apply(overpass.length)
            results[city] = df
        self.raw_data = pd.concat(results.values(), sort=False)
        self.raw_data.reset_index(inplace=True)
        return self.raw_data
    
    def save(self, filename=None):
        if filename:
            self.raw_data.to_json(filename)
        else:
            date = str(dt.date.today())
            filename = f'{date}_raw_data.json'
            self.raw_data.to_json(filename)
    
    def _get_query(self, query_type):
        if query_type == 'bikes':
            return self.cycle_query
        elif query_type == 'roads':
            return self.road_query
        else:
            raise ValueError(query_type)
        
    def _get_cities(self, cities):
        osm_cities = {}
        if isinstance(cities, str):
            input_type = 'string'
        else:
            input_type = 'iterable'
                 
        if input_type == 'string':
            try:
                osm_cities[cities] = int(self.available_cities[cities])
            except KeyError:
                print(f'Queries for {cities} not yet supported')
        else:
            for c in cities:
                try:
                    osm_cities[c] = int(self.available_cities[c])
                except KeyError:
                    print(f'Queries for {cities} not yet supported')
                    
        return osm_cities
        
    def _get_format(self, query_format):
        return 'All'
        
    def _load_cities(self):
        try:
            with open('OSM_Relation_ID - list.csv', 'r') as f:
                reader = csv.reader(f)
                available = {rows[1]:rows[2] for rows in reader if rows[2] != ''}
        except FileNotFoundError as e:
            print(e)
        return available     
        