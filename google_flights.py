import json, requests, os

def get_flights(origin, destination, depart_date, return_date):
    api_key = os.environ['QPX_KEY']
    url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + api_key
    headers = {'content-type': 'application/json'}

    #round trip api call
    params = {
      "request": {
        "slice": [
          {
            "origin": origin,
            "destination": destination,
            "date": depart_date,
            "maxStops":2
          },
          {
            "origin": destination,
            "destination": origin,
            "date": return_date,
            "maxStops":2
          }
        ],
        "passengers": {
          "adultCount": 1
        },
        "solutions": 2,
        "refundable": False
      }
    }

    response = requests.post(url, data=json.dumps(params), headers=headers)
    data = response.json()

    first_option = data['trips']['tripOption'][0]

    raw_fare = first_option['saleTotal'][3:]
    total_fare = float(raw_fare)

    to_minutes = first_option['slice'][0]['duration']
    to_hours = round(float(to_minutes)/60,2)
    to_segments = first_option['slice'][0]['segment']
    to_stops = len(to_segments) - 1

    from_minutes = first_option['slice'][1]['duration']
    from_hours = round(float(from_minutes)/60,2)
    from_segments = first_option['slice'][1]['segment']
    from_stops = len(from_segments) - 1

    return {'total_fare': total_fare, 
            'to_data': (to_stops, to_hours), 
            'from_data': (from_stops, from_hours)}

def get_url(origin, destination, depart_date, return_date):
    api_key = os.environ['QPX_KEY']
    url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + api_key

    #round trip api call
    params = {
      "request": {
        "slice": [
          {
            "origin": origin,
            "destination": destination,
            "date": depart_date,
            "maxStops":2
          },
          {
            "origin": destination,
            "destination": origin,
            "date": return_date,
            "maxStops":2
          }
        ],
        "passengers": {
          "adultCount": 1
        },
        "solutions": 2,
        "refundable": False
      }
    }

    return [url, params]
    
def process_response(response):
    data = json.loads(response)

    first_option = data['trips']['tripOption'][0]

    raw_fare = first_option['saleTotal'][3:]
    total_fare = float(raw_fare)

    to_minutes = first_option['slice'][0]['duration']
    to_hours = round(float(to_minutes)/60,2)
    to_segments = first_option['slice'][0]['segment']
    to_stops = len(to_segments) - 1

    from_minutes = first_option['slice'][1]['duration']
    from_hours = round(float(from_minutes)/60,2)
    from_segments = first_option['slice'][1]['segment']
    from_stops = len(from_segments) - 1

    return {'total_fare': total_fare, 
            'to_data': (to_stops, to_hours), 
            'from_data': (from_stops, from_hours)}