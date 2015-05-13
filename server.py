from model import City, Airport, CityImage, connect_to_db, db
from flask import Flask, request, render_template, redirect, jsonify, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from trip import Trip
import flickr

#import flickr

app = Flask(__name__)

app.secret_key = "ABC"
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Show index page."""
    return render_template("index.html")

@app.route('/destinaton-form')
def show_destination_form():
	"""Display initial destination form."""
	return render_template("destination_form.html")

@app.route('/preference-form')
def gather_perferences():
    """Return results from homepage."""

    departure_city = request.args.get('departure-city')
    destination_1 = request.args.get('destination-1').split(', ')
    destination_2 = request.args.get('destination-2').split(', ')

    departure_city = City.query.filter_by(name=departure_city).first()
    city1 = City.query.filter_by(name=destination_1[0], country=destination_1[1]).first()
    city2 = City.query.filter_by(name=destination_2[0], country=destination_2[1]).first()

    # assert city1 is not None, "No such city"
    cities = [city1, city2]
    for city in cities:
        city.get_photo()           

    return render_template('preference_form.html',
                            departure_city=departure_city, 
    						city1=city1, 
    						city2=city2)

@app.route('/results', methods=['POST'])
def show_results():
    depart_date = request.form['depart-date']
    return_date = request.form['return-date']
    origin = request.form['departure-airport']
    food_weighting = request.form['food']
    cost_of_living_weighting = request.form['cost-of-living']
    weather_weighting = request.form['weather']
    wow_factor_1 = request.form['wow-factor-1']
    wow_factor_2 = request.form['wow-factor-2']

    airport_1 = Airport.query.filter_by(airport_code=request.form['airport-1']).first()
    airport_2 = Airport.query.filter_by(airport_code=request.form['airport-2']).first()

    restaurants_1 = airport_1.city.restaurants
    restaurants_2 = airport_2.city.restaurants

    trip1 = Trip(airport_1.city.name, origin, airport_1.airport_code, depart_date, return_date)
    trip2 = Trip(airport_2.city.name, origin, airport_2.airport_code, depart_date, return_date)

    trip1.wow_factor = wow_factor_1
    trip1.cost_of_living = airport_1.city.col_index
    trip1.weather = trip1.get_weather_data(airport_1.latitude, airport_1.longitude)
    trip1.food = {'restaurants':len(restaurants_1), 
                  'stars': sum(restaurant.stars for restaurant in restaurants_1)}

    trip2.wow_factor = wow_factor_2   
    trip2.cost_of_living = airport_2.city.col_index   
    trip2.weather = trip2.get_weather_data(airport_2.latitude, airport_2.longitude)
    
    return render_template("results.html",
                            trip1=trip1, 
                            trip2=trip2)

if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run()