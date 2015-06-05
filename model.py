"""Create ORM for app."""

import flickr

from flask_sqlalchemy import SQLAlchemy

DEFAULT_IMAGE_URL = '/static/images/default_image.jpg'

db = SQLAlchemy()


class City(db.Model):
    """Destination city."""

    __tablename__ = "cities"

    city_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    state = db.Column(db.String(64))
    country = db.Column(db.String(64), nullable=False)
    col_index = db.Column(db.Integer)

    def __repr__(self):
        return "<City city_id=%s country=%s>" % (self.name, self.country)

    def get_photos(self):
        """Check to see if photo for city is cached in DB; if not,
        call Flickr API for new photo."""

        if self.city_images:
            self.photos = [image.image_url for image in self.city_images]
        else:
            flickr_images = flickr.get_flickr_photos(self)
            if flickr_images:
                for image_url in flickr_images:
                    image = CityImage(city_id=self.city_id,
                                      image_url=image_url)
                    db.session.add(image)
                db.session.commit()
                self.photos = flickr_images
            else:
                image_url = DEFAULT_IMAGE_URL
                self.photos = [image_url]


class CityImage(db.Model):
    """Image for potential destination city"""
    __tablename__ = "city_images"

    image_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    image_url = db.Column(db.Text, unique=True)

    city = db.relationship("City",
                           backref=db.backref("city_images", order_by=image_id))


class Airport(db.Model):
    """Destination city."""

    __tablename__ = "airports"

    airport_id = db.Column(db.Integer, primary_key=True)
    airport_code = db.Column(db.String(10), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    city = db.relationship("City",
                           backref=db.backref("airports", order_by=airport_id))

    def __repr__(self):

        return "<Airport airport_code=%s name=%s>" % (self.airport_code,
                                                      self.name)


class Restaurant(db.Model):
    """Michelin star restuarant"""

    __tablename__ = "restaurants"

    restaurant_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    stars = db.Column(db.Integer, nullable=False)

    city = db.relationship("City",
                           backref=db.backref("restaurants", order_by=restaurant_id))

    def __repr__(self):

        return "<Restaurant name=%s city_id=%s>" % (self.name, self.city_id)


class Place(db.Model):
    __tablename__ = "places"

    place_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    google_place_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    place_type = db.Column(db.String(10), nullable=False)

    city = db.relationship("City",
                           backref=db.backref("places", order_by=place_id))

    def __repr__(self):

        return "<Place name=%s city_id=%s>" % (self.name, self.city_id)


class Trip(db.Model):
    __tablename__ = "trips"

    trip_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    search_id = db.Column(db.Integer, db.ForeignKey('searches.search_id'))
    avg_temp = db.Column(db.Float)
    michelin_stars = db.Column(db.Integer)
    airfare = db.Column(db.Integer)
    wow_factor = db.Column(db.Integer)

    city = db.relationship("City",
                           backref=db.backref("trips", order_by=trip_id))

    search = db.relationship("Search",
                             backref=db.backref("trips", order_by=search_id))

    def __repr__(self):
        return "<Trip city_id=%s, airfare=%s>" % (self.city_id, self.airfare)


class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(64))
    age = db.Column(db.Integer)
    zipcode = db.Column(db.String(5))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Search(db.Model):

    __tablename__ = "searches"

    search_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    user = db.relationship("User",
                           backref=db.backref("searches", order_by=user_id))


class WikipediaPage(db.Model):

    __tablename__ = "wikipedia_pages"

    city_id = db.Column(db.Integer,
                        db.ForeignKey('cities.city_id'),
                        primary_key=True)
    content = db.Column(db.Text)


class Similarity(db.Model):

    __tablename__ = "similarities"

    combo_id = db.Column(db.String(10), primary_key=True)
    city_id_1 = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    city_id_2 = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    similarity = db.Column(db.Float)


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/pensive_passport'
    # app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."
