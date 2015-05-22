import json, requests, os
WEATHER_URL = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx?key='

def get_weather(date, latitude, longitude):
	api_key = os.environ['WEATHER_KEY']
	response=requests.get(WEATHER_URL+'%s&q=%s,%s&cc=no&date=%s&format=json' 
	                %(api_key, latitude, longitude, date))

	python_dict = json.loads(response.text)

	high_temp = python_dict['data']['weather'][0]['maxtempF']
	low_temp = python_dict['data']['weather'][0]['mintempF']
	return {'high': high_temp, 'low': low_temp}