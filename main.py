import streamlit as st

from functions.fetch_data import fetch_data_england, fetch_highway_authorities_england
from functions.map_prep_england import plot_map_england

# Set page config as wide by default
st.set_page_config(layout="wide")

def impact_scores_map_england():
    """
    Streamlit logic to fetch england data and display map on page
    """
    st.title("Street Work Impact Scores")
    st.markdown("#### Select a Local Highway Authority from the list and zoom into the map for more detail 🔍")
    st.markdown("##### Reorting Period: November 2024")

    try:
        highway_authorities = fetch_highway_authorities_england()
        selected_authority = st.selectbox(
            "Select Highway Authority",
            options=[''] + highway_authorities,
            index=0
        )
        
        if selected_authority:
            geodf = fetch_data_england(selected_authority)
            if not geodf.empty:
                st.info(f"Showing data for {selected_authority}")
                total_impact = geodf['total_impact_level'].sum()
                st.metric("Total Impact Score", f"{total_impact:.2f}")
                plot_map_england(geodf)
            else:
                st.warning(f"No data available for {selected_authority}")
        else:
            st.info("Please select a highway authority to display the map.")
            
    except Exception as e:
        st.error(f"Error fetching data: {e}")

def main():
    """
    Streamlit Application Launch
    """
    impact_scores_map_england()

if __name__ == "__main__":
    main()
