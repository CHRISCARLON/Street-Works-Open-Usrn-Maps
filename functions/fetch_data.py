import duckdb
import streamlit as st
import pandas as pd
from loguru import logger

def connect_to_motherduck() -> duckdb.DuckDBPyConnection:
    """
    Create a database connection object
    """
    # use st.secrets to pull env variables from yaml file
    database = st.secrets["db"]
    token = st.secrets["token"]
    if token is None:
        raise ValueError("MotherDuck token not found in environment variables")

    connection_string = f'md:{database}?motherduck_token={token}'
    try:
        con = duckdb.connect(connection_string)
        return con
    except Exception as e:
        logger.warning(f"An error occured: {e}")
        raise

def fetch_data_wiltshire(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Fetch df containing data
    """
    # use st.secrets to pull env variables from yaml file
    try:
        schema = st.secrets["schema"]
        table_name = st.secrets["table_name_wiltshire"]

        query = f"""
        SELECT *
        FROM {schema}.{table_name}
        """
        result = con.execute(query)
        df = result.fetchdf()

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

def fetch_data_london(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Fetch df containing data
    """
    # use st.secrets to pull env variables from yaml file
    try:
        schema = st.secrets["schema"]
        table_name = st.secrets["table_name_london_impact"]

        query = f"""
        SELECT *
        FROM {schema}.{table_name}
        """
        result = con.execute(query)
        df = result.fetchdf()
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

def fetch_data_london_future(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Fetch df containing data
    """
    # use st.secrets to pull env variables from yaml file
    try:
        schema = st.secrets["schema"]
        table_name = st.secrets["table_name_london_impact_future"]

        query = f"""
        SELECT *
        FROM {schema}.{table_name}
        """
        result = con.execute(query)
        df = result.fetchdf()

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
