from model import City, Airport, Restaurant, Place, Trip, User, connect_to_db, db
from flask import Flask, request, render_template, redirect, jsonify, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from datetime import datetime, timedelta
from google_places import get_places
from google_flights import get_flights
from weather import get_weather
import json, psycopg2


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
    try:
        departure_city = request.args.get('departure-city').split(', ')
        destination_1 = request.args.get('destination-1').split(', ')
        destination_2 = request.args.get('destination-2').split(', ')

        origin_city = City.query.filter_by(name=departure_city[0], state=departure_city[1]).first()
        city1 = City.query.filter_by(name=destination_1[0], country=destination_1[1]).first()
        city2 = City.query.filter_by(name=destination_2[0], country=destination_2[1]).first()

        city1.get_photos()
        city2.get_photos()

        max_photos = min(len(city1.photos), len(city2.photos))

        return render_template('preference_form.html',
                                origin_city=origin_city, 
                                city1=city1, 
                                city2=city2,
                                max_photos=max_photos)
    except:
        flash("Please enter a valid choice from the dropdown menu.")
        return redirect('/')

    
@app.route('/results')
def show_results():
    """Display map of city that user chose along with accompanying attractions."""
    city, country, city_id = request.args['city'], request.args['country'], request.args['city_id']
    
    return render_template("results.html",
                            city=city,
                            country=country,
                            city_id=city_id)


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
    city_id = int(request.form.get('city_id'))
    city_center = tuple(request.form.get('city_lat_lon').split(","))

    restaurants = add_places(city_id, city_center, place_type ='restaurant')
    
    return jsonify(restaurants)


@app.route('/get-museums', methods=['POST'])
def get_museums():
    city = request.form.get('city')
    country = request.form.get('country')
    city_id = int(request.form.get('city_id'))
    city_center = tuple(request.form.get('city_lat_lon').split(","))

    museums = add_places(city_id, city_center, place_type ='museum')
    
    return jsonify(museums)


@app.route('/get-parks', methods=['POST'])
def get_parks():
    city = request.form.get('city')
    country = request.form.get('country')
    city_id = int(request.form.get('city_id'))
    city_center = tuple(request.form.get('city_lat_lon').split(","))

    parks = add_places(city_id, city_center, place_type ='park')
    
    return jsonify(parks)


@app.route('/get-flight1', methods=['POST'])
def get_first_flight():
    depart_date = request.form['depart_date']
    return_date = request.form['return_date']
    origin = request.form['origin']
    destination = request.form['destination']

    #airfare = process_flights(origin, destination, depart_date, return_date)
    airfare = {'airfare': 1000}
    return jsonify(airfare)


@app.route('/get-flight2', methods=['POST'])
def get_second_flight():
    depart_date = request.form['depart_date']
    return_date = request.form['return_date']
    origin = request.form['origin']
    destination = request.form['destination']

    #airfare = process_flights(origin, destination, depart_date, return_date)
    airfare = {'airfare': 1000}
    return jsonify(airfare)


@app.route('/get-weather1', methods=['POST'])
def get_first_weather():
    depart_date = request.form['depart_date']
    destination = request.form['destination']

    weather = process_weather(depart_date, destination)
    return jsonify(weather)


@app.route('/get-weather2', methods=['POST'])
def get_second_weather():
    depart_date = request.form['depart_date']
    destination = request.form['destination']

    weather = process_weather(depart_date, destination)
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


@app.route('/store-trips', methods=['POST'])
def store_trips():
    trip1 = json.loads(request.form['trip1'])
    trip2 = json.loads(request.form['trip2'])
    trips = [trip1, trip2]

    for trip in trips:
        trip = Trip(city_id=trip['city_id'],
                avg_temp=trip['weather'], 
                wow_factor=trip['wow'],
                michelin_stars=trip['food'],
                airfare=trip['airfare'],
                user_id=session['username'])
        db.session.add(trip)
        session.setdefault('cities_searched', []).append(trip.city_id)
    db.session.commit()

    return 'success'

