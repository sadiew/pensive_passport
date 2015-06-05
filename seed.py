"""Seeds the database with city, airport, and restaurant data."""

from model import City, Airport, Restaurant, connect_to_db, db
from server import app
import codecs


def load_cities():
    """Load cities into database."""

    with codecs.open('./seed_data/cities.txt', encoding='utf-8') as source_file:
        source_file.readline()
        for line in source_file:
            city_data = line.rstrip().split('\t')
            city = City(city_id=city_data[0],
                        name=city_data[1],
                        state=city_data[2],
                        country=city_data[3],
                        col_index=city_data[4])
            db.session.add(city)
        db.session.commit()


def load_airports():
    """Load airports into database."""

    with codecs.open('./seed_data/airports.txt', encoding='utf-8') as source_file:
        source_file.readline()
        for line in source_file:
            airport_data = line.rstrip().split('\t')

            airport = Airport(airport_id=airport_data[0],
                            airport_code=airport_data[1],
                            name=airport_data[2],
                            city_id=airport_data[3],
                            latitude=airport_data[4],
                            longitude=airport_data[5])
            db.session.add(airport)
        db.session.commit()


def load_restaurants():
    """Load restaurants into database."""

    with codecs.open('./seed_data/restaurants.txt', encoding='utf-8') as source_file:
        source_file.readline()
        for line in source_file:
            restaurant_data = line.rstrip().split('\t')

            restaurant = Restaurant(restaurant_id=restaurant_data[0],
                                    name=restaurant_data[1],
                                    city_id=restaurant_data[2],
                                    stars=restaurant_data[3])
            db.session.add(restaurant)
        db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    load_cities()
    load_airports()
    load_restaurants()
