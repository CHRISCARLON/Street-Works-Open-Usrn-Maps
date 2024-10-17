import geopandas as gpd
import pandas as pd

def convert_to_geodf(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Takes in a pandas dataframe and returns a geo-dataframe
    with the crs set to use with folium
    """

    if df is None or df.empty:
        raise ValueError("Input DataFrame is None or empty")
    else:
        df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry'])
        geodf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:27700")
        # Convert to EPSG:4326
        geodf = geodf.to_crs(epsg=4326)
        assert isinstance(geodf, gpd.GeoDataFrame)
        assert geodf.crs.to_epsg() == 4326
        return geodf
