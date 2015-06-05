"""Connect to World Weather Online API."""

import json
import requests
import os
from datetime import datetime, timedelta
from model import Airport

WEATHER_URL = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx?key='


def call_weather_api(date, latitude, longitude):
    api_key = os.environ['WEATHER_KEY']
    response = requests.get(WEATHER_URL + '%s&q=%s,%s&cc=no&date=%s&format=json' % (api_key, latitude, longitude, date))

    python_dict = json.loads(response.text)

    high_temp = python_dict['data']['weather'][0]['maxtempF']
    low_temp = python_dict['data']['weather'][0]['mintempF']
    return {'high': high_temp, 'low': low_temp}


def process_weather(depart_date, destination):
    date_last_year = datetime.strftime(datetime.strptime(depart_date, '%Y-%m-%d') - timedelta(days=365), '%Y-%m-%d')
    airport = Airport.query.filter_by(airport_code=destination).first()
    latitude, longitude = airport.latitude, airport.longitude

    try:
        weather = call_weather_api(date_last_year, latitude, longitude)
    except:
        weather = {'high': 80, 'low': 50}
    return weather
