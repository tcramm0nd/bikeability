import pandas as pd
def main():
    bike_lanes = pd.read_json('bikes.json')

    remove = ['motorway', 'trunk', 'motorway_link','trunk_link']
    bike_lanes.drop(bike_lanes.loc[(bike_lanes['tags.highway'].isin(remove)) & (bike_lanes['tags.cycleway'].isnull()) & (bike_lanes['tags.bicycle'] != 'designated')].index, inplace=True)

    remove_columns = ['index','type','tiger', 'bounds', 'source', 'note', 'ref', 'horse', 'maxweight',
                    'layer','name', 'description', 'lanes:']
    columns = bike_lanes.columns
    for r in remove_columns:
        columns = [c for c in columns if r not in c]

    bike_lanes = bike_lanes[columns]

    columns = bike_lanes.columns
    columns = [c.replace('tags.', '') for c in columns]
    bike_lanes.columns = columns

    # get search tearms programmatically
    search_terms = ['cycleway:', 'bicycle:']

    bike_lanes['cycleway'].fillna(bike_lanes['cycleway:right'], inplace=True)
    bike_lanes['cycleway'].fillna(bike_lanes['cycleway:left'], inplace=True)
    bike_lanes['cycleway'].fillna(bike_lanes['cycleway:buffer'], inplace=True)

    bike_lanes['bicycle'].fillna(bike_lanes['bicycle:designated'], inplace=True)
    bike_lanes.drop(columns=['cycleway:right', 'cycleway:left'],
                    inplace=True)

    bike_lanes = bike_lanes.loc[:, bike_lanes.isnull().mean() <=.8]
    bike_lanes.info(verbose=True)

if __name__ == '__main__':
    main()