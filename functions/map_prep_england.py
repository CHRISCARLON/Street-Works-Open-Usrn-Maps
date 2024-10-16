import folium
import geopandas as gpd
from branca.colormap import LinearColormap
from streamlit_folium import folium_static
from loguru import logger

def plot_map_england(geodf):
    """
    Takes in a geodataframe for a specific highway and plots a folium map centered on the UK.
    Applies a colourmap so that roads are colored based on their total_impact_score.
    """
    try:
        # Check if input is a GeoDataFrame
        if not isinstance(geodf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame")

        # Check if required columns exist
        required_columns = ['usrn', 'total_impact_level', 'street_name', 'geometry']
        missing_columns = [col for col in required_columns if col not in geodf.columns]
        if missing_columns:
            raise ValueError(f"Missing key columns: {', '.join(missing_columns)}")

        # Set UK coordinates (centered approximately on the UK)
        uk_coords = [54.5, -4.0]

        # Create a map centered on the UK
        m = folium.Map(location=uk_coords, zoom_start=6, tiles="cartodbpositron")

        # Create a green color map
        colors = [
            '#91cf60',  # Light green
            '#fc8d59',  # Orange
            '#d73027'   # Red
        ]

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
