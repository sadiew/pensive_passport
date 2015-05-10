library(dplyr)
library(data.table)

#Cost of living data - select necessary columns and bind US + Int'l
us_per_diem <- read.csv('~/Desktop/sw_project/original_data_sources/per_diem_us.csv')
us_per_diem$country <- 'United States'
us_per_diem <- us_per_diem %>% select(city, country, m_ie_rate)
us_per_diem$m_ie_rate <- gsub('$', '', us_per_diem$m_ie_rate)

us_per_diem <- data.table(us_per_diem)
setkey(us_per_diem)
us_per_diem <- unique(us_per_diem)

intl_per_diem <- read.csv('~/Desktop/sw_project/original_data_sources/per_diem_intl.csv')
intl_per_diem <- intl_per_diem %>% select(city, country, m_ie_rate)

intl_per_diem <- data.table(intl_per_diem)
setkey(intl_per_diem)
intl_per_diem <- unique(intl_per_diem)

finalCostOfLiving <- rbind(us_per_diem, intl_per_diem)

#Airport Data - select necessary columns
us_airports_by_state <- read.csv('~/Desktop/sw_project/original_data_sources/us_airports_by_state.csv', stringsAsFactors=FALSE)
setnames(us_airports_by_state, "code", "airport_code")
us_airports_by_state <- us_airports_by_state %>% select(state, airport_code)
airports <- read.csv('~/Desktop/sw_project/original_data_sources/airports.csv')
setnames(airports, "iata_faa","airport_code")
airports$latitude <- round(airports$latitude,2)
airports$longitude <- round(airports$longitude,2)
airports <- airports %>%
  filter(airport_code!='', city!='', iaco!='') %>%
  arrange(country, city) %>%
  left_join(us_airports_by_state, by="airport_code")
airports$state[is.na(airports$state)] = ''

#City Data - seeded from Airports above
cities <- airports %>%
  select(city, state, country) %>%
  unique()
cities <- mutate(cities, city_id=rownames(cities)) %>% select(city_id, city, state, country)

#Append city id to airports
airports <- airports %>% 
  left_join(cities, by = c('city', 'state', 'country')) %>%
  select(airport_id, airport_code, name, city_id, name, latitude, longitude)

#Append cost of living to cities

#write.csv(finalCostOfLiving, '~/Desktop/sw_project/original_data_sources/per_diem_rates.csv', row.names=FALSE)
write.csv(airports, '~/Desktop/sw_project/original_data_sources/airports_model.csv', row.names=FALSE)
write.csv(cities, '~/Desktop/sw_project/original_data_sources/cities_model.csv', row.names=FALSE)
