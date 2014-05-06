__author__ = 'Mike'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ispp8.settings")
from django.conf import settings
import urllib3
import json
from plan.models import Activity
from datetime import datetime, timedelta
from pytz import timezone
import pytz


def get_references(keywords, latitud, longitud, radio):
    url = 'https://maps.googleapis.com/maps/api/place/search/json?keyword='
    api_key = 'AIzaSyDXn3jBP_WNPRZl--vp_ycQfqbX-WJFn0U'
    http = urllib3.PoolManager()
    response = http.request('GET', url + keywords + '&location=' + latitud + ',' + longitud + '&radius=' + radio + '&sensor=false' + '&key=' + api_key)
    jdata = json.loads(response.data.decode('utf-8'))
    results = jdata['results']
    referenceList = []
    for elem in results:
        if jdata['status'] == 'OK':
            referenceList.append(elem['reference'])
    return referenceList


def get_info(reference):
    url = 'https://maps.googleapis.com/maps/api/place/details/json?reference='
    api_key = 'AIzaSyDXn3jBP_WNPRZl--vp_ycQfqbX-WJFn0U'
    http = urllib3.PoolManager()
    response = http.request('GET', url + reference + '&sensor=false' + '&key=' + api_key)
    return json.loads(response.data.decode('utf-8'))


def get_photo(ref):
    return 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=' + ref +'&sensor=false&key=AIzaSyDXn3jBP_WNPRZl--vp_ycQfqbX-WJFn0U'


def save_info(djson, sector, isfree, moment):
    elem = djson['result']
    location = ''
    for item in elem['address_components']:
        if 'locality' in item['types']:
            location = item['short_name']
    name = elem['name']
    latitude = elem['geometry']['location']['lat']
    longitude = elem['geometry']['location']['lng']
    pref = ''
    if 'photos' in elem:
        for foto in elem['photos']:
            if 'photo_reference' in elem:
                pref = foto['photo_reference']
                break
    photo = get_photo(pref)

    madrid = timezone('Europe/Madrid')
    sd = madrid.localize(datetime(2000, 1, 1, 0, 0, 0))
    ed = madrid.localize(datetime(2999, 1, 1, 0, 0, 0))
    valoration = 0.0
    if 'rating' in elem:
        valoration = elem['rating']
    url = elem['url']
    description = 'Sorry, no description has been posted yet'
    if 'reviews' in elem:
        for rev in elem['reviews']:
            if len(rev['text']) < 200:
                description = rev['text']
                break
    Activity.objects.create(location=location, name=name, latitude=latitude, longitude=longitude, photo=photo,
                            sector=sector, moment=moment, startDate=sd, endDate=ed, valoration=valoration,
                            isFree=isfree, isPromoted=False, description=description, url=url)

citylist = [{'City': 'Madrid', 'lat': '40.4378271', 'lon': '-3.6795366'},
            {'City': 'Sevilla', 'lat': '37.397058', 'lon': '-5.984241'},
            {'City': 'Paris', 'lat': '48.8588589', 'lon': '2.3470599'},
            {'City': 'Roma', 'lat': '41.9100711', 'lon': '12.5359979'},
            {'City': 'Londres', 'lat': '51.5286416', 'lon': '-0.1015987'}]
sectorlist = ['entertainment', 'tourism', 'restaurant', 'disco', 'pub', 'theater', 'park', 'monument']
radius = '100000'

for city in citylist:
    print('Searching in ' + city['City'])
    for sector in sectorlist:
        print('Searching sector ' + sector)
        references = get_references(sector, city['lat'], city['lon'], radius)
        print('Found ' + str(len(references)) + ' references')
        for reference in references:
            print('Saving data')
            info = get_info(reference)
            save_info(info, sector, 'f', 'm')