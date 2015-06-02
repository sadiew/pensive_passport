from model import City, Airport, Restaurant, Place, Trip, User, Search, connect_to_db, db
from flask import Flask, request, render_template, redirect, jsonify, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from google_flights import process_flights
from new_places import get_places
from weather import process_weather
from similar_trips import get_user_similar_trips, get_nl_similar_trips
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
        departure_city, departure_country = request.args['depart-city'].split(', ')
        dest_1_city, dest_1_country = request.args['dest-1'].split(', ')
        dest_2_city, dest_2_country = request.args['dest-2'].split(', ')

        origin_city = City.query.filter_by(name=departure_city,
                                           state=departure_country).first()
        city1 = City.query.filter_by(name=dest_1_city,
                                     country=dest_1_country).first()
        city2 = City.query.filter_by(name=dest_2_city,
                                     country=dest_2_country).first()

        city1.get_photos()
        city2.get_photos()

        max_photos = min(len(city1.photos), len(city2.photos))

        return render_template('preference_form.html',
                                origin_city=origin_city,
                                city1=city1,
                                city2=city2,
                                max_photos=max_photos,
                                session=session)
    except:
        flash("Please enter a valid choice from the dropdown menu.")
        return redirect('/search')


@app.route('/results')
def show_results():
    """Display map of city that user chose along with accompanying attractions."""

    city_id = request.args['city_id']
    city = City.query.get(city_id)

    return render_template("results.html", city=city, session=session)

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
            return redirect('/user/' + str(user.user_id))
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


@app.route('/city/<int:city_id>')
def show_city_details(city_id):
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

@app.route('/user/<int:user_id>')
def show_user_details(user_id):

    user = User.query.get(user_id)

    searches = [sorted([search.trips[0].city.name, search.trips[1].city.name]) for search in user.searches]
    unique_searches = []

    for search in searches:
        if search not in unique_searches:
            unique_searches.append(search)

    return render_template("user.html", searches=unique_searches, session=session)


@app.route('/intl-city-list')
def get_cities():
    """Get list of cities for typeahead pre-population."""

    intl_cities = db.session.query(City.name,
                                   City.country).filter(City.country != "United States").all()
    intl_cities_list = [city + ', ' + country for city, country in intl_cities]

    return jsonify({'intlCities': intl_cities_list})


@app.route('/us-city-list')
def get_us_cities():
    """Get list of cities for typeahead pre-population."""

    us_cities = db.session.query(City.name, 
                                 City.state).filter(City.country == "United States", 
                                                    City.state != "").all()
    us_cities_list = [city + ', ' + state for city, state in us_cities]

    return jsonify({'usCities': us_cities_list})


@app.route('/get-flight1', methods=['POST'])
def get_first_flight():
    """Grab cost of airfare from Google flights for first city."""

    depart_date = request.form['depart_date']
    return_date = request.form['return_date']
    origin = request.form['origin']
    destination = request.form['destination']

    #airfare = process_flights(origin, destination, depart_date, return_date)
    airfare = {'airfare': 1272}
    return jsonify(airfare)


@app.route('/get-flight2', methods=['POST'])
def get_second_flight():
    """Grab cost of airfare from Google flights for second city."""

    depart_date = request.form['depart_date']
    return_date = request.form['return_date']
    origin = request.form['origin']
    destination = request.form['destination']

    #airfare = process_flights(origin, destination, depart_date, return_date)
    airfare = {'airfare': 1753}
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
        trip = Trip(city_id=trip['cityId'],
                    search_id=search.search_id,
                    avg_temp=trip['weather'],
                    wow_factor=trip['wow'],
                    michelin_stars=trip['food'],
                    airfare=trip['airfare'])
        db.session.add(trip)
    db.session.commit()

    return 'success'

@app.route('/get-restaurants', methods=['POST'])
def get_restaurants():
    """Grab restaurants from DB if cached, otherwise call Google Places API."""

    city_id = int(request.form['city_id'])
    city_center = request.form['city_lat_lon']

    restaurants = add_places(city_id, city_center, place_type='restaurant')

    return jsonify(restaurants)


@app.route('/get-museums', methods=['POST'])
def get_museums():
    """Grab museums from DB if cached, otherwise call Google Places API."""

    city_id = int(request.form['city_id'])
    city_center = request.form['city_lat_lon']

    museums = add_places(city_id, city_center, place_type='museum')

    return jsonify(museums)


@app.route('/get-parks', methods=['POST'])
def get_parks():
    """Grab parks from DB if cached, otherwise call Google Places API."""

    city_id = int(request.form['city_id'])
    city_center = request.form['city_lat_lon']

    parks = add_places(city_id, city_center, place_type='park')

    return jsonify(parks)

@app.route('/get-similar-trips')
def get_similar_trips():
    """Query the DB for destinations searched by other users who searched
    the same 'winning' city."""

    city_id = request.args['city_id']

    if 'username' in session:
        user_id = session['username']
    else:
        user_id = 0

    user_similar_cities = get_user_similar_trips(city_id, user_id)
    num_matches = len(user_similar_cities)
    
    if num_matches == 4:
        return jsonify(user_similar_cities)
    elif num_matches > 0:
        nltk_similar_cities = get_nl_similar_trips(city_id, 4 - num_matches)
        return jsonify(user_similar_cities.update(nltk_similar_cities))
    else:
        nltk_similar_cities = get_nl_similar_trips(city_id, 4 - num_matches)
        return jsonify(nltk_similar_cities)


# helper functions


def fetch_city_data(airport_code):
    """Fetch city specific data from DB for trip comparison."""

    airport = Airport.query.filter_by(airport_code=airport_code).first()

    food = db.session.query(db.func.sum(Restaurant.stars)).filter_by(city_id=airport.city.city_id).one()

    city_stats = {'cityId': airport.city.city_id,
                  'city': airport.city.name,
                  'country': airport.city.country,
                  'costOfLiving': airport.city.col_index,
                  'food': food[0]}
    
    return city_stats


def add_places(city_id, city_center, place_type):
    """Check to see if place type for given city is already stored in DB. If so,
    return 5 establishments closest to city center.  If not, call Google
    Places API to grab 20 most prominent places, and then of those, select 5 closest
    to city center."""

    places = Place.query.filter_by(city_id=city_id, 
                                   place_type=place_type).all()

    if places:
        return select_ten_closest(places, city_center)

    else:
        places = get_places(city_id, city_center, place_type)
        return select_ten_closest(places, city_center)


def distance_from_city_center(city_center, place):
    """Calculate the distance of a place from its respective city center, given as a string
    'lat, lon'."""

    lat, lon = (float(x) for x in city_center.split(","))

    distance = abs(place.lat-lat) + abs(place.lon-lon)

    return round(distance, 3)


def select_ten_closest(places, city_center):
    """Rank places in ascending order by distance and take the
    10 with shortest distance."""

    distance = {place.name: distance_from_city_center(city_center, place) for place in places}
    closest_places = sorted(distance.items(), key=lambda x: x[1])
    closest_places_list = [place[0] for place in closest_places]

    return {place.name: place.google_place_id for place in places if place.name in closest_places_list[:10]}


if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    # DebugToolbarExtension(app)

    app.run()