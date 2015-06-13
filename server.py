import json
import os

from flask import Flask, request, render_template, redirect, jsonify
from flask import session, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from datetime import datetime, date, timedelta

from model import City, Airport, Restaurant, Place, Trip, User, Search
from model import connect_to_db, db

from flights import process_flights
from places import call_places_api
from weather import process_weather
from similar_trips import get_user_similar_trips, get_nl_similar_trips


SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "development")

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Show home page."""

    return render_template("homepage.html", session=session)


@app.route('/search')
def search():
    """Show search page."""

    return render_template("search.html")


@app.route('/preference-form', methods=['GET', 'POST'])
def gather_perferences():
    """Gather user preferences."""

    try:
        depart_city, depart_country = request.args['depart-city'].split(', ')
        dest_1_city, dest_1_country = request.args['dest-1'].split(', ')
        dest_2_city, dest_2_country = request.args['dest-2'].split(', ')

    except ValueError:
        flash("Please enter a valid choice from the dropdown menu.")
        return redirect('/search')

    origin_city = City.query.filter_by(name=depart_city,
                                       state=depart_country).first()
    city1 = City.query.filter_by(name=dest_1_city,
                                 country=dest_1_country).first()
    city2 = City.query.filter_by(name=dest_2_city,
                                 country=dest_2_country).first()

    city1.get_photos()
    city2.get_photos()

    nphotos = min(len(city1.photos), len(city2.photos))
    start_date = datetime.strftime(date.today() + timedelta(days=14), '%Y-%m-%d')
    end_date = datetime.strftime(date.today() + timedelta(days=28), '%Y-%m-%d')

    return render_template('preference_form.html',
                           origin_city=origin_city,
                           city1=city1,
                           city2=city2,
                           nphotos=nphotos,
                           start_date=start_date,
                           end_date=end_date)


@app.route('/winning-city')
def show_results():
    """Display map of city along with attractions."""

    city_id = request.args['city_id']
    city = City.query.get(city_id)

    return render_template("winning_city.html", city=city)


@app.route('/login')
def login():
    """Login form"""

    return render_template('login_form.html')


@app.route('/logout')
def logout():
    """Log user out - return to homepage"""

    del session['username']
    flash("You have been successfully logged out. Please return soon!")

    return redirect('/')


@app.route('/login-submission', methods=['POST'])
def handle_login():
    """Handles the login form and adds the user to the session."""

    user = User.query.filter_by(email=request.form['username']).first()

    if not user:
        return render_template('register.html')

    if user.password == request.form['password']:
        session['username'] = user.user_id
        flash("Login successful!")
        return redirect('/user/' + str(user.user_id))
    else:
        flash("Invalid login.")
        return redirect("/login")


@app.route('/registration-submission', methods=['POST'])
def handle_registration():
    """Handles registration and adds user to DB and session."""

    username = request.form['username']
    password = request.form['password']
    reenter_password = request.form['reenter_password']
    age = request.form['age']
    zipcode = request.form['zipcode']

    if password == reenter_password:
        user = User(email=username,
                    password=password,
                    age=age,
                    zipcode=zipcode)
        session['username'] = user.user_id

        db.session.add(user)
        db.session.commit()

        flash("Thank you for registering!")
        return redirect('/search')
    else:
        flash("Passwords do not match, try again.")
        return render_template('register.html')


@app.route('/city/<int:city_id>')
def show_city_details(city_id):
    """Grab data to present quick city snapshot."""

    city = City.query.get(city_id)
    restaurants, stars = db.session \
        .query(db.func.count(Restaurant.restaurant_id),
               db.func.sum(Restaurant.stars)) \
        .filter_by(city_id=city.city_id).one()

    avg_wow = db.session \
        .query(db.func.avg(Trip.wow_factor)) \
        .filter_by(city_id=city.city_id) \
        .scalar()

    avg_airfare = db.session \
        .query(db.func.avg(Trip.airfare)) \
        .filter_by(city_id=city.city_id).scalar()

    city.food = [restaurants, stars]
    city.avg_wow = round(avg_wow, 1)
    city.avg_airfare = int(avg_airfare)

    return render_template('city.html', city=city)


@app.route('/user/<int:user_id>')
def show_user_details(user_id):
    """Show past searches for logged-in user."""

    user = User.query.get(user_id)

    # sort cities in each pair in order to remove duplicate entries
    searches = [tuple(sorted([search.trips[0].city.name, search.trips[1].city.name]))
                for search in user.searches]

    unique_searches = set(searches)

    return render_template("user.html", searches=unique_searches)


@app.route('/intl-city-list')
def get_cities():
    """Get list of intl cities for typeahead pre-population."""

    intl_cities = db.session.query(City.name, City.country) \
        .filter(City.country != "United States").all()

    intl_cities_list = [city + ', ' + country
                        for city, country in intl_cities]

    return jsonify({'intlCities': intl_cities_list})


@app.route('/us-city-list')
def get_us_cities():
    """Get list of US cities for typeahead pre-population."""

    us_cities = db.session.query(City.name, City.state) \
        .filter(City.country == "United States", City.state != "").all()

    us_cities_list = [city + ', ' + state for city, state in us_cities]

    return jsonify({'usCities': us_cities_list})


@app.route('/get-flight', methods=['POST'])
def get_flight():
    """Grab cost of airfare from Google flights."""

    depart_date = request.form['depart_date']
    return_date = request.form['return_date']
    origin = request.form['origin']
    destination = request.form['destination']

    airfare = process_flights(origin, destination, depart_date, return_date)

    return jsonify(airfare)


@app.route('/get-weather', methods=['POST'])
def get_weather():
    """Grab weather data from World Weather Online."""

    depart_date = request.form['depart_date']
    destination = request.form['destination']

    weather = process_weather(depart_date, destination)

    return jsonify(weather)


@app.route('/get-city-data', methods=['GET'])
def get_city_data():
    """Grab city specific data from DB."""

    airport_code = request.args['airport']
    city_stats = fetch_city_data(airport_code)

    return jsonify(city_stats)


@app.route('/store-trips', methods=['POST'])
def store_trips():
    """Add each trip search to the DB."""

    search = Search(user_id=session['username'])
    db.session.add(search)
    db.session.flush()

    trip1 = json.loads(request.form['trip1'])
    trip2 = json.loads(request.form['trip2'])
    trips = [trip1, trip2]

    for trip in trips:
        trip = Trip(city_id=trip['cityId'],
                    search_id=search.search_id,
                    avg_temp=trip['weather'],
                    wow_factor=trip['wow'],
                    michelin_stars=trip['stars'],
                    airfare=trip['airfare'])
        db.session.add(trip)
    db.session.commit()

    return 'success'


@app.route('/get-places', methods=['POST'])
def get_places():
    """Grab places from DB if cached, otherwise call Google Places API."""

    city_id = int(request.form['city_id'])
    city_center = request.form['city_lat_lon']
    place_type = request.form['place_type']

    places = process_places(city_id, city_center, place_type=place_type)

    return jsonify(places)


@app.route('/get-similar-trips')
def get_similar_trips():
    """Make recommendations to user for other destinations."""

    city_id = request.args['city_id']
    user_id = session.get('username', 0)

    user_similar_cities = get_user_similar_trips(city_id, user_id)
    num_matches = len(user_similar_cities)
    num_needed = 4 - num_matches

    if num_needed == 0:
        return jsonify(user_similar_cities)

    else:
        nltk_similar_cities = get_nl_similar_trips(city_id, num_needed)
        if num_needed < 4:
            return jsonify(user_similar_cities.update(nltk_similar_cities))
        else:
            return jsonify(nltk_similar_cities)


# helper functions


def fetch_city_data(airport_code):
    """Fetch city specific data from DB for trip comparison."""

    airport = Airport.query.filter_by(airport_code=airport_code).first()

    michelin_stars = db.session \
        .query(db.func.sum(Restaurant.stars)) \
        .filter_by(city_id=airport.city.city_id).scalar()

    city_stats = {'cityId': airport.city.city_id,
                  'city': airport.city.name,
                  'country': airport.city.country,
                  'costOfLiving': airport.city.col_index,
                  'stars': michelin_stars}

    return city_stats


def process_places(city_id, city_center, place_type):
    """Get city specific places by type."""

    places = Place.query.filter_by(city_id=city_id,
                                   place_type=place_type).all()

    if not places:
        data = call_places_api(city_center, place_type)
        add_places_to_db(city_id, data, place_type)
        places = Place.query \
            .filter_by(city_id=city_id, place_type=place_type).all()

    return select_ten_closest(places, city_center)


def add_places_to_db(city_id, data, place_type):
    """Add places gather from Google Places to DB."""

    for result in data['results']:
        place = Place(google_place_id=result['place_id'],
                      city_id=city_id,
                      name=result['name'].encode('utf8'),
                      lat=result['geometry']['location']['lat'],
                      lon=result['geometry']['location']['lng'],
                      place_type=place_type)
        db.session.add(place)
    db.session.commit()


def distance_from_city_center(city_center, place):
    """Distance of a place from its city center 'lat, lon'."""

    lat, lon = (float(coord) for coord in city_center.split(","))

    distance = abs(place.lat-lat) + abs(place.lon-lon)

    return round(distance, 3)


def select_ten_closest(places, city_center):
    """Rank places in asc. order by distance and take top 10."""

    distance = {place.name: distance_from_city_center(city_center, place)
                for place in places}

    # sort by distance from city center
    closest_places = sorted(distance.items(), key=lambda x: x[1])
    closest_places_list = [place[0] for place in closest_places]

    return {place.name: place.google_place_id
            for place in places
            if place.name in closest_places_list[:10]}


if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = "NO_DEBUG" not in os.environ

    connect_to_db(app)

    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)
