from model import City, Airport, CityImage, Restaurant, Trip, connect_to_db, db
from flask import Flask, request, render_template, redirect, jsonify, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
import flickr, google_places
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

@app.route('/results', methods=['POST'])
def show_results():
    """Display destination decision to user along with underlying data."""
    depart_date = request.form['depart-date']
    return_date = request.form['return-date']
    origin = request.form['departure-airport']
    user_preferences = [request.form['cost'],
                        request.form['food'],
                        request.form['weather']]
    ideal_temp = request.form['ideal-temp']

    trip1 = Trip(origin, request.form['airport-1'], depart_date, return_date)
    trip2 = Trip(origin, request.form['airport-2'], depart_date, return_date)

    trip1.wow_factor = int(request.form['wow-factor-1'])
    trip2.wow_factor = int(request.form['wow-factor-2'])

    session = FuturesSession()

    trip1 = get_external_data(trip1, session)
    trip2 = get_external_data(trip2, session)

    winner = trip1.determine_destination(trip2, user_preferences, ideal_temp)   
    
    return render_template("results.html",
                            trip1=trip1, 
                            trip2=trip2,
                            winner=winner)

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


if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run()