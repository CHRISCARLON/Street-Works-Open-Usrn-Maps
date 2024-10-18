import streamlit as st

from functions.fetch_data import fetch_data_london, fetch_data_england, fetch_highway_authorities_england
from functions.map_prep_london import plot_map_london
from functions.map_prep_england import plot_map_england

# Set page config as wide by default
st.set_page_config(layout="wide")

def impact_scores_map_london():
    """
    Streamlit logic to fetch all london data and display map on page
    """
    # Set the page title
    st.title("London Impact Scores Grouped by USRN")
    st.markdown("#### Zoom into the map for more detail 🔍")

    # Fetch and process data
    geodf = fetch_data_london()

    # Get a list of unique highway authorities to use in drop down
    highway_authorities = [''] + sorted(geodf['highway_authority'].unique().tolist())

    # Create a selectbox for highway authority using list created above
    selected_authority = st.selectbox(
        "Select Highway Authority",
        options=highway_authorities,
        index=0
    )

    # Filter the dataframe based on the selected highway authority
    if selected_authority:
        filtered_geodf = geodf[geodf['highway_authority'] == selected_authority]
        st.info(f"Showing data for {selected_authority} - there may be minor errors and we are fixing those!")

        # Calculate total impact score
        total_impact = filtered_geodf['total_impact_level'].sum()

        # Display the total impact score as text
        st.metric("Total Impact Score", f"{total_impact:.2f}")

        # Plot map
        plot_map_london(filtered_geodf)
    else:
        st.info("Please select a highway authority to display the map.")

def impact_scores_map_england():
    """
    Streamlit logic to fetch England data for a specific highway authority and display map on page
    """
    # Set the page title
    st.title("England Impact Scores Grouped by USRN")
    st.markdown("#### Select a highway authority and zoom into the map for more detail 🔍")

    try:
        # Fetch the list of all highway authorities
        highway_authorities = fetch_highway_authorities_england()
    except Exception as e:
        st.error(f"Error fetching highway authorities: {e}")
        return

    # Create a selectbox for highway authority
    selected_authority = st.selectbox(
        "Select Highway Authority",
        options=[''] + highway_authorities,
        index=0  # This will select the empty string, prompting the user to make a selection
    )

    if selected_authority:
        # Fetch and process data for the selected highway authority
        geodf = fetch_data_england(selected_authority)

        if not geodf.empty:
            st.info(f"Showing data for {selected_authority}")
            # Calculate total impact score
            total_impact = geodf['total_impact_level'].sum()
            # Display the total impact score as text
            st.metric("Total Impact Score", f"{total_impact:.2f}")
            # Plot map
            plot_map_england(geodf)
        else:
            st.warning(f"No data available for {selected_authority}")
    else:
        st.info("Please select a highway authority to display the map.")

def main():
    """
    Streamlit Application Launch
    """
    # Set sidebar to select map
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["London Impact Scores Map", "England Impact Scores Map"])

    # Select map logic
    if selection == "London Impact Scores Map":
        impact_scores_map_london()
    elif selection == "England Impact Scores Map":
        impact_scores_map_england()

if __name__ == "__main__":
    main()
