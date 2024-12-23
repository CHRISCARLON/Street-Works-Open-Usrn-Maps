import folium
import geopandas as gpd
import streamlit as st
from .fetch_data import fetch_permit_details_england
from branca.colormap import LinearColormap
from streamlit_folium import folium_static
from loguru import logger

def plot_map_england(geodf):
    try:
        if not isinstance(geodf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame")
            
        # Get the highway authority from the geodataframe
        highway_authority = geodf['highway_authority'].iloc[0]
        
        # Get the bounds of all geometries in the geodataframe
        total_bounds = geodf.total_bounds
        
        # Create the map and set bounds to the highway authority area
        m = folium.Map(tiles="cartodbpositron")
        m.fit_bounds([[total_bounds[1], total_bounds[0]], [total_bounds[3], total_bounds[2]]])

        # Create colormap for impact scores
        min_score = float(geodf['total_impact_level'].min())
        max_score = float(geodf['total_impact_level'].max())
        colormap = LinearColormap(
            colors=['#F5F5F5', '#fc8d59', '#d73027'],
            vmin=min_score,
            vmax=max_score,
            caption=f"Total Impact Score (Range: {min_score:.2f} - {max_score:.2f})"
        )

        # Add features to map
        for _, row in geodf.iterrows():
            if row.geometry is not None and not row.geometry.is_empty:
                score = float(row['total_impact_level'])
                color = colormap(score)
                folium.GeoJson(
                    row.geometry.__geo_interface__,
                    style_function=lambda x, color=color: {
                        'color': color,
                        'weight': 3,
                        'opacity': 0.7
                    },
                    tooltip=folium.Tooltip(
                        f"Street Name: {row['street_name']}<br>"
                        f"USRN: {row['usrn']}<br>"
                        f"UPRN Count: {row['uprn_count']}<br>"
                        f"<strong>Total Impact Score: {score:.2f}</strong>"
                    )
                ).add_to(m)

        # Add the colormap legend to the map
        colormap.add_to(m)

        # Display map using folium_static
        folium_static(m, width=1100, height=600)

        # Street selection and permit details
        col_select, col_details = st.columns([1, 2])
        with col_select:
            st.markdown("### For Details Please Select a Street")
            street_usrn_map = geodf[['street_name', 'usrn']].drop_duplicates()
            street_names = [''] + sorted(street_usrn_map['street_name'].unique().tolist())
            selected_street = st.selectbox(
                "Street Name",
                options=street_names,
                format_func=lambda x: x if x else "Select a Street"
            )

        if selected_street:
            with col_details:
                permit_details = fetch_permit_details_england(
                    selected_street,
                    highway_authority
                )
                permit_details = permit_details.drop("date_processed", axis=1)
                if not permit_details.empty:
                    st.subheader(f"Showing Permit Details for {selected_street}")
                    st.dataframe(permit_details)
                else:
                    st.info(f"No permit details available for {selected_street}")

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise