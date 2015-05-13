import json, requests, os
from datetime import datetime, timedelta

class Trip(object):
	def __init__(self, name, origin, destination, depart_date, return_date):
		self.name = name
		self.origin = origin
		self.destination = destination
		self.depart_date = depart_date
		self.return_date = return_date
		self.weather = {}
		self.flights = self.get_flight_data()
		self.cost_of_living = 50
		self.food = {'restaurants': 25, 'michelin_stars': 2}
		self.wow_factor = 5

	def __repr__(self):
		return "<Trip origin=%s, destination=%s-%s>" % (self.origin, self.name, self.destination)

	def get_flight_data(self):
	    api_key = os.environ['QPX_KEY']
	    url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + api_key
	    headers = {'content-type': 'application/json'}

	    #round trip api call
	    params = {
	      "request": {
	        "slice": [
	          {
	            "origin": self.origin,
	            "destination": self.destination,
	            "date": self.depart_date,
	            "maxStops":2
	          },
	          {
	            "origin": self.destination,
	            "destination": self.origin,
	            "date": self.return_date,
	            "maxStops":2
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

	    total_fare = float(first_option['saleTotal'][3:])
	    to_duration = round(float(first_option['slice'][0]['duration'])/60,2)
	    to_stops = len(first_option['slice'][0]['segment']) - 1
	    from_duration = round(float(first_option['slice'][1]['duration'])/60,2)
	    from_stops = len(first_option['slice'][1]['segment']) - 1

	    return {'total_fare': total_fare, 
	            'to_data': (to_stops, to_duration), 
	            'from_data': (from_stops, from_duration)}

	def get_weather_data(self, latitude, longitude):
		api_key = os.environ['WEATHER_KEY']
		date_last_year = datetime.strftime(datetime.strptime(self.depart_date, '%Y-%m-%d') - timedelta(days=365), '%Y-%m-%d')
		r=requests.get(
		'http://api.worldweatheronline.com/premium/v1/past-weather.ashx?key=%s&q=%s&cc=no&date=%s&format=json' 
		%(api_key, str(latitude) + ',' + str(longitude), date_last_year))

		python_dict = json.loads(r.text)

		high_temp = python_dict['data']['weather'][0]['maxtempF']
		low_temp = python_dict['data']['weather'][0]['mintempF']
		return {'high': high_temp, 'low': low_temp}

	def determine_destination(self, user_prefernces={}):
		pass

		