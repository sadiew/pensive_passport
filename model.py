from flask_sqlalchemy import SQLAlchemy
import flickrapi, os

db = SQLAlchemy()

# Model definitions

class City(db.Model):
    """Destination city."""

    __tablename__ = "cities"

    city_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64))
    country = db.Column(db.String(64), nullable=False)
    col_index = db.Column(db.Integer)

    def __repr__(self):

        return "<City city_id=%s email=%s>" % (self.city_name, self.country_name)

    def get_flickr_photos(self):
        pass

    def get_weather_data(self):
        pass


class Airport(db.Model):
    """Destination city."""

    __tablename__ = "airports"

    airport_id = db.Column(db.Integer, primary_key=True)
    airport_code = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    city = db.relationship("City",
                           backref=db.backref("airports", order_by=airport_id))
    

    def __repr__(self):

        return "<Airport airport_code=%s name=%s>" % (self.airport_code, self.name)

    def get_flickr_photos(self):
        api_key = os.environ['FLICKR_KEY']
        api_secret = os.environ['FLICKR_SECRET']
        flickr = flickrapi.FlickrAPI(api_key, api_secret, cache=True)
        
        photos = flickr.photos_search(
                                    tags=self.city.name.lower(), 
                                    lat=self.latitude, 
                                    lon=self.longitude, 
                                    radius='20',
                                    sort='interestingness-desc', 
                                    geo_context=2, 
                                    per_page=3)[0]

        url_list = []
        for photo in photos:
            photo_sizes = flickr.photos_getSizes(photo_id=photo.attrib['id'])[0]
            for i in range(len(photo_sizes)):
                if photo_sizes[i].attrib['label'] == 'Original':
                    url_list.append(photo_sizes[i].attrib['source'])
        return url_list

# Helper functions
def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sw_project.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."