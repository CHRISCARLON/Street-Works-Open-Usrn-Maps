import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, MultiLineString

def convert_to_geodf(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Takes in a pandas dataframe and returns a geo-dataframe
    with the crs set to use with folium, removing Z coordinates if present
    """
    if df is None or df.empty:
        raise ValueError("Input DataFrame is None or empty")
    else:
        # Convert WKT to geometry, removing Z coordinate if present
        def remove_z(geom):
            if geom.has_z:
                if isinstance(geom, LineString):
                    return LineString([xy[0:2] for xy in geom.coords])
                elif isinstance(geom, MultiLineString):
                    return MultiLineString([remove_z(line) for line in geom.geoms])
            return geom

        df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry']).apply(remove_z)

        # Create GeoDataFrame and ensure correct crs
        geodf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:27700")

        # Convert to EPSG:4326
        geodf = geodf.to_crs(epsg=4326)

        assert isinstance(geodf, gpd.GeoDataFrame)
        assert geodf.crs.to_epsg() == 4326
        return geodf
