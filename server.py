from model import City, Airport, connect_to_db, db
from flask import Flask, request, render_template, redirect, jsonify, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

#import flickr

app = Flask(__name__)

app.secret_key = "ABC"
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Show index page."""
    return render_template("index.html")

@app.route('/destinaton_form')
def show_destination_form():
	"""Display initial destination form."""
	return render_template("destination_form.html")


@app.route('/comparison-form')
def gather_info():
    """Return results from homepage."""

    departure_city = request.args.get('departure-city')
    destination_1 = request.args.get('destination-1')
    destination_2 = request.args.get('destination-2')

    city1 = City.query.filter_by(name=destination_1).first()
    city2 = City.query.filter_by(name=destination_2).first()

    flickr_images_1= city1.airports[0].get_flickr_photos()
    flickr_images_2= city2.airports[0].get_flickr_photos()

    if flickr_images_1:
    	flickr_image_1 = flickr_images_1[0]
    else:
    	flickr_image_1 = 'http://gigabiting.com/wp-content/uploads/2010/08/WorldTravelerSign.jpg'

    if flickr_images_2:
    	flickr_image_2 = flickr_images_2[0]
    else:
    	flickr_image_2 = 'http://gigabiting.com/wp-content/uploads/2010/08/WorldTravelerSign.jpg'

    return render_template('comparison-form.html', 
    						city1=city1, 
    						city2=city2,
    						flickr_image_1=flickr_image_1,
    						flickr_image_2=flickr_image_2)

@app.route('/results', methods=['POST'])
def show_results():
	# depart_date = request.args.form('depart-date')
 #    return_date = request.args.form('return-date')
	# food_weighting = request.args.form['food_weight']
	# cost_of_living_weighting = request.args.form['col_weight']
	# weather_weighting = request.args.form['weather_weighting']
	# wow_factor_1 = request.args.form['wow_factor_1']
	# wow_factor_2 = request.args.form['wow_factor_2']

	#run algorithm, which runs each of the api calls as well.
	#final_destination = determine_destination()

	return "results page"


if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run()