import json
import requests
import os


class GoogleService(object):
    api_key = os.environ['GOOGLE_KEY']
    headers = {'content-type': 'application/json'}

    def __init__(self, url):
        self.url = url

    def get_response(self):
        response = requests.post(self.url,
                                data=json.dumps(self.params),
                                headers=self.headers)

        data = response.json()

        return data


class FlightService(GoogleService):

    def __init__(self):

        url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + self.api_key

        super(FlightService, self).__init__(url)

    def set_parameters(self, origin, destination, depart_date, return_date):
            self.params = {
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


    def process_response(self, origin, destination, depart_date, return_date):

        self.set_parameters(origin, destination, depart_date, return_date)

        try:
            data = self.get_response()

            first_option = data['trips']['tripOption'][0]

            raw_fare = first_option['saleTotal'][3:]
            total_fare = round(float(raw_fare), 0)

            airfare = {'airfare': total_fare}
        except:
            airfare = {'airfare': 1241}

        return airfare


class PlaceService(GoogleService):
    def __init__(self):
        url = url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=" + self.api_key

        super(PlaceService, self).__init__(url)

    def set_parameters(self, city_center, place_type):
        self.params = {
            "location": city_center,
            "types": place_type,
            "keyword": place_type,
            "radius": 5000
            }

    def get_response(self):
        response = requests.post(self.url, params=self.params, headers=self.headers)

        data = response.json()
        return data

    def process_response(self, city_center, place_type):

        self.set_parameters(city_center, place_type)

        return self.get_response()

