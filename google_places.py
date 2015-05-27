from googleplaces import GooglePlaces, types, lang
import os

def get_places(city, country, place_type):
	api_key = os.environ['GOOGLE_KEY']
	google_places = GooglePlaces(api_key)
	query_result = google_places.nearby_search(
        location=city+','+country, 
        types=[place_type],
        keyword=place_type,
        radius=20000)

	places = {}
	for place in query_result.places:
		places[place.name] = place.geo_location
		places[place.name]['google_place_id'] = place.place_id

	print places
	#places = {place.name:place.geo_location for place in query_result.places}

	return places
