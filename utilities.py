# This function is an improvement upon get_crimes_area function from police_api.__init__.py
# As the original function has a problem of HTTP request
def new_get_crimes_area (points, list_date=[None], category=None):
    from police_api import PoliceAPI, Crime
    api = PoliceAPI()
    def encode_polygon(points):
        return ':'.join(['{0},{1}'.format(*p) for p in points])
#     if isinstance(category, CrimeCategory):
#         category = category.id
#     method = 'crimes-street/%s' % (category or 'all-crime')
    base_url = 'https://data.police.uk:443/api/crimes-street/all-crime'
    myobj = {'poly': encode_polygon(points)}
    # make list_date as a list
    if list_date is None:
        list_date = [None]
    elif not isinstance(list_date, list) :
        list_date = [list_date]
    
    crimes = []
    # iterate over 
    for date in list_date:
        if date is not None:
            myobj['date'] = date
        x = requests.request('POST', url, data=myobj)
        try:
            x.raise_for_status()
        except requests.models.HTTPError as e:
            raise APIError(e)
        for c in x.json():
            crimes.append(Crime(api, data=c))
    return crimes

# Three of this function
# boundary_test = [(52.268, 0.543),
#          (52.794,0.238),
#          (52.130,0.478)]
# crimes_test = new_get_crimes_area(boundary_test)
# print(len(crimes_test))
## 71
# crimes_test = new_get_crimes_area(boundary_test, '2021-10')
# print(len(crimes_test))
## 114
# crimes_test = new_get_crimes_area(boundary_test, ['2021-1', '2021-10'])
# print(len(crimes_test))
## 202

# read in the distance csv and transform it into an ndarray
# return a numpy array, with rows and columns corresponding to demands and sites, respectively
def read_distance_matrix_as_np_array(path_csv_distance):
    import pandas as pd
    distance_matrix = pd.read_csv(path_csv_distance, index_col=0)
    return distance_matrix.to_numpy()

def read_distance_matrix_as_dataframe(path_csv_distance):
    import pandas as pd
    return pd.read_csv(path_csv_distance, index_col=0)

def get_selected_facility_sites(model, facility_points):
    """Get selected facility sites. Return a geodataframe of the selected sites

    Args:
        model (_type_): p-median model (solved)
        facility_points (GeoDataFrame): the facility site point dataset
    """
    fac_sites = []
    for i in range(facility_points.shape[0]):
        if model.fac2cli[i]:
            fac_sites.append(i)
    return facility_points.iloc[fac_sites,]

def plot_pmp_results(model, facility_points, demand_points, boundary, plot_title = 'P-median problem'):
    """Plot the results of p-median model

    Args:
        model (_type_): p-median model (solved)
        facility_points (GeoDataFrame): the facility site point dataset
        demand_points (GeoDataFrame): the demand site dataset
        boundary (GeoDataFrame): the boundary polygon dataset
    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    import matplotlib.lines as mlines

    # dv_colors = [
    # "darkcyan",
    # "mediumseagreen",
    # "cyan",
    # "darkslategray",
    # "lightskyblue",
    # "limegreen",
    # "darkgoldenrod",
    # "peachpuff",
    # "coral",
    # "mediumvioletred",
    # "blueviolet",
    # "fuchsia",
    # "thistle",
    # "lavender",
    # "saddlebrown",
    # ] 

    arr_points = []
    fac_sites = []
    
    for i in range(facility_points.shape[0]):
        if model.fac2cli[i]:
            fac_sites.append(i)

    fig, ax = plt.subplots(figsize=(6, 6))
    legend_elements = []

#     # plot streets
#     street.plot(ax=ax, alpha=1, color='black', zorder=1)
#     legend_elements.append(mlines.Line2D(
#         [],
#         [],
#         color='black',
#         label='streets',
#     ))

#     facility_points.plot(ax=ax, color='brown', marker="*", markersize=80, zorder=2)
#     legend_elements.append(mlines.Line2D(
#         [],
#         [],
#         color='brown',
#         marker="*",
#         linewidth=0,
#         label=f'facility sites ($n$={FACILITY_COUNT})'
#     ))

    # boundary
    boundary.plot(ax=ax, color='white', edgecolor='black')
    
    # demand points
    demand_points.plot(ax=ax, color='blue', edgecolor='white', alpha=0.3)
    label = f"Street segments"
    legend_elements.append(Patch(facecolor='blue', edgecolor="k", label=label))
    
    # unselected sites
    gdf_poi_unselected = facility_points[~facility_points.index.isin(fac_sites)]
    gdf_poi_unselected.plot(ax=ax, color='grey',marker="*",markersize=200 * 0.5,)
    label = f"Unselected sites"
#     legend_elements.append(Patch(marker="*",facecolor='grey', edgecolor="k", label=label))
    legend_elements.append(mlines.Line2D(
    [],
    [],
    color='grey',
    marker="*",
    ms=20 / 2,
    markeredgecolor="k",
    linewidth=0,
    alpha=0.8,
    label=label))
    
    # selected sites
    gdf_poi_selected = facility_points.iloc[fac_sites,]
    gdf_poi_selected.plot(ax=ax, color='red', marker="*",markersize=200 * 1.0,)
    label = f"Selected sites"
    legend_elements.append(mlines.Line2D(
    [],
    [],
    color='red',
    marker="*",
    ms=20 / 2,
    markeredgecolor="k",
    linewidth=0,
    alpha=0.8,
    label=label))
    

    
#     for i in range(len(arr_points)):
#         gdf = geopandas.GeoDataFrame(arr_points[i])

#         label = f"coverage_points by y{fac_sites[i]}"
#         legend_elements.append(Patch(facecolor=dv_colors[i], edgecolor="k", label=label))

#         gdf.plot(ax=ax, zorder=3, alpha=0.7, edgecolor="k", color=dv_colors[i], label=label)
#         facility_points.iloc[[fac_sites[i]]].plot(ax=ax,
#                                 marker="*",
#                                 markersize=200 * 3.0,
#                                 alpha=0.8,
#                                 zorder=4,
#                                 edgecolor="k",
#                                 facecolor=dv_colors[i])
        
#         legend_elements.append(mlines.Line2D(
#             [],
#             [],
#             color=dv_colors[i],
#             marker="*",
#             ms=20 / 2,
#             markeredgecolor="k",
#             linewidth=0,
#             alpha=0.8,
#             label=f"y{fac_sites[i]} facility selected",
#         ))

    plt.title(plot_title, fontweight="bold")
    plt.legend(handles = legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1))