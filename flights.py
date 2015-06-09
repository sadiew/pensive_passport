"""Calls the Google Flights API for airfare information."""

import json
import requests
import os

from random import randrange, choice


def call_flights_api(origin, destination, depart_date, return_date):
    api_key = os.environ['GOOGLE_KEY']
    url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + api_key
    headers = {'content-type': 'application/json'}

    # round trip api call
    params = {
        "request": {
            "slice": [
                {
                    "origin": origin,
                    "destination": destination,
                    "date": depart_date,
                    "maxStops": 2
                },
                {
                    "origin": destination,
                    "destination": origin,
                    "date": return_date,
                    "maxStops": 2
                }
            ],
            "passengers": {
                "adultCount": 1
            },
            "solutions": 2,
            "refundable": False
        }
    }

    response = requests.post(url, data=json.dumps(params), headers=headers)

    data = response.json()

    first_option = data['trips']['tripOption'][0]

    raw_fare = first_option['saleTotal'][3:]
    total_fare = round(float(raw_fare), 0)

    return {'airfare': total_fare}


def process_flights(origin, destination, depart_date, return_date):
    """Attempt to call Google flights API, but return default values
    if unavailable."""

    # try:
    #     airfare = call_flights_api(origin, destination, depart_date, return_date)
    # except:
    #     random_airfare = choice([randrange(1000, 2000) for i in range(20)])
    #     airfare = {'airfare': random_airfare}

    random_airfare = choice([randrange(1000, 2000) for i in range(20)])
    airfare = {'airfare': random_airfare}

    return airfare
