import pandas as pd

from geopy.distance import distance

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