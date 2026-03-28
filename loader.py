import geopandas as gpd
import pandas as pd
import fiona

# Enable KML support for geopandas
fiona.drvsupport.supported_drivers['KML'] = 'rw'
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

def load_geodata(filepath, subarea_filter=None):
    ext = str(filepath).split('.')[-1].lower()
    
    if ext in ['kml', 'kmz']:
        gdf = gpd.read_file(filepath, driver='KML')
    else:
        gdf = gpd.read_file(filepath)

    if subarea_filter:
        for key, val in subarea_filter.items():
            if key in gdf.columns:
                gdf = gdf[gdf[key] == val]
            else:
                print(f"Warning: subarea_filter key '{key}' not found in geographic dataset.")
                
    return gdf

def load_csv(filepath):
    return pd.read_csv(filepath)
