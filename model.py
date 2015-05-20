from flask_sqlalchemy import SQLAlchemy

import json, requests, os, psycopg2, random
from datetime import datetime, timedelta
import flickr, google_flights, weather

DEFAULT_IMAGE_URL = 'http://www.posterparty.com/images/photography-paris-france-famous-sights-collage-poster-GB0404.jpg'

db = SQLAlchemy()

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
            flickr_images = flickr.get_flickr_photos(self)
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

class Place(db.Model):
    __tablename__ = "places"

    place_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    place_type = db.Column(db.String(10), nullable=False)

    city = db.relationship("City",
                           backref=db.backref("places", order_by=place_id))

    def __repr__(self):

        return "<Place name=%s city_id=%s>" % (self.name, self.city_id)


class Trip(object):
    def __init__(self, origin, destination, depart_date, return_date):
        self.origin = origin
        self.destination = destination
        self.depart_date = depart_date
        self.return_date = return_date
        # self.weather = self.get_weather_data()
        # self.flights = self.get_flight_data()
        self.get_city_data()

    def __repr__(self):
        return "<Trip origin=%s, destination=%s-%s>" % (self.origin, self.name, self.destination)

    def get_city_data(self):
        airport = Airport.query.filter_by(airport_code=self.destination).first()
        city_id = airport.city.city_id
        self.name = airport.city.name
        self.country = airport.city.country
        self.cost_of_living = airport.city.col_index
        self.food = db.session.query(db.func.count(Restaurant.restaurant_id), 
                                db.func.sum(Restaurant.stars)).filter_by(city_id=city_id).one()

    def get_flight_data(self):
        """Call Google Flights API and store flight info in flights attribute."""

        try:
            flights = google_flights.get_flights(self.origin, self.destination, self.depart_date, self.return_date)
            return flights

        except:
            flash('Unable to get flight info for %s at this time. Default values assigned.' %(self.name))
            return {'total_fare': 1000, 
                'to_data': (1, 10), 
                'from_data': (1, 12)}

    def get_weather_data(self):
        """Call weather API and grab historical weather data for respective destination."""
        date_last_year = datetime.strftime(datetime.strptime(self.depart_date, '%Y-%m-%d') - timedelta(days=365), '%Y-%m-%d')
        airport = Airport.query.filter_by(airport_code=self.destination).first()
        latitude = airport.latitude
        longitude = airport.longitude

        try:
            weather_data = weather.get_weather(date_last_year, latitude, longitude)
            return weather_data
        except:
            flash('Unable to get weather info for %s at this time. Default values assigned.' %(self.name))
            return {'high': 75, 'low': 55}
        

    def determine_destination(self, trip2, user_preferences):
        """Determine ideal destination for user based on preferences."""
        
        #unpack user weightings
        cost_weight, food_weight, weather_weight = user_preferences
        cost_weight, food_weight, weather_weight = float(cost_weight), float(food_weight), float(weather_weight)
        total_weight = cost_weight + food_weight + weather_weight
        
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
        try:
            michelin_star_delta = (self.food[1] - trip2.food[1])/self.food[1]
        except:
            michelin_star_delta = 0

        #wow_factor_delta
        wow_factor_delta = (self.wow_factor - trip2.wow_factor)/self.wow_factor

        
        final_score = ((food_weight/total_weight)*michelin_star_delta -
                        (cost_weight*0.5/total_weight)*col_delta -
                        (cost_weight*0.5/total_weight)*flight_delta - 
                        (weather_weight/total_weight)*weather_delta)

        #calculate "scores"
        if final_score > 0 and wow_factor_delta >= 0:
            return self
        elif final_score < 0 and wow_factor_delta <= 0:
            return trip2
        elif final_score > 0 and wow_factor_delta < 0:
            if final_score > abs(wow_factor_delta):
                return self
            else:
                return trip2
        elif final_score < 0 and wow_factor_delta > 0:
            if wow_factor_delta > abs(final_score):
                return self
            else:
                return trip2
        else:
            return random.choice([self, trip2])    

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