import folium
import geopandas as gpd
import json

def create_map(gdf: gpd.GeoDataFrame, df, config, output_path: str):
    geo_key = config.geo_join_key
    csv_key = config.csv_join_key
    
    # Merge geographic data with tabular data
    merged = gdf.merge(df, left_on=geo_key, right_on=csv_key, how='left')
    
    # Ensure merged is a GeoDataFrame after merging
    if not isinstance(merged, gpd.GeoDataFrame):
        merged = gpd.GeoDataFrame(merged, geometry='geometry')
    
    # Reproject to Web Mercator for proper folium representation if needed, though Folium assumes WGS84
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
        choropleth = folium.Choropleth(
            geo_data=merged.__geo_interface__,
            data=merged,
            columns=[geo_key, value_col],
            key_on=f"feature.properties.{geo_key}",
            fill_color='YlGnBu',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=config.title,
            highlight=True
        ).add_to(m)
        
        # In order for tooltip to work properly, properties must be injected back
        # Since folium.Choropleth passes only limited info, we add a transparent GeoJson layer for tooltips
        
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
            tooltip=tooltip,
            style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent'}
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
        
    m.save(output_path)
    print(f"Map successfully generated and saved to {output_path}")
