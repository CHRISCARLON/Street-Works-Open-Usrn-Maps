import streamlit as st
import sys

from functions.fetch_data import connect_to_motherduck, fetch_data_london, fetch_data_london_future, fetch_data_wiltshire
from functions.geo_prep import convert_to_geodf
from functions.map_prep_london import plot_map
from functions.map_prep_london_future import plot_map_london_future
from functions.map_prep_wiltshire import plot_map_wiltshire
from loguru import logger

st.set_page_config(layout="wide")

def impact_scores_map():
    # Set the titles of the page
    st.title("Impact Scores Grouped by USRN")
    st.markdown("#### Zoom into the map for more detail")

    # Get and process data
    conn = connect_to_motherduck()
    data = fetch_data_london(conn)
    geodf = convert_to_geodf(data)

    # Get unique highway authorities
    highway_authorities = [''] + sorted(geodf['highway_authority'].unique().tolist())

    # Create a selectbox for highway authority
    selected_authority = st.selectbox(
        "Select Highway Authority",
        options=highway_authorities,
        index=0
    )

    # Filter the dataframe based on selected highway authority
    if selected_authority:
        filtered_geodf = geodf[geodf['highway_authority'] == selected_authority]
        st.info(f"Showing data for {selected_authority}")

        # Calculate total impact score
        total_impact = filtered_geodf['Acute & Legacy Impact Score'].sum()

        # Display the total impact score as text
        st.metric("Total Impact Score", f"{total_impact:.2f}")

        plot_map(filtered_geodf)
    else:
        st.warning("Please select a highway authority to display the map.")

def future_impact_scores_map():
    # Set the titles of the page
    st.title("Future Impact Scores Grouped by USRN")
    st.markdown("#### Zoom into the map for more detail")

    # Get and process data
    conn = connect_to_motherduck()
    geodf = fetch_data_london_future(conn)
    geodf = convert_to_geodf(geodf)

    # Get unique highway authorities
    highway_authorities = [''] + sorted(geodf['highway_authority'].unique().tolist())

    # Create a selectbox for highway authority
    selected_authority = st.selectbox(
        "Select Highway Authority",
        options=highway_authorities,
        index=0
    )

    # Filter the dataframe based on selected highway authority
    if selected_authority:
        filtered_geodf = geodf[geodf['highway_authority'] == selected_authority]
        st.info(f"Showing data for {selected_authority}")

        # Calculate total impact score
        total_impact = filtered_geodf['Acute & Legacy Impact Score'].sum()

        # Display the total impact score as text
        st.metric("Total Future Impact Score", f"{total_impact:.2f}")

        plot_map_london_future(filtered_geodf)
    else:
        st.warning("Please select a highway authority to display the map.")

def wiltshire_map():
    # Set the page titles
    st.title("Wiltshire Activities Map")
    st.markdown("#### Select activities and zoom into the map for more detail")

    # Get and process data
    conn = connect_to_motherduck()
    geodf = fetch_data_wiltshire(conn)
    geodf = convert_to_geodf(geodf)

    # Get unique activity types
    activity_types = sorted(geodf['activity_type'].unique().tolist())

    # Create a multiselect for activity types
    selected_activities = st.multiselect(
        "Select Activities",
        options=activity_types,
        default=[]
    )

    if selected_activities:
        # Filter the dataframe based on selected activities
        filtered_geodf = geodf[geodf['activity_type'].isin(selected_activities)]
        st.info(f"Showing data for selected activities in Wiltshire")

        # Calculate total number of activities
        total_activities = len(filtered_geodf)

        # Display the total number of activities as text
        st.metric("Total Works", total_activities)

        # Plot the map
        plot_map_wiltshire(filtered_geodf, selected_activities)
    else:
        st.warning("Please select at least one activity to display on the map.")

def main():
    """
    Streamlit Application Launch
    """
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["London Impact Scores Map", "London Future Impact Scores Map", "Wiltshire Example Map"])

    if selection == "London Impact Scores Map":
        impact_scores_map()
    elif selection == "London Future Impact Scores Map":
        future_impact_scores_map()
    elif selection == "Wiltshire Example Map":
        wiltshire_map()

if __name__ == "__main__":
    main()
