# drone_station_pmp
The code for the p-median problem of the stations of drone patrols. Drone patrols are used to respond to crime incidents in an area, in which the crime risk of each street segments is estimated using historical crime records and network kernel density estimation methods. 

## Key steps

1. Download the street-based historical crime data in Liverpool from the UK police website. Determine the borough as the case study area. (Liverpool city??)
1. Preprocess the street-based historical crime data and export it as a CSV file.



## Key code files

1. `Download_uk_police_data.ipynb`
2. `nkde_liverpool.R`: generate the network KDE results for Liverpool
   1. Input: csv files of crime incidents and geojson
   2. Output: `nkde_crime_Liverpool_hub_four.geojson`.
3. `process_poi.ipynb`: process the POI data and compute distance matrices
   1. Input: POI data, demand geojson data, site geojson data
   2. Output: distance matrix files

4. `p-median-drone.ipynb`: the notebook for the pmp.

## Key data files

1. Merseyside police neighbourhood data (geojson): `Merseyside_police_neighbourhood.geojson`. Generated from Download_uk_police_data.ipynb.

2. Liverpool Hub Four neighbourhood data: `Liverpool_hub_four_neighbourhood.geojson`.

3. Street segment data in Liverpool Hub Four neighbourhoods (with network-based crime density): `nkde_crime_Liverpool_hub_four.geojson`

   1. CRS: EPSG:27700 (British National Grid)
   2. Attributes: `density` represents the crime risk or density; `demand_id` is the demand ID which would be used in the pmp model; locational attributes include `feature_easting`, `feature_northing`, `long`, `lat`.

4. Candidate sites in Liverpool Hub Four neighbourhood: `Sites_Liverpool_hub_four.geojson`

   1. CRS: EPSG:27700 (British National Grid)
   2. Attributes: `site_id` is the site ID which would be used in the pmp model. locational attributes include `feature_easting`, `feature_northing`, `long`, `lat`.

5. Crime data (csv): `crimes_Liverpool_hub_four.csv`. 

   1. Data source: https://data.police.uk/

   2. Downloaded and processed: Download_uk_police_data.ipynb

   3. The `Liverpool Hub Four` is one of the ten police neighbourhoods  of Merseyside police and one of the four neighbourhoods in Liverpool. It is selected as the case study as it features the most crime incidents in the four Liverpool neighbourhoods in 2021, with a total number of 29101 incidents. 

   4. Note that the latitude and longitude are not accurate. The location anonymisation is introduced [here](https://data.police.uk/about/). 

      ```
      The latitude and longitude locations of Crime and ASB incidents published on this site always represent the approximate location of a crime — not the exact place that it happened.
      
      How are crime locations anonymised?
      We maintain a master list of anonymous map points. Each map point is specifically chosen so that it:
      
      Appears over the centre point of a street, above a public place such as a Park or Airport, or above a commercial premise like a Shopping Centre or Nightclub.
      Has a catchment area which contains at least eight postal addresses or no postal addresses at all.
      When crime data is uploaded by police forces, the exact location of each crime is compared against this master list to find the nearest map point. The co-ordinates of the actual crime are then replaced with the co-ordinates of the map point. If the nearest map point is more than 20km away, the co-ordinates are zeroed out. No other filtering or rules are applied.
      
      How was the master list of snap points created?
      The snap points list was created in 2012 and based on Ordnance Survey population and housing developments relevant to that year.
      
      In summary, to create the master list of anonymous points, we:
      
      Took the centre point of every road in England and Wales from the Ordnance Survey Locator dataset.
      Augmented these with locally relevant points of interest from the Point X dataset.
      Subsequently analysed each map point to see how many postal addresses were contained in its catchment area according to the Ordnance Survey Address-Point dataset. Any with between 1 and 7 postal addresses were discarded to protect privacy.
      The remaining points were provided to police forces for a human assessment. A small number of additions and deletions were made based on their feedback to make the map points more locally relevant.
      ```

6. Crime risk on street segments (csv or shp): 

   1. Number of segments: 

7. Download_Liverpool_hub_four_POI_2016730.zip: 

   1. The POI data from Digimap
   2. The csv file containing the POI data is `Liverpool_hub_four_POI/poi_4565130/poi-extract-2022_03.csv`.
   2. The classification table of the POI data is `Liverpool_hub_four_POI/poi_4565130/docs/POI_CLASSIFICATIONS.txt`.

8. 

9. Euclidean distance matrix (csv): `distance_matrix_demand_site_Euclidean.csv`

   1. This files contains M rows and N columns, with rows and columns representing demands and facilities, respectively.
   2. The first column is the index column. To read in this file, use the `read_distance_matrix_as_np_array` function from `utilities.py`.

10. Street-network distance matrix (csv): `distance_matrix_demand_site_network.csv`

11. No-fly-zone-constrained distance matrix (csv): `distance_matrix_demand_site_constrained.csv`

12. The distance csv file containing all distance values and the locations of all demands and sites: `distance_dataframe.csv`

    1. Attributes: 'site_id', 'site_long', 'site_lat', 'site_easting', 'site_northing', 'demand_id', 'demand_long', 'demand_lat', 'demand_easting',
              'demand_northing', 'Euclidean', 'network', 'constrained'.

13. The DTM data in England: `SURVEY_LIDAR_Composite_1m_DTM_2020_Elevation.tiff`

       1. [source](https://environment.data.gov.uk/image/rest/services/SURVEY/LIDAR_Composite_1m_DTM_2020_Elevation/ImageServer)
       2. Note that this data is not used. It is very coarse with width of 400 and height of 400 in England.

14. LIDAR Composite DTM data (2m resolution)

       1. [link](https://environment.data.gov.uk/DefraDataDownload/?Mode=survey)
       2. Steps: upload the zip file containing the bounding box of Liverpool hub four (the file called bbox_Liverpool_hub_four.zip); select **LIDAR Composite DTM** in product, select **2020** in Year, and **DTM 2M** in Resolution.
       3. Will get multiple tiff. Using the gdalwarp function to concatenate all tiff files.

15. 

