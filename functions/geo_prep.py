import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, MultiLineString
from typing import Union, List, cast

def convert_to_geodf(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Takes in a pandas dataframe and returns a geodataframe
    Ensure that the crs is set to EPSG:4326 and removes Z coordinates if present
    """
    # Check that DataFrame is not empty
    if df is None or df.empty:
        raise ValueError("Input DataFrame is None or empty")
    else:
        # Convert WKT to geometry and remove the Z coordinates if present
        def remove_z(geom: Union[LineString, MultiLineString]) -> Union[LineString, MultiLineString]:
            if isinstance(geom, LineString):
                return LineString([(x, y) for x, y, *_ in geom.coords])
            elif isinstance(geom, MultiLineString):
                lines = [remove_z(line) for line in geom.geoms]
                return MultiLineString(cast(List[LineString], lines))
            return geom

        # Isolate geometry column and apply the Z coordinate removal
        df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry']).apply(remove_z)

        # Create GeoDataFrame and ensure correct crs
        geodf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:27700")

        # Convert to EPSG:4326
        geodf = geodf.to_crs(epsg=4326)

        # Assert that data is a GeoDataFrame and that CRS is correct
        assert isinstance(geodf, gpd.GeoDataFrame)
        assert geodf.crs is not None and geodf.crs.to_epsg() == 4326
        return geodf
