import requests
import os
from model import Place, connect_to_db, db


def call_places_api(city_center, place_type):

	api_key = os.environ['GOOGLE_KEY']
	url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=" + api_key
	headers = {'content-type': 'application/json'}

	params = {
		"location": city_center,
		"types": place_type,
		"keyword": place_type,
		"radius": 5000
		}

	response = requests.post(url, params=params, headers=headers)

	data = response.json()
	return data


def add_places_to_db(city_id, data, place_type):

	for result in data['results']:
		place = Place(google_place_id=result['place_id'],
						city_id=city_id,
						name=result['name'].encode('utf8'),
						lat=result['geometry']['location']['lat'],
						lon=result['geometry']['location']['lng'],
						place_type=place_type)
		db.session.add(place)
	db.session.commit()


def get_places(city_id, city_center, place_type):

	data = call_places_api(city_center, place_type)
	add_places_to_db(city_id, data, place_type)
	places = Place.query.filter_by(city_id=city_id, place_type=place_type).all()
	return places


