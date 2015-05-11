from model import City, Airport, connect_to_db, db
from server import app
from datetime import datetime
import codecs

def load_cities():
    """Load users from u.user into database."""

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
    """Load movies from u.item into database."""
    
    with codecs.open('./seed_data/airports.txt', encoding='utf-8') as source_file:
        source_file.readline()
        for line in source_file:
            print line
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
    pass

if __name__ == "__main__":
    connect_to_db(app)
    load_airports()
    load_cities()