@app.route('/login')
def login():
    """Login form"""

    return render_template('login_form.html')


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
            return redirect('/')
        else:
            flash("Invalid login.")
            return render_template('login_form.html')


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
        return redirect('/')
    else:
        flash("Passwords do not match, try again.")
        return render_template('register.html')


@app.route('/get-similar-trips')
def get_similar_trips():
    
    city_id = request.args['city_id']
    query = """SELECT DISTINCT trips.city_id, cities.name, cities.country, COUNT(trips.city_id)
            FROM trips
            JOIN cities on trips.city_id = cities.city_id
            WHERE trips.city_id <> %s and user_id IN 
            (SELECT DISTINCT user_id 
            FROM trips
            WHERE city_id =%s)
            GROUP BY 1,2,3
            ORDER BY COUNT(trips.city_id) DESC""" %(city_id, city_id)
    
    
    results = call_sql(query)
    top_five = results[:4]

    similar_cities = {city[0]:'%s, %s' %(city[1], city[2]) for city in top_five}

    return jsonify(similar_cities)

@app.route('/cities/<int:city_id>')
def show_city(city_id):
    city = City.query.get(city_id)
    
    food = db.session.query(db.func.count(Restaurant.restaurant_id), 
                            db.func.sum(Restaurant.stars)).filter_by(city_id=city.city_id).one()

    avg_wow = db.session.query(db.func.avg(Trip.wow_factor)).filter_by(city_id=city.city_id).one()
    avg_airfare = db.session.query(db.func.avg(Trip.airfare)).filter_by(city_id=city.city_id).one()

    city.food = [food[0], food[1]]
    city.avg_wow = round(avg_wow[0],1)
    city.avg_airfare = int(avg_airfare[0])

    return render_template('city.html', city=city)
    

#helper functions
def process_flights(origin, destination, depart_date, return_date):
    try:
        airfare = get_flights(origin, destination, depart_date, return_date)
    except:
        flash("Flight info unavailable. Default values assigned.")
        airfare = {'airfare': 1000}

    return airfare

def process_weather(depart_date, destination):
    date_last_year = datetime.strftime(datetime.strptime(depart_date, '%Y-%m-%d') - 
                        timedelta(days=365), '%Y-%m-%d')
    airport = Airport.query.filter_by(airport_code=destination).first()
    latitude = airport.latitude
    longitude = airport.longitude
    try:
        weather = get_weather(date_last_year, latitude, longitude)
    except:
        flash("Weather info unavailable. Default values assinged.")
        weather = {'high': 80, 'low': 50}
    return weather


def fetch_city_data(airport_code):
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
    try:
        conn = psycopg2.connect("dbname='pensive_passport' host='localhost' port=5432")
        cur = conn.cursor()
        cur.execute(query)
        return cur.fetchall()
    except Exception,e:
        print "\nCan't connect to the database!"
        print e
        print '\n'

def add_places(city_id, city_center, place_type):
    places = Place.query.filter_by(city_id=city_id, place_type=place_type).all()

    if places:
        five_closest_places = select_five_closest_prominent(places, city_center)

    else:
        city_object = City.query.get(city_id)
        city = city_object.name
        country = city_object.country
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
        five_closest_places = select_five_closest_prominent(places, city_center)
    
    return five_closest_places

def distance_from_city_center(city_center, place):
    city_lat = float(city_center[0])
    city_lon = float(city_center[1])

    distance_from_center = abs(place.lat-city_lat) + abs(place.lon-city_lon)

    return round(distance_from_center, 3)

def select_five_closest_prominent(places, city_center):
    distance_from_center = {place.name:distance_from_city_center(city_center, place) for place in places}
    closest_places = sorted(distance_from_center.items(), key=lambda x:x[1])
    closest_places_list = [place[0] for place in closest_places]

    five_closest_places = {place.name:place.google_place_id for place in places if place.name in closest_places_list[:5]}
    return five_closest_places



if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run()