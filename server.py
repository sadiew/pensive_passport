from model import City, Airport, CityImage, Restaurant, Trip, connect_to_db, db
from flask import Flask, request, render_template, redirect, jsonify, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
import flickr


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

    departure_city = City.query.filter_by(name=departure_city[0], country=departure_city[1]).first()
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
    """Display destination decision to user along with underlying data."""
    depart_date = request.form['depart-date']
    return_date = request.form['return-date']
    origin = request.form['departure-airport']
    user_preferences = [request.form['cost'],
                        request.form['food'],
                        request.form['weather']]

    airport_1 = Airport.query.filter_by(airport_code=request.form['airport-1']).first()
    airport_2 = Airport.query.filter_by(airport_code=request.form['airport-2']).first()

    trip1 = Trip(airport_1.city.name, origin, airport_1.airport_code, depart_date, return_date)
    trip2 = Trip(airport_2.city.name, origin, airport_2.airport_code, depart_date, return_date)

    #wow-factor
    trip1.wow_factor = int(request.form['wow-factor-1'])
    trip2.wow_factor = int(request.form['wow-factor-2'])

    #cost of living
    trip1.cost_of_living = airport_1.city.col_index
    trip2.cost_of_living = airport_2.city.col_index

    #weather
    trip1.weather = trip1.get_weather_data(airport_1.latitude, airport_1.longitude)      
    trip2.weather = trip2.get_weather_data(airport_2.latitude, airport_2.longitude)

    #food
    trip1.food = db.session.query(db.func.count(Restaurant.restaurant_id), 
                                db.func.sum(Restaurant.stars)).filter_by(city_id=airport_1.city_id).one()   

    trip2.food = db.session.query(db.func.count(Restaurant.restaurant_id), 
                                db.func.sum(Restaurant.stars)).filter_by(city_id=airport_2.city_id).one()

    winner = trip1.determine_destination(trip2, user_preferences)   
    
    return render_template("results.html",
                            trip1=trip1, 
                            trip2=trip2,
                            winner=winner)

@app.route('/city-list')
def get_cities():
    """Get list of cities for typeahead pre-population."""
    cities = db.session.query(City.name, City.country).all()
    cities_list = [city + ', ' + country for city, country in cities]

    return jsonify({'cities': cities_list})

if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run()