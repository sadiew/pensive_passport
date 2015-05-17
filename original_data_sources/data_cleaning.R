library(dplyr)
library(tidyr)
library(data.table)

#Cost of living data - select necessary columns and bind US + Int'l
us_per_diem <- read.csv('~/Desktop/sw_project/original_data_sources/per_diem_us.csv')
us_per_diem$country <- 'United States'
us_per_diem <- us_per_diem %>% select(city, state, country, m_ie_rate)
us_per_diem$m_ie_rate <- gsub('$', '', us_per_diem$m_ie_rate)

us_per_diem <- data.table(us_per_diem)
setkey(us_per_diem)
us_per_diem <- unique(us_per_diem)

intl_per_diem <- read.csv('~/Desktop/sw_project/original_data_sources/per_diem_intl.csv')
intl_per_diem$state = ''
intl_per_diem <- intl_per_diem %>% select(city, state, country, m_ie_rate)

intl_per_diem <- data.table(intl_per_diem)
setkey(intl_per_diem)
intl_per_diem <- unique(intl_per_diem)
intl_per_diem$country <- tolower(intl_per_diem$country)

simpleCap <- function(x) {
  s <- strsplit(x, " ")[[1]]
  paste(toupper(substring(s, 1,1)), substring(s, 2),
        sep="", collapse=" ")
}

intl_per_diem$country <- sapply(intl_per_diem$country, simpleCap)

all_per_diem <- rbind(us_per_diem, intl_per_diem)

unnested_CostOfLiving <- data.frame(all_per_diem) %>% 
  mutate(city = strsplit(as.character(city), " / ")) %>% 
  unnest(city)
unnested_CostOfLiving$city[unnested_CostOfLiving$city=='New York City'] = "New York"

finalCostOfLiving <- unnested_CostOfLiving %>% 
  group_by(city, state, country) %>%
  summarize(m_ie_rate = max(m_ie_rate)) %>%
  ungroup() %>%
  arrange(country, city)

#Airport Data - select necessary columns
us_airports_by_state <- read.csv('~/Desktop/sw_project/original_data_sources/us_airports_by_state.csv', stringsAsFactors=FALSE)
setnames(us_airports_by_state, "code", "airport_code")
us_airports_by_state$country = 'United States'
us_airports_by_state <- us_airports_by_state %>% select(state, country, airport_code)
airports <- read.csv('~/Desktop/sw_project/original_data_sources/airports.csv')
setnames(airports, "iata_faa","airport_code")
airports$latitude <- round(airports$latitude,2)
airports$longitude <- round(airports$longitude,2)
airports <- airports %>%
  filter(airport_code!='', city!='', iaco!='') %>%
  arrange(country, city) %>%
  left_join(us_airports_by_state, by=c('airport_code', 'country'))
airports$state[is.na(airports$state)] = ''
airports$state[airports$city=='New York'] = 'NY'
airports$city[airports$city=='Firenze'] = 'Florence'
airports$state[airports$city=='Chicago'] = 'IL'

#City Data - seeded from Airports above, joined to cost of living data
cities <- airports %>%
  select(city, state, country) %>%
  unique()

cities <- cities %>% left_join(finalCostOfLiving, by = c('city', 'state', 'country'))
cities <- mutate(cities, city_id=rownames(cities)) %>% 
  select(city_id, city, state, country, m_ie_rate)
cities$m_ie_rate[is.na(cities$m_ie_rate)] = 46

#Append city id to airports
airports <- airports %>% 
  left_join(cities, by = c('city', 'state', 'country')) %>%
  select(airport_id, airport_code, name, city_id, name, latitude, longitude)

#Restaurant data
restaurants <- read.csv('~/Desktop/sw_project/original_data_sources/michelin_star_restaurants.csv')
restaurants <- restaurants %>% 
  left_join(cities, by = c('city', 'country')) %>%
  filter(!is.na(city_id))
restaurants <- mutate(restaurants, restaurant_id=rownames(restaurants)) %>% 
  select(restaurant_id, name, city_id, stars)

#Create csv files
write.csv(airports, '~/Desktop/sw_project/original_data_sources/airports_model.csv', row.names=FALSE)
write.csv(cities, '~/Desktop/sw_project/original_data_sources/cities_model.csv', row.names=FALSE)
write.csv(restaurants, '~/Desktop/sw_project/original_data_sources/restaurants_model.csv', row.names=FALSE)
