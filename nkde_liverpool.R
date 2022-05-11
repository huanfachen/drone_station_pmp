# getwd()
# setwd('/Users/wilsongao/Dropbox/Mac (2)/Desktop/Liverpool_Safety')

## install these packages if necessary
library(tidygraph)
library(igraph)
library(stplanr)
library(bigstatsr)
library(osmdata)
library(dplyr)
library(spNetwork)
library(tmap)
library(sf)
library(ggplot2)
library(stringr)
library(leaflet)
library(patchwork)

# /jeremygelb.github.io/spNetwork/articles/NKDE.htmlhttps:/ 
# https://michaelbcalles.netlify.app/post/kernel-density-estimation-in-network-space/ 

bbx <- getbb("Liverpool, UK")

# the polygon shapefile of Liverpool (or the case study area)
study_area <- st_read('Merseyside_police_neighbourhood.geojson') %>%
  st_transform(crs = 27700)
# only use Liverpool Hub Four
study_area <- study_area %>% filter(name == "Liverpool Community Police Team - Hub Four")

study_area %>% st_write("Liverpool_hub_four_neighbourhood.geojson")
# study_area<- st_read('./shp/Liverpool.shp') %>%
#   st_transform(crs = 27700) 

# liverpool network
streets <- bbx %>%
  opq()%>%
  add_osm_feature(key = "highway", 
                  value=c("residential", "living_street",
                          "service","unclassified",
                          "pedestrian", "footway",
                          "track","path","motorway", "trunk",
                          "primary","secondary", 
                          "tertiary","motorway_link",
                          "trunk_link","primary_link",
                          "secondary_link",
                          "tertiary_link")) %>%
  osmdata_sf()

streets_sf <- st_transform(streets$osm_lines,crs=27700) %>% 
  filter(st_intersects(.,study_area,sparse=FALSE))

plot(st_geometry(streets_sf))

ggplot() + geom_sf(data = streets_sf)

ggplot() +
  geom_sf(data = streets_sf,
          aes(color=highway),
          size = .4,
          alpha = .65)

# # cycling accident data
# collisions <- st_read('./shp/accident/acci_cycle/gdf_20_cycle.shp') %>%
#   st_transform(crs = 27700) 
# 
# ggplot(collisions) +
#   geom_sf() + 
#   coord_sf() + 
#   theme_void()

# crime data
df_crime <- read.csv("crimes_Liverpool_hub_four.csv")
# crs = 4326 is the WGS84
sf_crime <- st_as_sf(x = df_crime, coords = c("lng", "lat"), crs = 4326) %>%
  st_transform(crs = 27700)

# how many crime incidents
nrow(sf_crime)
# 29101

# plot road network and crime points
ggplot() +
  geom_sf(data = streets_sf,
          aes(color=highway),
          size = .4,
          alpha = .65) +
  geom_sf(data = sf_crime)

# save tiff file
ggsave("Liverpool_neighbourhood_hub_four_network_crime_incidents.tiff")
ggsave("Liverpool_neighbourhood_hub_four_network_crime_incidents.pdf")

#prepare network data(# https://michaelbcalles.netlify.app/post/kernel-density-estimation-in-network-space/ )
split_lines <- function(input_lines, max_length, id) {
  
  input_lines <- input_lines %>% ungroup()
  
  geom_column <- attr(input_lines, "sf_column")
  
  input_crs <- sf::st_crs(input_lines)
  
  input_lines[["geom_len"]] <- sf::st_length(input_lines[[geom_column]])
  
  attr(input_lines[["geom_len"]], "units") <- NULL
  input_lines[["geom_len"]] <- as.numeric(input_lines[["geom_len"]])
  
  too_short <- filter(select(all_of(input_lines),all_of(id), all_of(geom_column), geom_len), geom_len < max_length) %>% select(-geom_len)
  
  too_long <- filter(select(all_of(input_lines),all_of(id), all_of(geom_column), geom_len), geom_len >= max_length)
  
  rm(input_lines) # just to control memory usage in case this is big.
  
  too_long <- mutate(too_long,
                     pieces = ceiling(geom_len / max_length),
                     fID = 1:nrow(too_long)) %>%
    select(-geom_len)
  
  split_points <- sf::st_set_geometry(too_long, NULL)[rep(seq_len(nrow(too_long)), too_long[["pieces"]]),] %>%
    select(-pieces)
  
  split_points <- mutate(split_points, split_fID = row.names(split_points)) %>%
    group_by(fID) %>%
    mutate(piece = 1:n()) %>%
    mutate(start = (piece - 1) / n(),
           end = piece / n()) %>%
    ungroup()
  
  new_line <- function(i, f, t) {
    lwgeom::st_linesubstring(x = too_long[[geom_column]][i], from = f, to = t)[[1]]
  }
  
  split_lines <- apply(split_points[c("fID", "start", "end")], 1,
                       function(x) new_line(i = x[["fID"]], f = x[["start"]], t = x[["end"]]))
  
  rm(too_long)
  
  split_lines <- st_sf(split_points[c(id)], geometry = st_sfc(split_lines, crs = input_crs))
  
  lixel <- rbind(split_lines,too_short) %>% mutate(LIXID = row_number())
  
  return(lixel)
}

