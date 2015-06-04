import requests
import os


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
