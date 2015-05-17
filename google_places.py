from googleplaces import GooglePlaces, types, lang
import os

def get_places(city, country, place_type):
	api_key = os.environ['QPX_KEY']
	google_places = GooglePlaces(api_key)
	query_result = google_places.nearby_search(
        location=city+','+country, keyword=place_type,
        #types=['restaurant', 'museum', 'park'],
        radius=20000)

	places = {}
	for place in query_result.places:
		place.get_details()
		places[place.name] = place.website
	return places
