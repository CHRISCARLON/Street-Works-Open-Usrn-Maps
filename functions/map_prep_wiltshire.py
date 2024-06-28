import folium
from streamlit_folium import folium_static
import osmnx as ox
import geopandas as gpd
import pandas as pd

def add_wiltshire_and_bristol_boundary(m):
    # Fetch Wiltshire and Bristol boundaries
    wiltshire = ox.geocode_to_gdf('Wiltshire, England')
    bristol = ox.geocode_to_gdf('Bristol, England')

    # Combine the GeoDataFrames
    combined = gpd.GeoDataFrame(pd.concat([wiltshire, bristol], ignore_index=True))

    # Add to map
    folium.GeoJson(
        combined,
        style_function=lambda x: {'fillColor': 'none', 'color': 'black', 'weight': 3}
    ).add_to(m)

def plot_map_wiltshire(geodf, selected_activities):
    # Set Wiltshire coordinates
    wiltshire_coords = [51.0688, -1.8004]

    # Create a map centered on Wiltshire
    m = folium.Map(location=wiltshire_coords, zoom_start=9)

    # Add Wiltshire boundary
    add_wiltshire_and_bristol_boundary(m)

    color_palette = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]

    # Create a dictionary to map work activity types to colors
    activity_types = geodf['activity_type'].unique()
    color_dict = {activity: color_palette[i % len(color_palette)] for i, activity in enumerate(activity_types)}

    # Add geometries to the map
    for _, row in geodf.iterrows():
        if row.geometry is not None and row['activity_type'] in selected_activities:
            color = color_dict.get(row['activity_type'], 'gray')
            # Create tooltip content with new lines
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

    # Use folium_static to display the map in Streamlit
    folium_static(m, width=1000, height=600)
