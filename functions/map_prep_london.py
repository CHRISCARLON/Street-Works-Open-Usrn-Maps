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
    Takes in a geo-dataframe for a specific highway and plots folium map with a green color scheme
    """
    try:
        # Check if input is a GeoDataFrame
        if not isinstance(geodf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame")

        # Check if key columns exist
        required_columns = ['usrn', 'total_impact_level', 'street_name', 'geometry']
        missing_columns = [col for col in required_columns if col not in geodf.columns]
        if missing_columns:
            raise ValueError(f"Missing key columns: {', '.join(missing_columns)}")

        # Set London coordinates
        london_coords = [51.5074, -0.1278]

        # Create a map centered on London
        m = folium.Map(location=london_coords, zoom_start=10, tiles="cartodbpositron")

        # Add London boundary
        add_london_boundary(m)

        # Create a green color map
        colors = ['#e6f3e6', '#c2e0c2', '#9fce9f', '#7cbc7c', '#ffcc80',
                  '#ffb366', '#ff944d', '#ff7733', '#ff5500', '#e64d00', '#cc4400']

        # Calculate min and max scores for the current highway
        min_score = float(geodf['total_impact_level'].min())
        max_score = float(geodf['total_impact_level'].max())

        # Create a color map based on the total "Acute & Legacy Impact Score" for the current highway
        colormap = LinearColormap(colors=colors, vmin=min_score, vmax=max_score)

        # Add geometries to the map
        for _, row in geodf.iterrows():
            if row.geometry is not None and not row.geometry.is_empty:
                score = float(row['total_impact_level'])
                color = colormap(score)
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
        colormap.caption = f"Total Impact Score (Range: {min_score:.2f} - {max_score:.2f})"

        # Use folium_static to display the map in Streamlit
        return folium_static(m, width=1000, height=600)

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise
