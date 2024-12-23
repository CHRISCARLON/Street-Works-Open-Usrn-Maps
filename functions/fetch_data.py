import duckdb
import streamlit as st
import geopandas as gpd
import pandas as pd

from loguru import logger
from .geo_prep import convert_to_geodf

@st.cache_resource
def connect_to_motherduck() -> duckdb.DuckDBPyConnection:
    """
    Create a database connection object to MotherDuck
    """
    # Define secrets
    database = st.secrets["db"]
    token = st.secrets["token"]

    # Check if token exists
    if token is None:
        raise ValueError("Env variable not present")

    # Connection string
    connection_string = f'md:{database}?motherduck_token={token}'

    # Attempt connection
    try:
        con = duckdb.connect(connection_string)
        return con
    except Exception as e:
        logger.warning(f"An error occured: {e}")
        raise

@st.cache_data
def fetch_data_england(highway_authority: str) -> gpd.GeoDataFrame:
    """
    Fetch DataFrame containing data for a specific highway authority and convert to GeoDataFrame
    """
    # Attempt connection and processing logic
    try:
        con = connect_to_motherduck()
        # Define table and schema
        schema = st.secrets["schema"]
        table_name = st.secrets["table_name_england_impact"]
        # Execute query and logic
        query = f"""
        SELECT *
        FROM {schema}.{table_name}
        WHERE highway_authority = ?
        """
        result = con.execute(query, [highway_authority])
        df = result.fetchdf()
        df = convert_to_geodf(df)
        if df.empty:
            logger.warning(f"The Dataframe is empty for highway authority: {highway_authority}")
        return df
    except KeyError as ke:
        error_msg = f"Missing key in st.secrets: {ke}"
        logger.error(error_msg)
        raise ke
    except duckdb.Error as quack:
        logger.error(f"A duckdb error occurred: {quack}")
        raise quack
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e

@st.cache_data
def fetch_highway_authorities_england() -> list[str]:
    """
    Fetch distinct highway authorities for England as a list
    """
    try:
        con = connect_to_motherduck()
        schema = st.secrets["schema"]
        table_name = st.secrets["table_name_england_impact"]
        query = f"""
        SELECT DISTINCT highway_authority
        FROM {schema}.{table_name}
        ORDER BY highway_authority
        """
        result = con.execute(query)
        authorities = [row[0] for row in result.fetchall()]
        return authorities
    except Exception as e:
        logger.error(f"An error occurred while fetching highway authorities: {e}")
        raise e

@st.cache_data
def fetch_permit_details_england(street_name: str, highway_authority: str) -> pd.DataFrame:
    """
    Fetch DataFrame containing permit details for a specific street_name
    """
    # Attempt connection and processing logic
    try:
        con = connect_to_motherduck()
        # Define table and schema
        schema = st.secrets["schema"]
        table_name = st.secrets["table_name_england_permit_details"]
         # Execute query with both street_name and highway_authority
        query = f"""
            SELECT *
            FROM {schema}.{table_name}
            WHERE street_name = ?
            AND highway_authority = ?
        """
        result = con.execute(query, [street_name, highway_authority])
        df = result.fetchdf()
        if df.empty:
            logger.warning(f"The Dataframe is empty for street_name: {street_name}")
        return df
    except KeyError as ke:
        error_msg = f"Missing key in st.secrets: {ke}"
        logger.error(error_msg)
        raise ke
    except duckdb.Error as quack:
        logger.error(f"A duckdb error occurred: {quack}")
        raise quack
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e