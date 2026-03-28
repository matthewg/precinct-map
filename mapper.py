import folium
import geopandas as gpd
import pandas as pd
import branca.colormap as cm
import json
import sys

def create_map(gdf: gpd.GeoDataFrame, df: pd.DataFrame, config, output_path: str):
    geo_key = config.geo_join_key
    csv_key = config.csv_join_key
    
    # Merge geographic data with tabular data
    merge_how = 'inner' if getattr(config, 'drop_unmatched_geo', True) else 'left'
    merged = gdf.merge(df, left_on=geo_key, right_on=csv_key, how=merge_how)
    
    # Ensure merged is a GeoDataFrame after merging
    if not isinstance(merged, gpd.GeoDataFrame):
        merged = gpd.GeoDataFrame(merged, geometry='geometry')
    
    # Reproject to Web Mercator for proper folium representation if needed
    if merged.crs != "EPSG:4326":
        merged = merged.to_crs("EPSG:4326")
        
    bounds = merged.total_bounds # [minx, miny, maxx, maxy]
    center_y = (bounds[1] + bounds[3]) / 2.0
    center_x = (bounds[0] + bounds[2]) / 2.0
    
    m = folium.Map(location=[center_y, center_x], tiles='OpenStreetMap')
    # Use fit_bounds to zoom exactly to the layer bounds
    m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
    
    value_col = config.value_column
    
    if value_col and value_col in merged.columns:
        if config.type == 'enum':
            # Map descriptions into the dataframe so tooltip can reference them
            desc_map = {k: v.get('description', k) for k, v in config.enum_mappings.items()}
            color_map = {k: v.get('color', '#cccccc') for k, v in config.enum_mappings.items()}
            
            merged['description'] = merged[value_col].map(desc_map).fillna(merged[value_col])
            
            def style_fn(feature):
                val = feature['properties'].get(value_col)
                return {'fillColor': color_map.get(val, '#cccccc'), 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}
        
        else: # numeric_open or numeric_closed
            min_color = config.numeric_colors.get('min_color', '#ffffcc')
            max_color = config.numeric_colors.get('max_color', '#800026')
            
            # Ensure the value column is numeric, coercing any parsing errors to NaN.
            # Strip common formatting characters that prevent correct parsing.
            cleaned = merged[value_col].astype(str).str.replace(r'[$,%]', '', regex=True)
            numeric_col = f"{value_col}_numeric"
            merged[numeric_col] = pd.to_numeric(cleaned, errors='coerce')
            
            if config.type == 'numeric_closed':
                vmin = config.numeric_bounds.get('min', merged[numeric_col].min())
                vmax = config.numeric_bounds.get('max', merged[numeric_col].max())
            else:
                vmin = merged[numeric_col].min()
                vmax = merged[numeric_col].max()
                
            colormap = cm.LinearColormap(colors=[min_color, max_color], vmin=vmin, vmax=vmax)
            colormap.caption = config.title
            m.add_child(colormap)
            
            def style_fn(feature):
                val = feature['properties'].get(numeric_col)
                
                # Attempt to properly cast string values in properties if needed
                if isinstance(val, str):
                    try:
                        val = float(val.replace(',', '').replace('$', '').replace('%', ''))
                    except ValueError:
                        val = None

                if pd.isna(val) or val is None:
                    return {'fillColor': '#cccccc', 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}
                return {'fillColor': colormap(val), 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}

        # Setup standard Tooltip 
        tooltip = folium.GeoJsonTooltip(
            fields=config.tooltips,
            aliases=[f"{f}: " for f in config.tooltips],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=800,
        )

        folium.GeoJson(
            merged,
            style_function=style_fn,
            name=config.title,
            tooltip=tooltip
        ).add_to(m)
        
    else:
        # Just simple map map with tooltips
        tooltip_fields = config.tooltips if config.tooltips else [geo_key]
        folium.GeoJson(
            merged,
            name="Precincts",
            tooltip=folium.GeoJsonTooltip(
                fields=tooltip_fields,
                aliases=[f"{f}: " for f in tooltip_fields]
            )
        ).add_to(m)
        
    if output_path == '-':
        print(m.get_root().render())
    else:
        m.save(output_path)
        print(f"Map successfully generated and saved to {output_path}", file=sys.stderr)
