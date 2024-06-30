import folium
import osmnx as ox
import geopandas as gpd
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from streamlit_folium import folium_static
from folium.plugins import HeatMap
from shapely.geometry import mapping

def add_wiltshire_and_bristol_boundary(m):
    # Fetch Wiltshire and Bristol boundaries
    wiltshire = ox.geocode_to_gdf('Wiltshire, England')

    # Add to map
    folium.GeoJson(
        wiltshire,
        style_function=lambda x: {'fillColor': 'none', 'color': 'black', 'weight': 3}
    ).add_to(m)

def plot_map_wiltshire(geodf, selected_activities):
    wiltshire_coords = [51.0688, -1.8004]
    m = folium.Map(location=wiltshire_coords, zoom_start=9, tiles="cartodbpositron")

    add_wiltshire_and_bristol_boundary(m)

    color_palette = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]

    activity_types = geodf['activity_type'].unique()
    color_dict = {activity: color_palette[i % len(color_palette)] for i, activity in enumerate(activity_types)}

    heat_data = []

    def extract_coords(geom):
        coords = []
        geom_type = geom['type']
        if geom_type == 'Point':
            coords.append((geom['coordinates'][1], geom['coordinates'][0]))
        elif geom_type in ['LineString', 'MultiPoint']:
            coords.extend((coord[1], coord[0]) for coord in geom['coordinates'])
        elif geom_type in ['Polygon', 'MultiLineString']:
            for ring in geom['coordinates']:
                coords.extend((coord[1], coord[0]) for coord in ring)
        elif geom_type == 'MultiPolygon':
            for polygon in geom['coordinates']:
                for ring in polygon:
                    coords.extend((coord[1], coord[0]) for coord in ring)
        return coords

    for _, row in geodf.iterrows():
        if row.geometry is not None and row['activity_type'] in selected_activities:
            color = color_dict.get(row['activity_type'], 'gray')

            tooltip_content = (
                f"Activity Type: {row['activity_type']}<br>"
                f"Work Category: {row.get('work_category', 'N/A')}<br>"
                f"Street Name: {row.get('street_name', 'N/A')}<br>"
                f"Traffic Sensitive: {row.get('is_traffic_sensitive', 'N/A')}<br>"
                f"TTRO Required: {row.get('is_ttro_required', 'N/A')}<br>"
                f"Collaboration: {row.get('collaborative_working', 'N/A')}<br>"
                f"Actual Start Date: {row.get('actual_start_date_time', 'N/A')}<br>"
                f"Actual End Date: {row.get('actual_end_date_time', 'N/A')}<br>"
                f"Work Promoter: {row.get('promoter_organisation', 'N/A')}"
            )

            folium.GeoJson(
                row.geometry.__geo_interface__,
                style_function=lambda x, color=color: {
                    'color': color,
                    'weight': 3,
                    'opacity': 0.7
                },
                tooltip=folium.Tooltip(tooltip_content)
            ).add_to(m)

            # Extract coordinates for heatmap
            geom_dict = mapping(row.geometry)
            coords = extract_coords(geom_dict)
            heat_data.extend([coord + (1,) for coord in coords])

    # Add heatmap layer
    HeatMap(heat_data, radius=15, blur=10, max_zoom=1, overlay=True).add_to(m)

    # Use folium_static to display the map in Streamlit
    folium_static(m, width=1150, height=600)

def transform_datetime(df):
    # Convert to datetime without creating a copy
    df["actual_end_date_time"] = pd.to_datetime(df["actual_end_date_time"])
    # Filter for 2024 data
    mask = df["actual_end_date_time"].dt.year == 2024
    # Create year_month column
    df.loc[mask, "year_month"] = df.loc[mask, "actual_end_date_time"].dt.to_period('M')
    return df[mask]

def table_prep_activity(geodf):
    table_df = geodf.groupby("activity_type")["year_month"].value_counts().unstack(fill_value=0)
    table_df = table_df.sort_values(by=table_df.columns.tolist(), ascending=False)
    table_df['Total'] = table_df.sum(axis=1)
    table_df = table_df.sort_values('Total', ascending=False)

    return st.table(table_df)

def table_prep_promoter(geodf):
    table_df = geodf.groupby("promoter_organisation")["year_month"].value_counts().unstack(fill_value=0)
    table_df = table_df.sort_values(by=table_df.columns.tolist(), ascending=False)
    table_df['Total'] = table_df.sum(axis=1)
    table_df = table_df.sort_values('Total', ascending=False)

    return st.table(table_df)
