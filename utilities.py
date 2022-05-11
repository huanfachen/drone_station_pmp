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