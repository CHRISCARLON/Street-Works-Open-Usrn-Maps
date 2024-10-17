import duckdb
import streamlit as st
import geopandas as gpd
from loguru import logger
from .geo_prep import convert_to_geodf

@st.cache_resource
def connect_to_motherduck() -> duckdb.DuckDBPyConnection:
    """
    Create a database connection object
    """
    database = st.secrets["db"]
    token = st.secrets["token"]

    if token is None:
        raise ValueError("Env variable not present")

    connection_string = f'md:{database}?motherduck_token={token}'

    try:
        con = duckdb.connect(connection_string)
        return con
    except Exception as e:
        logger.warning(f"An error occured: {e}")
        raise

@st.cache_data
def fetch_data_london() -> gpd.GeoDataFrame:
    """
    Fetch df containing data
    """
    try:
        con = connect_to_motherduck()
        schema = st.secrets["schema"]
        table_name = st.secrets["table_name_london_impact"]

        query = f"""
        SELECT *
        FROM {schema}.{table_name}
        """
        result = con.execute(query)
        df = result.fetchdf()
        df = convert_to_geodf(df)
        if df.empty:
            logger.warning("The Dataframe is empty")
        return df

    except KeyError as ke:
            error_msg = f"Missing key in st.secrets: {ke}"
            logger.error(error_msg)
            raise ke

    except duckdb.Error as quack:
        logger.error(f"A duckdb error occured: {quack}")
        raise quack

    except Exception as e:
        logger.error(f"An error occured: {e}")
        raise e
