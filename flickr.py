import flickrapi, os


def get_flickr_photos(airport):
    api_key = os.environ['FLICKR_KEY']
    api_secret = os.environ['FLICKR_SECRET']
    flickr = flickrapi.FlickrAPI(api_key, api_secret, cache=True)
    
    photos = flickr.photos_search(
                                tags=airport.city.name+','+airport.city.country, 
                                lat=airport.latitude, 
                                lon=airport.longitude, 
                                radius='20',
                                sort='interestingness-desc', 
                                geo_context=2, 
                                per_page=2)[0]


    url_list = []
    for photo in photos:
        photo_sizes = flickr.photos_getSizes(photo_id=photo.attrib['id'])[0]
        for i in range(len(photo_sizes)):
            if photo_sizes[i].attrib['label'] == 'Original':
                url_list.append(photo_sizes[i].attrib['source'])

    return url_list