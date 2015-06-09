#Pensive Passport

Pensive Passport is a travel app that assists the indecisive traveler in making data-driven decisions.  Once the user has chosen travel options, PP gathers airfare, weather, cost of living, and Michelin star data.  Based on this, PP’s scoring algorithm suggests an initial destination.  The user may then adjust the relative importance of food/weather/cost, and PP’s algorithm will interactively recalculate her destination.  Once satisfied, the user can explore the “winning” city through a selection of prominent city attractions, as well as peruse PP’s additional featured recommendations.

###Technology Stack
* Backend: Python, Flask, SQLAlchemy, Postgres
  * Python Libaries: nltk, scikit-learn, scipy
* Frontend: JavaScript, jQuery, AJAX, Bootstrap
* APIs: Flickr, Google Flights, Google Maps, Google Places, World Weather Online, Wikipedia

###Control Flow
<p align="center">
  <img align="center" src="/static/images/control-flow.png">
</p>

###Overview
* Search Form
  * Search destination of interest.
  * Typeahead pre-populates from DB.
* Preference Form
  * Connect to DB for airport dropdown selection.
  * If city images are not already cached in DB, call Flickr API to gather relevant photos.
* Data Table & Algo Results
  * Data Collection
    * Call Google Flights API to gather airfare.
    * Call World Weather Online API to gather weather data for the same travel dates in the previous year.
    * Query database for static data including cost-of-living and Michelin stars.
    * Flight, weather, and static data passed through to the frontend for the scoring algorithm.
  * Destination Deciscion Algorithm
    * Calculates a weighted average for the data delta between cities:
      <img align="center" src="/static/images/data-delta.png">
    * Calculate the wow factor delta:
    <p align="center">
      <img align="center" src="/static/images/wow-delta.png">
    </p>
    * The sign (+/-) on the sum of the data delta and wow delta determines the winning city:
    <p align="center">
      <img align="center" src="/static/images/winning-city-equation.png">
    </p>
    * The user is able to adjust sliders to change the relative importance of cost, food, and weather and then the algorithm will recalculate the destination.
* Winning City Details
  * Map
    * Connect to Google Maps API for map of winning city.
  * City Attractions
    * Prominent and proximate attractions are displayed for the winning city.
    * If the destination has been searched before, places are cached in DB; if not, call Google places API for relevant attractions.
  * Featured Recommendations
    * User-based: Suggest cities that other users with similar travel preferences have searched.
    * Natural-language-based: Perform cosine similarity for winning city's Wikipedia page as compared to other cities' Wikipedia pages.
      * Generate tf-idf (term frequency, inverse document frequency) vectors (multi-dimensional) for each city's Wikipedia page.
      * For each pair of cities, determine the cosine of the angle between the two vectors.
      * A smaller angle between two vectors means a larger value of cosine and thus greater similarity between the two texts (Wikipedia pages).
      * Return cities with cosine similarity closest to 1 (0 = no similarity, 1 = perfect similarity).

###Set Up PP on Your Machine

Clone or fork this repo:

```
https://github.com/sadiew/pensive_passport.git
```

Create and activate a virtual environment inside your project directory:

```
virtualenv env

source env/bin/activate
```

Install the requirements:

```
pip install -r requirements.txt
```

Get your own secret keys for Google, Flickr, and World Weather Online and save them to a file <kbd>secrets.sh</kbd>. You should also set your own secret key for Flask. Your file should look something like this:

```
export FLICKR_KEY="YOUR_API_KEY"
export FLICKR_SECRET="YOUR_API_SECRET"
export WEATHER_KEY="YOUR_API_KEY"
export GOOGLE_KEY="YOUR_API_KEY"
```

Source your secret keys:

```
source secrets.sh
```

Run the app:

```
python server.py
```
Navigate to `localhost:5000` to decide upon your next vacation!

###Deployment

pensivepassport.com has been procured – deployment coming soon!
