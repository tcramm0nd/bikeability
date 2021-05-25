# bikeability

How bike-able is your city? Actually, what does that even mean? This is a collection of tools to get information on Bike-friendly routes of travel, and, hopefully, try to better understand what makes an urban area "Bike Friendly".

## components
There are several elements to this repo:
* tools for retrieving data (primarily from OSM)
* tools for cleaning and organizing data 
* tools for visualizing and comparing data
* Notebooks for a more user friendly/descriptive interface

## Getting Started
The easiest wayto get started is to jump into the `get_raw_data` notebook and download some OSM data. Right now the top 50 most populous cities in the US are supported. The notebook is set up to apply some basic cleaning focused on removing any of the ancillary data; when using OSM this can balloon out quite quickly.

The data cleaning is mostly contained in the notebook to allow the user to adjust as they see fit.