def determine_destination():
	"""Calculate scores for each destination and return destination with higher score."""
	
	trip1 = Trip(session['depart_date'], session['return_date'], session[airport1.city], ....)

	trip1.weather = get_weather_data()
	trip2.weather = get_weather_data()
	trip1.flight = get_flight_data()
	trip2.flight = get_flight_data()
	

#Maybe these should be class methods on the Trip class?
def get_flight_data(departure_city, arrival_city, depart_date, return_date):
	"""Gather flight data for a given destination."""

	#return a dictionary with 'cost' and 'num_stops' as keys


def get_weather_data(latitude, longitude, depart_date):
	"""Gather weather data for a given destination."""

	#return a dictionary with 'temp' and 'precipitation' as keys