## The function split the network into segments within a maximum length
lixelize_network <- function(sf_network,max_lixel_length,uid){
  print("Splitting input spatial lines by lixel length...")
  target_lixel <- split_lines(input_lines = sf_network,max_length = max_lixel_length,id = uid)
  print("Create corresponding shortest distance network...")
  shortest_distance_network <- split_lines(input_lines = target_lixel,max_length = max_lixel_length/2,id = uid)
  return(list(target_lixel=target_lixel,shortest_distance_network=shortest_distance_network))
}

network_sln <- SpatialLinesNetwork(streets_sf)

summary(network_sln)

network_sln <- sln_clean_graph(network_sln)
# get the connected part
sf_network<- network_sln@sl

# how many streets?
# befor graph cleaning
nrow(streets_sf)
#7089

nrow(sf_network)
# 1350
# compare two networks
g1 <- ggplot() + geom_sf(data = streets_sf) + labs(title = sprintf("Before cleaning (#streets %1$s)", nrow(streets_sf)))
g2 <- ggplot() + geom_sf(data = sf_network) + labs(title = sprintf("After cleaning (#streets %1$s)", nrow(sf_network)))
g1 + g2

ggsave("Liverpool_hub_four_road_network_before_after_cleaning.pdf")


sf_network <- sf::st_set_crs(sf_network, 27700)
sf_network.cut1=sf_network[,c('osm_id','length','highway','geometry')]
#st_write(obj = sf_network.cut1,dsn=paste0("./shp/network/liverpool_road_osm.shp/sf_network_clean_NKDE.shp"))
lixels <- lixelize_lines(sf_network,200,mindist = 50)

# lixels <- lixelize_network(sf_network,200,uid='osm_id')
nrow(sf_network)
#1350
nrow(lixels)
# 1710
length(lixels)
#195

# get the line center
samples <- lines_center(lixels)

# then applying the NKDE
densities <- nkde(sf_network, 
                  events = sf_crime,
                  w = rep(1,nrow(sf_crime)),
                  samples = samples,
                  kernel_name = "quartic",
                  bw = 300, div= "bw", 
                  method = "continuous", digits = 1, tol = 1,
                  grid_shape = c(2,2), max_depth = 8,
                  agg = 5, #we aggregate events within a 5m radius (faster calculation)
                  sparse = TRUE,
                  verbose = FALSE)

# add densities to samples
samples$density <- densities
ggplot() + geom_sf(data=samples, aes(color=density))
ggsave("NKDE_density_crimes_Liverpool_hub_four.pdf")

# save samples as geojson
st_write(samples, "nkde_crime_Liverpool_hub_four.geojson")

boxplot(samples$density)
ggsave("boxplot_NKDE_density_crimes_Liverpool_hub_four.pdf")

names(sf_network.cut1)
names(sf_network)
nrow(sf_network)
nrow(sf_network.cut1)
#1350
nrow(sf_crime)
# 29101

# rescaling to help the mapping
#samples$density <- samples$density*1000
samples2 <- samples[order(samples$density),]
data.cut1=samples2[,c('osm_id','length','density','geometry')]
gdf_nkde_2018<-data.cut1%>% as.data.frame() %>% 
  group_by(osm_id) %>% summarise(density=mean(density))
gdf_nkde_2018<- left_join(sf_network.cut1,gdf_nkde_2018, by='osm_id')

st_write(gdf_nkde_2018, "./shp/nkde_r_jeremygelb/nkde_2020.shp")

#colorRamp <- brewer.pal(n = 7, name = "Spectral")
#colorRamp <- rev(colorRamp)

title <- paste0("bike accident density by kilometres in 2020,",
                "\nwithin a radius of 300 metres")

tm_shape(sf_network) + 
  tm_lines("black")+
  tm_shape(samples2) + 
  tm_dots("density", style = "kmeans", n = 7, size = 0.1) + 
  tm_layout(legend.outside = TRUE, 
            main.title = title , main.title.size = 1)
