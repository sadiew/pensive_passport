import flickrapi, os


def get_flickr_photos(city):
    api_key = os.environ['FLICKR_KEY']
    api_secret = os.environ['FLICKR_SECRET']
    flickr = flickrapi.FlickrAPI(api_key, api_secret, cache=True)
    
    print city.name+','+city.country
    photos = flickr.photos_search(
                                tags=city.name+','+city.country,
                                tag_mode=all,
                                has_geo='true',  
                                radius='20',
                                sort='relevance', 
                                geo_context=2, 
                                per_page=5)[0]

    url_list = []
    for photo in photos:
        photo_sizes = flickr.photos_getSizes(photo_id=photo.attrib['id'])[0]
        for i in range(len(photo_sizes)):
            if photo_sizes[i].attrib['label'] == 'Original':
                url_list.append(photo_sizes[i].attrib['source'])

    return url_list