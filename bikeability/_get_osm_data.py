import csv
import datetime as dt

import pandas as pd

from geopy.distance import distance

from bikeability import overpass
from bikeability import _data_utils


class OSM_retriever():
    ROAD_QUERY = """(
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
    
    CYCLE_QUERY = """(way[highway=cycleway](area.a);way[cycleway=lane](area.a);
                   way[cycleway=asl](area.a);way[cycleway=bike_box](area.a);
                   way[cycleway=crossing](area.a);way[cycleway=opposite_lane](area.a);
                   way[cycleway=opposite_track](area.a);way[cycleway=separate](area.a);
                   way[cycleway=sidepath](area.a);way[cycleway=track](area.a);
                   way[bicycle=designated](area.a);way[bicycle=yes](area.a);
                   way[bicycle_road=yes](area.a);
                   );"""
                   
    def __init__(self, query_type, cities='All', results_format='All'):
        self.available_cities = self._load_cities()
        self.query = self._get_query(query_type)
        self.cities = self._get_cities(cities)
        self.results_format = self._get_format(results_format)
        
    def get(self, clean=True):
        api = overpass.API()
        results = {}
        for city, relation_id in self.cities.items():
            df = pd.json_normalize(api.get(self.query, area_id=relation_id))
            df['city'] = city
            # put into data cleaner; only raw data should be returned
            if clean:
                # df = _data_utils.clean(df)
                df['geometry'] = df['geometry'].apply(_data_utils.clean_geometry)
                df['length'] = df['geometry'].apply(_data_utils.calculate_length)
                df = _data_utils.mph_filler(df)
                df = _data_utils.clean_column_names(df)
            results[city] = df
        print(results.keys())
        self.raw_data = pd.concat(results.values(), sort=False)
        print(self.raw_data['city'].unique())
        self.raw_data.reset_index(inplace=True)
        print(self.raw_data['city'].unique())
        # self.raw_data = _data_utils.clean_column_names(df)
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
            return self.CYCLE_QUERY
        elif query_type == 'roads':
            return self.ROAD_QUERY
        else:
            raise ValueError(query_type)
        
    def _get_cities(self, cities):
        osm_cities = {}
        # if cities.lower() == 'all':
        #     osm_cities = self.available_cities     
        # elif isinstance(cities, str):
        #     try:
        #         osm_cities[cities] = int(self.available_cities[cities])
        #     except KeyError:
        #         print(f'Queries for {cities} not yet supported')
        # else:
        #     for c in cities:
        #         try:
        #             osm_cities[c] = int(self.available_cities[c])
        #         except KeyError:
        #             print(f'Queries for {cities} not yet supported')
        if isinstance(cities, str):
            if cities.lower() == 'all':
                osm_cities = self.available_cities
            else:
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
        
    def _get_format(self, results_format):
        results_format = results_format.lower()
        if results_format == 'all':
            df_builder = self._all_builder
        elif results_format == 'attributes':
            df_builder = self._attribute_builder
        elif results_format == 'geomtery':
            df_builder = self._geomtry_builder
        else:
            raise ValueError('Format not currently supported')
        return df_builder
    
    def _all_builder(self):
        pass
    def _attribute_builder(self):
        pass
    def _geomtry_builder(self):
        pass
        
    def _load_cities(self):
        try:
            with open('OSM_Relation_ID - list.csv', 'r') as f:
                reader = csv.reader(f)
                available = {rows[1]:int(rows[2]) for rows in reader if rows[2] != ''}
        except FileNotFoundError as e:
            print(e)
        return available     

def clean_geometry(geometry):
    """[summary]

    Args:
        geometry ([type]): [description]

    Returns:
        [type]: [description]
    """
    coordinates = [(c['lat'], c['lon']) for c in geometry]
    
    return coordinates

def calculate_length(coordinates):
    if len(coordinates) < 2:
        return 0
    else:
        length = 0
        for i in range(0,len(coordinates)-1):
            length += distance(coordinates[i], coordinates[i+1]).m
        return length