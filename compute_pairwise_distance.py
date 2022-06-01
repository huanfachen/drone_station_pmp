# require several packages: osrm, numpy, geopandas
def osrm_distance(origin_long, origin_lat, dest_long, dest_lat):
    """using OSRM to query the driving distance between origin and destination. Require OSRM running on localhost:5000

    Args:
        origin_long (float): long of origin
        origin_lat (float): lat of origin
        dest_long (float): long of destination
        dest_lat (float): lat of destination
    """
    from osrm import Point, simple_route

    result = simple_route(
                      Point(latitude=origin_lat, longitude=origin_long), Point(latitude=dest_lat, longitude=dest_long),
                      output='route', geometry='wkt')
    return result[0]['distance']

def compute_pairwise_distance(df_origin, df_dest, distance_cutoff, b_speedup_using_Euclidean = True, b_include_over_distance=True):
    """Compute the driving distance between origin and destination points, using OSRM. If the distance is greater than distance_cutoff, it is marked as NA.
    Return a dataframe containing the origin_ID, dest_ID, and distance. If the disntace is equal to or greater than distance_cutoff, it means it is larger than the cutoff but the value may be inaccurate.

    Args:
        df_origin (pandas.dataframe): containing three columns (ID, long, lat). The column names are ignored
        df_dest (pandas.dataframe): containing three columns (ID, long, lat). The column names are ignored
        distance_cutoff (float): in meters. If distance is greater than cutoff, it will be marked as NA
        b_speedup_using_Euclidean (bool, default True): if True, use Euclidean distance as the filter to reduce computation. Only applies to points in UK.
        b_include_over_distance (bool, default True): if True, the distance greater than cutoff will be included. Otherwise, these rows will be removed
    """
    # import pandas as pd
    import numpy as np
    import geopandas
    from tqdm import tqdm
    # use tqdm to record progress
    # import osrm
    # form the dataframe
    # df_distance = pd.DataFrame(columns=[df_origin.columns[0], df_dest.columns[0], 'distance']
    
    
    # Register `pandas.progress_apply` and `pandas.Series.map_apply` with `tqdm`
    # (can use `tqdm.gui.tqdm`, `tqdm.notebook.tqdm`, optional kwargs, etc.)
    tqdm.pandas(desc="Progress bar:")

    # convert WGS84 to BNG (epsg:27700)
    df_origin_cp = df_origin.copy()
    df_dest_cp = df_dest.copy()
    # print(df_origin_cp.columns)
    df_origin_cp.columns = ['origin_id', 'origin_long', 'origin_lat']
    df_dest_cp.columns = ['dest_id', 'dest_long', 'dest_lat']

    if b_speedup_using_Euclidean:
        # add easting and northing to df_origin and df_test
        gdf_origin = geopandas.GeoDataFrame(df_origin_cp, geometry=geopandas.points_from_xy(df_origin.iloc[:,1], df_origin.iloc[:,2]))
        # wgs84
        gdf_origin.crs = 'epsg:4326'
        gdf_origin = gdf_origin.to_crs('epsg:27700')
        gdf_dest = geopandas.GeoDataFrame(df_dest_cp, geometry=geopandas.points_from_xy(df_dest.iloc[:,1], df_dest.iloc[:,2]))
        # wgs84
        gdf_dest.crs = 'epsg:4326'
        gdf_dest = gdf_dest.to_crs('epsg:27700')

        df_origin_cp['origin_easting'] =  gdf_origin.geometry.x
        df_origin_cp['origin_northing'] =  gdf_origin.geometry.y
        df_dest_cp['dest_easting'] =  gdf_dest.geometry.x
        df_dest_cp['dest_northing'] =  gdf_dest.geometry.y

        df_distance = df_origin_cp.merge(df_dest_cp, how = 'cross')
        df_distance['distance_Eucl'] = np.linalg.norm(df_distance[['origin_easting','origin_northing']].values - df_distance[['dest_easting','dest_northing']], axis=1)
    else:
        # if Euclidean distance is not used, set distance_Eucl as 0
        df_distance = df_origin_cp.merge(df_dest_cp, how = 'cross')
        df_distance['distance_Eucl'] = 0

    # if distance_Eucl is greater than distance_cutoff, then distance=distance_cutoff. 
    # Otherwise, use OSRM to query the driving distance

    # use `progress_apply` instead of `apply` 
    df_distance['distance'] = df_distance.progress_apply(lambda row: distance_cutoff if row.distance_Eucl > distance_cutoff else 
    osrm_distance(row.origin_long, row.origin_lat, row.dest_long, row.dest_lat), axis=1)

    # df_distance['distance'] = df_distance.apply(lambda row: distance_cutoff if row.distance_Eucl > distance_cutoff else 
    # osrm_distance(row.origin_long, row.origin_lat, row.dest_long, row.dest_lat), axis=1)

    df_distance = df_distance[['origin_id', 'dest_id', 'distance']]
    if b_include_over_distance is False:
        df_distance = df_distance[df_distance.distance <= distance_cutoff,:]
    return df_distance

if __name__ == "__main__":
    # test two points in each of origin and dest
    import pandas
    df_origin = pandas.DataFrame({'index': ['E1','F2'],
        'long': [-0.1904869, -0.1336332],
        'lat': [51.5996503, 51.5188742]})
    df_dest = df_origin.copy()
    df_origin.columns =  ['origin_id', 'origin_long', 'origin_lat']
    # print(df_origin.columns)
    print(compute_pairwise_distance(df_origin, df_dest, distance_cutoff = 10, b_speedup_using_Euclidean=False))