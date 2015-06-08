#Pensive Passport

Pensive Passport is a travel app that assists the indecisive traveler in making data-driven decisions.  Once the user has chosen travel options and dates, PP gathers airfare, weather , cost of living, and Michelin star data.  Based on this, PP’s scoring algorithm suggests an initial destination.  The user may then adjust the relative importance of food/weather/cost, and PP’s algorithm will interactively recalculate her destination.  Once satisfied, the user can explore the “winning” city through a selection of prominent city attractions, as well as peruse PP’s additional featured recommendations (user and natural-language based).

####Technology Stack
* Backend
  * Python/Flask
  * Postgres, SQLAlchemy
  * Python Libaries: nltk, scikit-learn, scipy
* Frontend
..* Javascript, jQuery, AJAX
..* Bootstrap
* API's
..* Flickr
..* Google Flights
..* Google Maps
..* Google Places
..* World Weather Online
..* Wikipedia

####Control Flow
<p align="center">
  <img align="center" src="/static/images/control-flow.png">
</p>

####Overview
* Search Form
..* Search destination of interest.
..* Typeahead pre-populates from DB.

* Preference Form
..* Connect to DB for airport dropdown selection.
..* If city images are not already cached in DB, call Flickr API to gather relevant photos.

* Data Table & Algo Results
..* Data Collection
..*..* Call Google Flights API to gather airfare.
....* Call World Weather Online API to gather weather data for the same travel dates in the previous year.
....* Query database for static data including cost-of-living and Michelin stars.
....* Flight, weather, and static data passed through to the frontend for the scoring algorithm.
..* Algorithm: determine destination
....* Calculates a weighted average for the data delta between cities:
<p align="center">
  <img align="center" src="/static/images/data-delta.png">
</p>
....* Calculate the wow factor delta:
<p align="center">
  <img align="center" src="/static/images/wow-delta.png">
</p>
....* The sign (+/-) on the sum of the data delta and wow delta determines the winning city:
<p align="center">
  <img align="center" src="/static/images/winning-city-equation.png">
</p>
....* The user is able to adjust sliders to change the relative importance of cost, food, and weather and then the algorithm will recalculate the destination.

* Winning City Details
..* Map
....* Connect to Google Maps API for map of winning city.
..* City Attractions
....* Prominent and proximate attractions are displayed for the winning city.
....* If the destination has been searched before, places are cached in DB; if not, call Google places API for relevant attractions.
..* Featured Recommendations
....* User-based: Suggest cities that other users with similar travel preferences have searched.
....* Natural-language-based: Perform cosine similarity for winning city's Wikipedia page as compared to other Wikipedia pages stored in DB.  Return cities with cosine similarity closest to 1 (0 = no similarity, 1 = perfect similarity).
