from flask_sqlalchemy import SQLAlchemy
import flickr, psycopg2

import json, requests, os
from datetime import datetime, timedelta

FLIGHT_URL = "https://www.googleapis.com/qpxExpress/v1/trips/search?key="
WEATHER_URL = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx?key='
DEFAULT_IMAGE_URL = 'http://www.posterparty.com/images/photography-paris-france-famous-sights-collage-poster-GB0404.jpg'

db = SQLAlchemy()

# Model definitions

class City(db.Model):
    """Destination city."""

    __tablename__ = "cities"

    city_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64))
    country = db.Column(db.String(64), nullable=False)
    col_index = db.Column(db.Integer)

    def __repr__(self):
        return "<City city_id=%s country=%s>" % (self.name, self.country)

    def get_photo(self):
        """Check to see if photo for city is cached in DB; if not, call Flickr API for new photo."""
        if self.city_images:
            image_url = self.city_images[0].image_url
            print "Image was in DB."
        else:
            flickr_images = flickr.get_flickr_photos(self.airports[0])
            if flickr_images:
                image = CityImage(city_id=self.city_id, image_url=flickr_images[0])
                image_url = image.image_url
                db.session.add(image)
                db.session.commit()
            else:
                image_url = DEFAULT_IMAGE_URL
        self.photo = image_url


class CityImage(db.Model):
    """Image for potential destination city"""
    __tablename__ = "city_images"

    image_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    image_url = db.Column(db.Text)

    city = db.relationship("City",
                           backref=db.backref("city_images", order_by=image_id))


class Airport(db.Model):
    """Destination city."""

    __tablename__ = "airports"

    airport_id = db.Column(db.Integer, primary_key=True)
    airport_code = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    city = db.relationship("City",
                           backref=db.backref("airports", order_by=airport_id))
    

    def __repr__(self):

        return "<Airport airport_code=%s name=%s>" % (self.airport_code, self.name)

class Restaurant(db.Model):
    """Michelin star restuarant"""

    __tablename__ = "restaurants"

    restaurant_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    stars = db.Column(db.Integer, nullable=False)

    city = db.relationship("City",
                           backref=db.backref("restaurants", order_by=restaurant_id))

    def __repr__(self):

        return "<Restaurant name=%s city_id=%s>" % (self.name, self.city_id)

class Trip(object):
    def __init__(self, name, origin, destination, depart_date, return_date):
        self.name = name
        self.origin = origin
        self.destination = destination
        self.depart_date = depart_date
        self.return_date = return_date
        self.weather = {}
        self.flights = self.get_flight_data()
        self.cost_of_living = 46
        self.food = (0,0)
        self.wow_factor = 5

    def __repr__(self):
        return "<Trip origin=%s, destination=%s-%s>" % (self.origin, self.name, self.destination)

    def get_flight_data(self):
        """Call Google Flights API and store flight info in flights attribute."""
        api_key = os.environ['QPX_KEY']
        url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + api_key
        #url = FLIGHT_URL + api_key
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

        raw_fare = first_option['saleTotal'][3:]
        total_fare = float(raw_fare)
        
        to_minutes = first_option['slice'][0]['duration']
        to_hours = round(float(to_minutes)/60,2)
        to_segments = first_option['slice'][0]['segment']
        to_stops = len(to_segments) - 1
        
        from_minutes = first_option['slice'][1]['duration']
        from_hours = round(float(from_minutes)/60,2)
        from_segments = first_option['slice'][1]['segment']
        from_stops = len(from_segments) - 1

        return {'total_fare': total_fare, 
                'to_data': (to_stops, to_hours), 
                'from_data': (from_stops, from_hours)}

        # return {'total_fare': 1000, 
        #         'to_data': (1, 10), 
        #         'from_data': (1, 12)}

    def get_weather_data(self, latitude, longitude):
        """Call weather API and grab historical weather data for respective destination."""
        
        api_key = os.environ['WEATHER_KEY']
        date_last_year = datetime.strftime(datetime.strptime(self.depart_date, '%Y-%m-%d') - timedelta(days=365), '%Y-%m-%d')
        response=requests.get(WEATHER_URL+'%s&q=%s,%s&cc=no&date=%s&format=json' 
                        %(api_key, latitude, longitude, date_last_year))

        python_dict = json.loads(response.text)

        high_temp = python_dict['data']['weather'][0]['maxtempF']
        low_temp = python_dict['data']['weather'][0]['mintempF']
        return {'high': high_temp, 'low': low_temp}

    def determine_destination(self, trip2, user_preferences):
        """Determine ideal destination for user based on preferences."""
        
        #unpack user weightings
        cost_weight, food_weight, weather_weight = user_preferences
        cost_weight, food_weight, weather_weight = float(cost_weight), float(food_weight), float(weather_weight)
        total_weight = cost_weight + food_weight + weather_weight
        print "Total weight: %s, cost_weight: %s, food_weight: %s, weather_weight: %s" %(total_weight,cost_weight, food_weight, weather_weight)
        
        #flight cost delta --> neg is better
        flight_delta = (self.flights['total_fare'] - trip2.flights['total_fare'])/self.flights['total_fare']

        #cost of living delta --> neg is better
        col_delta = (self.cost_of_living - trip2.cost_of_living)/self.cost_of_living

        #weather delta --> neg is better
        IDEAL_TEMP = 70
        trip1_abs_delta = abs(int(self.weather['high']) - IDEAL_TEMP)
        trip2_abs_delta = abs(int(trip2.weather['high']) - IDEAL_TEMP)
        weather_delta = (trip1_abs_delta - trip2_abs_delta)/trip1_abs_delta

        #food_delta --> pos is better
        michelin_star_delta = (self.food[1] - trip2.food[1])/self.food[1]

        #wow_factor_delta
        wow_factor_delta = (self.wow_factor - trip2.wow_factor)/self.wow_factor

        
        final_score = ((food_weight/total_weight)*michelin_star_delta -
                        (cost_weight*0.5/total_weight)*col_delta -
                        (cost_weight*0.5/total_weight)*flight_delta - 
                        (weather_weight/total_weight)*weather_delta)

        #calculate "scores"
        if final_score > 0 and wow_factor_delta >= 0:
            return self.name
        elif final_score < 0 and wow_factor_delta <= 0:
            return trip2.name
        elif final_score > 0 and wow_factor_delta < 0:
            if abs(final_score) > abs(wow_factor_delta):
                return self.name
            else:
                return trip2.name
        elif final_score < 0 and wow_factor_delta > 0:
            if abs(wow_factor_delta) > abs(final_score):
                return self.name
            else:
                return trip2.name    

# Helper functions
def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/pensive_passport'
    #app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."