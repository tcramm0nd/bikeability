import re

import numpy as np
import pandas as pd
from geopy.distance import distance

def clean(df):
    # df = clean_column_names(df)
    df['nodecount'] = df['nodes'].apply(len)
    df['geometry'] = df['geometry'].apply(clean_geometry)
    df['length'] = df['geometry'].apply(calculate_length)
    df = mph_filler(df)
    return df

def clean_column_names(df):
    columns = df.columns
    columns = [c.replace('tags.', '') for c in columns]
    # df.columns = columns
    # df.reset_index(inplace=True)
    return df

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
    
def mph_cleaner(mph_string):
    if not mph_string:
        return None
    else:
        mph_string = str(mph_string)
    pattern = re.compile(r'^\d{1,2}')
    mph_int = pattern.search(mph_string)
    if mph_int:
        mph = mph_int[0]
        if int(mph[-1]) !=8:
            mph = int(mph)
            rounded_mph = round(5 * round(mph/5))
        else:
             rounded_mph = int(mph)
    else:
        return None
                         

    return int(rounded_mph)

def mph_filler(df):
    if 'maxspeed' in df.columns:
        df['speedlimit'] = df['tags.maxspeed'].apply(mph_cleaner)
        df['speedlimit'] = df.groupby('tagshighway')['speedlimit'].apply(lambda grp: grp.fillna(np.mean(grp)))
        df['speedlimit'] = df['speedlimit'].apply(mph_cleaner)
        return df
    else:
        return df
    