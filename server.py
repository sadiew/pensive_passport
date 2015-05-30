from model import City, Airport, Restaurant, Place, Trip, User, Search, connect_to_db, db
from flask import Flask, request, render_template, redirect, jsonify, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from datetime import datetime, timedelta
from google_places import get_places
from google_flights import get_flights
from weather import get_weather
import json
import psycopg2


app = Flask(__name__)

app.secret_key = "ABC"
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Show index page."""

    return render_template("homepage.html", session=session)


@app.route('/search')
def search():
    """Show index page."""

    return render_template("search.html")


@app.route('/preference-form')
def gather_perferences():
    """Gather user preferences."""

    try:
        departure_city, departure_country = request.args.get('departure-city').split(', ')
        dest_1_city, dest_1_country = request.args.get('destination-1').split(', ')
        dest_2_city, dest_2_country = request.args.get('destination-2').split(', ')

        origin_city = City.query.filter_by(name=departure_city, state=departure_country).first()
        city1 = City.query.filter_by(name=dest_1_city, country=dest_1_country).first()
        city2 = City.query.filter_by(name=dest_2_city, country=dest_2_country).first()

        city1.get_photos()
        city2.get_photos()

        max_photos = min(len(city1.photos), len(city2.photos))

        return render_template('preference_form.html', origin_city=origin_city, city1=city1,
                                city2=city2, max_photos=max_photos, session=session)
    except:
        flash("Please enter a valid choice from the dropdown menu.")
        return redirect('/')


@app.route('/results')
def show_results():
    """Display map of city that user chose along with accompanying attractions."""

    city_id = request.args['city_id']
    city = City.query.get(city_id)

    return render_template("results.html", city=city, session=session)


@app.route('/intl-city-list')
def get_cities():
    """Get list of cities for typeahead pre-population."""

    cities = db.session.query(City.name, City.country).filter(City.country != "United States").all()
    cities_list = [city + ', ' + country for city, country in cities]

    return jsonify({'cities': cities_list})


@app.route('/us-city-list')
def get_us_cities():
    """Get list of cities for typeahead pre-population."""

    us_cities = db.session.query(City.name, City.state).filter(City.country == "United States", City.state != "").all()
    us_cities_list = [city + ', ' + state for city, state in us_cities]

    return jsonify({'us_cities': us_cities_list})


@app.route('/get-restaurants', methods=['POST'])
def get_restaurants():
    """Grab restaurants from DB if cached, otherwise call Google Places API."""

    city_id = int(request.form.get('city_id'))
    city_center = tuple(request.form.get('city_lat_lon').split(","))

    restaurants = add_places(city_id, city_center, place_type='restaurant')

    return jsonify(restaurants)


@app.route('/get-museums', methods=['POST'])
def get_museums():
    """Grab museums from DB if cached, otherwise call Google Places API."""

    city_id = int(request.form.get('city_id'))
    city_center = tuple(request.form.get('city_lat_lon').split(","))

    museums = add_places(city_id, city_center, place_type='museum')
    return jsonify(museums)


@app.route('/get-parks', methods=['POST'])
def get_parks():
    """Grab parks from DB if cached, otherwise call Google Places API."""

    city_id = int(request.form.get('city_id'))
    city_center = tuple(request.form.get('city_lat_lon').split(","))

    parks = add_places(city_id, city_center, place_type='park')

    return jsonify(parks)


@app.route('/get-flight1', methods=['POST'])
def get_first_flight():
    """Grab cost of airfare from Google flights for first city."""

    depart_date = request.form['depart_date']
    return_date = request.form['return_date']
    origin = request.form['origin']
    destination = request.form['destination']

    airfare = process_flights(origin, destination, depart_date, return_date)
    #airfare = {'airfare': 1272}
    return jsonify(airfare)


@app.route('/get-flight2', methods=['POST'])
def get_second_flight():
    """Grab cost of airfare from Google flights for second city."""

    depart_date = request.form['depart_date']
    return_date = request.form['return_date']
    origin = request.form['origin']
    destination = request.form['destination']

    airfare = process_flights(origin, destination, depart_date, return_date)
    #airfare = {'airfare': 1753}
    return jsonify(airfare)


@app.route('/get-weather1', methods=['POST'])
def get_first_weather():
    """Grab weather data from World Weather Online for first city."""

    depart_date = request.form['depart_date']
    destination = request.form['destination']

    weather = process_weather(depart_date, destination)
    return jsonify(weather)


@app.route('/get-weather2', methods=['POST'])
def get_second_weather():
    """Grab weather data from World Weather Online for second city."""

    depart_date = request.form['depart_date']
    destination = request.form['destination']

    weather = process_weather(depart_date, destination)
    return jsonify(weather)


@app.route('/get-city1-data', methods=['GET'])
def get_city1_data():
    """Grab city specific data (city, country, cost of living, Michelin star restaurants)
    from DB for first city."""

    airport_code = request.args['airport-1']
    city_stats = fetch_city_data(airport_code)

    return jsonify(city_stats)


@app.route('/get-city2-data', methods=['GET'])
def get_city2_data():
    """Grab city specific data (city, country, cost of living, Michelin star restaurants)
    from DB for second city."""

    airport_code = request.args['airport-2']
    city_stats = fetch_city_data(airport_code)

    return jsonify(city_stats)


@app.route('/store-trips', methods=['POST'])
def store_trips():
    """Add each trip search to the DB."""

    search = Search(user_id=session['username'])
    db.session.add(search)
    db.session.commit()

    trip1 = json.loads(request.form['trip1'])
    trip2 = json.loads(request.form['trip2'])
    trips = [trip1, trip2]

    for trip in trips:
        trip = Trip(city_id=trip['city_id'],
                    search_id=search.search_id,
                    avg_temp=trip['weather'],
                    wow_factor=trip['wow'],
                    michelin_stars=trip['food'],
                    airfare=trip['airfare'])
        db.session.add(trip)
    db.session.commit()

    return 'success'


@app.route('/login')
def login():
    """Login form"""

    return render_template('login_form.html', session=session)


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
    else:
        if user and (user.password == request.form['password']):
            session['username'] = user.user_id
            flash("Login successful!")
            return redirect('/search')
        else:
            flash("Invalid login.")
            return redirect("/login")


@app.route('/registration-submission', methods=['POST'])
def handle_registration():
    """Handles the registration form and adds the user to DB and session."""

    username = request.form['username']
    password = request.form['password']
    reenter_password = request.form['reenter_password']
    age = request.form['age']
    zipcode = request.form['zipcode']

    if password == reenter_password:
        user = User(email=username, password=password, age=age, zipcode=zipcode)
        session['username'] = user.user_id

        db.session.add(user)
        db.session.commit()

        flash("Thank you for registering!")
        return redirect('/search')
    else:
        flash("Passwords do not match, try again.")
        return render_template('register.html', session=session)


@app.route('/get-similar-trips')
def get_similar_trips():
    """Searches the DB for destinations searched by others who searched the same original cities."""

    city_id = request.args['city_id']

    if 'username' in session:
        user_id = session['username']
    else:
        user_id = 0

    query = """SELECT DISTINCT trips.city_id, cities.name, cities.country, COUNT(trips.city_id)
            FROM trips
            JOIN cities on trips.city_id = cities.city_id
            JOIN searches on trips.search_id = searches.search_id
            WHERE user_id IN
                (SELECT DISTINCT user_id
                FROM searches
                JOIN trips on searches.search_id = trips.search_id
                WHERE city_id =%s)
            AND trips.city_id NOT IN
                (SELECT DISTINCT city_id
                FROM trips
                JOIN searches on trips.search_id=searches.search_id
                WHERE searches.user_id=%s)
            GROUP BY 1,2,3
            ORDER BY COUNT(trips.city_id) DESC
            LIMIT 4""" % (city_id, user_id)

    results = call_sql(query)
    user_similar_cities = {result[0]: '%s, %s' % (result[1], result[2]) for result in results}

    return jsonify(user_similar_cities)


@app.route('/get-nltk-trips')
def get_nltk_trips():
    city_id = request.args['city_id']

    query = """SELECT city_id_1, city_id_2
             FROM similarities
             WHERE city_id_1 = %s OR city_id_2 = %s
             ORDER BY similarity
             DESC LIMIT 4;""" % (city_id, city_id)

    results = call_sql(query)
    if results:
        similar_cities = []
        for result in results:
            if result[0] == city_id:
                city = City.query.get(result[1])
                similar_cities.append(city)
            else:
                city = City.query.get(result[0])
                similar_cities.append(city)
        nltk_similar_cities = {city.city_id: '%s, %s' % (city.name, city.country) for city in similar_cities}

    return jsonify(nltk_similar_cities)


@app.route('/cities/<int:city_id>')
def show_city(city_id):
    """Grab data to present a quick city snapshot, including Michelin star data,
    average wow score, and average airfare."""

    city = City.query.get(city_id)
    food = db.session.query(db.func.count(Restaurant.restaurant_id),
                            db.func.sum(Restaurant.stars)).filter_by(city_id=city.city_id).one()

    avg_wow = db.session.query(db.func.avg(Trip.wow_factor)).filter_by(city_id=city.city_id).one()
    avg_airfare = db.session.query(db.func.avg(Trip.airfare)).filter_by(city_id=city.city_id).one()

    city.food = [food[0], food[1]]
    city.avg_wow = round(avg_wow[0], 1)
    city.avg_airfare = int(avg_airfare[0])

    return render_template('city.html', city=city, session=session)

# helper functions


def process_flights(origin, destination, depart_date, return_date):
    """Attempt to call Google flights API, but return default values
    if unavailable."""

    try:
        airfare = get_flights(origin, destination, depart_date, return_date)
    except:
        flash("Flight info unavailable. Default values assigned.")
        airfare = {'airfare': 1000}

    return airfare


def process_weather(depart_date, destination):
    """Attempt to call World Weather Online API,but return default
    values if unavailable."""

    date_last_year = datetime.strftime(datetime.strptime(depart_date, '%Y-%m-%d') - timedelta(days=365), '%Y-%m-%d')
    airport = Airport.query.filter_by(airport_code=destination).first()
    latitude, longitude = airport.latitude, airport.longitude

    try:
        weather = get_weather(date_last_year, latitude, longitude)
    except:
        flash("Weather info unavailable. Default values assinged.")
        weather = {'high': 80, 'low': 50}
    return weather


def fetch_city_data(airport_code):
    """Fetch city specific data from DB for trip comparison."""

    airport = Airport.query.filter_by(airport_code=airport_code).first()
    city_id = airport.city.city_id
    name = airport.city.name
    country = airport.city.country
    cost_of_living = airport.city.col_index
    food = db.session.query(db.func.count(Restaurant.restaurant_id),
                            db.func.sum(Restaurant.stars)).filter_by(city_id=city_id).one()

    city_stats = {'city_id': city_id,
                  'city': name,
                  'country': country,
                  'costOfLiving': cost_of_living,
                  'food': {'restarants': food[0], 'stars': food[1]}}
    return city_stats


def call_sql(query):
    """Connect to Postgres. If connection fails, return an exception."""

    try:
        conn = psycopg2.connect("dbname='pensive_passport' host='localhost' port=5432")
        cur = conn.cursor()
        cur.execute(query)
        return cur.fetchall()
    except Exception, e:
        print "\nCan't connect to the database!"
        print e
        print '\n'


def add_places(city_id, city_center, place_type):
    """Check to see if place type for given city is already stored in DB. If so,
    return 5 establishments closes to city center.  If not, call Google
    Places API to grab 20 most prominent places, and then of those, select 5 closest
    to city center."""

    places = Place.query.filter_by(city_id=city_id, place_type=place_type).all()

    if places:
        ten_closest_places = select_ten_closest_prominent(places, city_center)

    else:
        city_object = City.query.get(city_id)
        city, country = city_object.name, city_object.country
        places = get_places(city, country, place_type)

        for place in places:
            place = Place(google_place_id=places[place]['google_place_id'],
                          city_id=city_id,
                          name=place,
                          lat=places[place]['lat'],
                          lon=places[place]['lng'],
                          place_type=place_type)
            db.session.add(place)
        db.session.commit()

        places = Place.query.filter_by(city_id=city_id, place_type=place_type).all()
        ten_closest_places = select_ten_closest_prominent(places, city_center)

    return ten_closest_places


def distance_from_city_center(city_center, place):
    """Calculate the distance of a place from its respective city center given as a tuple
    of lat at index 0 and lon at index 1."""

    city_lat = float(city_center[0])
    city_lon = float(city_center[1])

    distance_from_center = abs(place.lat-city_lat) + abs(place.lon-city_lon)

    return round(distance_from_center, 3)


def select_ten_closest_prominent(places, city_center):
    """Calculate the distance of each place from city center, then rank in ascending
    order by distance and take the top 5 with shortest distance."""

    distance_from_center = {place.name: distance_from_city_center(city_center, place) for place in places}
    closest_places = sorted(distance_from_center.items(), key=lambda x: x[1])
    closest_places_list = [place[0] for place in closest_places]

    ten_closest_places = {place.name: place.google_place_id for place in places if place.name in closest_places_list[:10]}
    return ten_closest_places


if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run()