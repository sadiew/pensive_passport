from model import City, Airport, CityImage, Restaurant, Trip, connect_to_db, db
from flask import Flask, request, render_template, redirect, jsonify, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from datetime import datetime, timedelta
import flickr, google_places
from google_flights import get_flights
from weather import get_weather
from requests_futures.sessions import FuturesSession
from external_apis import get_external_data


app = Flask(__name__)

app.secret_key = "ABC"
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Show index page."""
    return render_template("index.html")

@app.route('/preference-form')
def gather_perferences():
    """Gather user preferences."""

    departure_city = request.args.get('departure-city').split(', ')
    destination_1 = request.args.get('destination-1').split(', ')
    destination_2 = request.args.get('destination-2').split(', ')

    origin_city = City.query.filter_by(name=departure_city[0], state=departure_city[1]).first()
    city1 = City.query.filter_by(name=destination_1[0], country=destination_1[1]).first()
    city2 = City.query.filter_by(name=destination_2[0], country=destination_2[1]).first()

    city1.get_photo() 
    city2.get_photo()         

    return render_template('preference_form.html',
                            origin_city=origin_city, 
    						city1=city1, 
    						city2=city2)

@app.route('/results')
def show_results():
    """Display map of city that user chose along with accompanying attractions."""
    city, country = request.args['winning-city'].split(', ') 
    
    return render_template("results.html",
                            city=city,
                            country=country)

@app.route('/intl-city-list')
def get_cities():
    """Get list of cities for typeahead pre-population."""
    cities = db.session.query(City.name, City.country).filter(City.country!="United States").all()
    cities_list = [city + ', ' + country for city, country in cities]

    return jsonify({'cities': cities_list})

@app.route('/us-city-list')
def get_us_cities():
    """Get list of cities for typeahead pre-population."""
    us_cities = db.session.query(City.name, City.state).filter(City.country=="United States", City.state!="").all()
    us_cities_list = [city + ', ' + state for city, state in us_cities]

    return jsonify({'us_cities': us_cities_list})

@app.route('/get-restaurants', methods=['POST'])
def get_restaurants():
    city = request.form.get('city')
    country = request.form.get('country')
    
    restaurants = google_places.get_places(city, country, place_type ='restaurant')
    return jsonify(restaurants)

@app.route('/get-museums', methods=['POST'])
def get_museums():
    city = request.form.get('city')
    country = request.form.get('country')
    museums = google_places.get_places(city, country, place_type ='museum')
    return jsonify(museums)

@app.route('/get-parks', methods=['POST'])
def get_parks():
    city = request.form.get('city')
    country = request.form.get('country')
    parks = google_places.get_places(city, country, place_type ='park')
    return jsonify(parks)

@app.route('/get-first-flight', methods=['POST'])
def get_first_flight():
    depart_date = request.form['depart_date']
    return_date = request.form['return_date']
    origin = request.form['origin']
    destination = request.form['destination']

    # airfare = get_flights(origin, destination, depart_date, return_date)
    # return jsonify(airfare)
    #return {'airfare': 1000}

@app.route('/get-second-flight', methods=['POST'])
def get_second_flight():
    depart_date = request.form['depart_date']
    return_date = request.form['return_date']
    origin = request.form['origin']
    destination = request.form['destination']

    # airfare = get_flights(origin, destination, depart_date, return_date)
    # return jsonify(airfare)
    #return {'airfare': 1000}

@app.route('/get-first-weather', methods=['POST'])
def get_first_weather():
    depart_date = request.form['depart_date']
    destination = request.form['destination']

    date_last_year = datetime.strftime(datetime.strptime(depart_date, '%Y-%m-%d') - 
                        timedelta(days=365), '%Y-%m-%d')
    airport = Airport.query.filter_by(airport_code=destination).first()
    latitude = airport.latitude
    longitude = airport.longitude

    weather = get_weather(date_last_year, latitude, longitude)
    return jsonify(weather)

@app.route('/get-second-weather', methods=['POST'])
def get_second_weather():
    depart_date = request.form['depart_date']
    destination = request.form['destination']

    date_last_year = datetime.strftime(datetime.strptime(depart_date, '%Y-%m-%d') - 
                        timedelta(days=365), '%Y-%m-%d')
    airport = Airport.query.filter_by(airport_code=destination).first()
    latitude = airport.latitude
    longitude = airport.longitude

    weather = get_weather(date_last_year, latitude, longitude)
    return jsonify(weather)

@app.route('/get-city1-data', methods=['GET'])
def get_city1_data():
    airport_code = request.args['airport-1']
    city_stats = fetch_city_data(airport_code)

    return jsonify(city_stats)

@app.route('/get-city2-data', methods=['GET'])
def get_city2_data():
    airport_code = request.args['airport-2']
    city_stats = fetch_city_data(airport_code)

    return jsonify(city_stats)


#helper functions
def fetch_city_data(airport_code):
    airport = Airport.query.filter_by(airport_code=airport_code).first()
    city_id = airport.city.city_id
    name = airport.city.name
    country = airport.city.country
    cost_of_living = airport.city.col_index
    food = db.session.query(db.func.count(Restaurant.restaurant_id), 
                            db.func.sum(Restaurant.stars)).filter_by(city_id=city_id).one()

    city_stats = {'name': name,
                  'country': country,
                  'costOfLiving': cost_of_living,
                  'food': {'restarants': food[0], 'stars': food[1]}}
    return city_stats




if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run()