import json, requests, os
from requests_futures.sessions import FuturesSession
from datetime import datetime, timedelta
from model import City, Airport

import weather, google_flights

def get_external_data(trip1, trip2):
	date_last_year = datetime.strftime(datetime.strptime(trip1.depart_date, '%Y-%m-%d') - timedelta(days=365), '%Y-%m-%d')
	headers = {'content-type': 'application/json'}
	airport1 = Airport.query.filter_by(airport_code=trip1.destination).first()
	latitude1 = airport1.latitude
	longitude1 = airport1.longitude

	weather1_url = weather.get_url(date_last_year, latitude1, longitude1)
	flight1_url, params_1 = google_flights.get_url(trip1.origin, trip1.destination, trip1.depart_date, trip1.return_date)

	airport2 = Airport.query.filter_by(airport_code=trip2.destination).first()
	latitude2 = airport2.latitude
	longitude2 = airport2.longitude

	weather2_url = weather.get_url(date_last_year, latitude2, longitude2)
	flight2_url, params_2 = google_flights.get_url(trip2.origin, trip2.destination, trip2.depart_date, trip2.return_date)
	
	session = FuturesSession()

	weather1_future = session.get(weather1_url)
	flight1_future = session.post(flight1_url, data=json.dumps(params_1), headers=headers)
	weather2_future = session.get(weather2_url)
	flight2_future = session.post(flight2_url, data=json.dumps(params_2), headers=headers)

	weather1_response = weather1_future.result()
	flight1_response = flight1_future.result()
	weather2_response = weather2_future.result()
	flight2_response = flight2_future.result()

	trip1.flights = google_flights.process_response(flight1_response.content)
	trip2.flights = google_flights.process_response(flight2_response.content)
	trip1.weather = weather.process_response(weather1_response.content)
	trip2.weather = weather.process_response(weather2_response.content)

	return [trip1, trip2]

