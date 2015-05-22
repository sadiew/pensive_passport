import json, requests, os
from requests_futures.sessions import FuturesSession
from datetime import datetime, timedelta

from model import Airport
import weather, google_flights

def get_external_data(trip, session):
	date_last_year = datetime.strftime(datetime.strptime(trip.depart_date, '%Y-%m-%d') - timedelta(days=365), '%Y-%m-%d')
	headers = {'content-type': 'application/json'}
	airport = Airport.query.filter_by(airport_code=trip.destination).first()
	latitude = airport.latitude
	longitude = airport.longitude

	weather_url = weather.get_url(date_last_year, latitude, longitude)
	flight_url, params = google_flights.get_url(trip.origin, trip.destination, trip.depart_date, trip.return_date)

	weather_future = session.get(weather_url)
	flight_future = session.post(flight_url, data=json.dumps(params), headers=headers)

	weather_response = weather_future.result()
	flight_response = flight_future.result()

	trip.flights = google_flights.process_response(flight_response.content)
	trip.weather = weather.process_response(weather_response.content)

	return trip

