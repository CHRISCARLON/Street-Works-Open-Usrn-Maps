import folium
import osmnx as ox
import geopandas as gpd
from branca.colormap import LinearColormap
from streamlit_folium import folium_static
from loguru import logger

def add_london_boundary(m):
    """
    Takes in a folium map object
    and adds the London boundary using osmnx
    """
    # Fetch London boundary
    london = ox.geocode_to_gdf('Greater London, England')
    # Add to map
    folium.GeoJson(
        london,
        style_function=lambda x: {'fillColor': 'none', 'color': 'black', 'weight': 3}
    ).add_to(m)

def plot_map(geodf):
    """
    Takes in a geo-dataframe and plots folium map
    """
    try:
        # Check if input is a GeoDataFrame
        if not isinstance(geodf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame")

        # Check if key columns exist
        required_columns = ['usrn', 'Acute & Legacy Impact Score', 'street_name', 'geometry']
        missing_columns = [col for col in required_columns if col not in geodf.columns]
        if missing_columns:
            raise ValueError(f"Missing key columns: {', '.join(missing_columns)}")

        # Group by USRN and calculate total "Acute & Legacy Impact Score"
        grouped_scores = geodf.groupby('usrn')['Acute & Legacy Impact Score'].sum().reset_index()

        # Merge the grouped scores back to the original geodataframe
        geodf = geodf.merge(grouped_scores, on='usrn', suffixes=('', '_total'))

        # Set London coordinates
        london_coords = [51.5074, -0.1278]

        # Create a map centered on London
        m = folium.Map(location=london_coords, zoom_start=10, tiles="cartodbpositron")

        # Add London boundary
        add_london_boundary(m)

        # Create a color map based on the total "Acute & Legacy Impact Score"
        min_score = grouped_scores['Acute & Legacy Impact Score'].min()
        max_score = grouped_scores['Acute & Legacy Impact Score'].max()
        colormap = LinearColormap(colors=['green', 'yellow', 'red'], vmin=min_score, vmax=max_score)

        # Add geometries to the map
        for _, row in geodf.iterrows():
            if row.geometry is not None and not row.geometry.is_empty:
                score = row['Acute & Legacy Impact Score_total']
                color = colormap(score)
                # Create tooltip content with new lines
                tooltip_content = (
                    f"USRN: {row['usrn']}<br>"
                    f"Street Name: {row['street_name']}<br>"
                    f"<strong>Total Impact Score: {score:.2f}</strong>"
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

        # Add a color legend
        colormap.add_to(m)
        colormap.caption = "Total Impact Score"

        # Use folium_static to display the map in Streamlit
        return folium_static(m, width=1400, height=600)

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise
