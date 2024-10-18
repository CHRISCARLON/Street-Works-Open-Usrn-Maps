import streamlit as st

from functions.fetch_data import fetch_data_london
from functions.map_prep_london import plot_map

st.set_page_config(layout="wide")

def impact_scores_map():
    # Set the titles of the page
    st.title("London Impact Scores Grouped by USRN")
    st.markdown("#### Zoom into the map for more detail 🔍")

    # Get and process data
    geodf = fetch_data_london()

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
        st.info(f"Showing data for {selected_authority} - there may be minor errors and we are fixing those!")

        # Calculate total impact score
        total_impact = filtered_geodf['total_impact_level'].sum()

        # Display the total impact score as text
        st.metric("Total Impact Score", f"{total_impact:.2f}")

        plot_map(filtered_geodf)
    else:
        st.warning("Please select a highway authority to display the map.")

def main():
    """
    Streamlit Application Launch
    """
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["London Impact Scores Map"])

    if selection == "London Impact Scores Map":
        impact_scores_map()

if __name__ == "__main__":
    main()
