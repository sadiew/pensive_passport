from flask_sqlalchemy import SQLAlchemy
#import flickrapi, os

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
        return "<City city_id=%s country=%s>" % (self.name, self.country)


class CityImage(db.Model):
    """Image for potential destination city"""
    __tablename__ = "city_images"

    image_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    image_url = db.Column(db.Text)

    city = db.relationship("City",
                           backref=db.backref("city_images", order_by=image_id))


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

class Restaurant(db.Model):
    """Michelin star restuarant"""

    __tablename__ = "restaurants"

    restaurant_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    stars = db.Column(db.Integer, nullable=False)

    city = db.relationship("City",
                           backref=db.backref("restaurants", order_by=restaurant_id))

    def __repr__(self):

        return "<Restaurant name=%s city_id=%s>" % (self.name, self.city_id)

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