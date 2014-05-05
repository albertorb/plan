__author__ = 'Mike'
import urllib3
import json


def getReferences(latitud, longitud, radio):
    url = 'https://maps.googleapis.com/maps/api/place/search/json?location='
    api_key = 'AIzaSyDXn3jBP_WNPRZl--vp_ycQfqbX-WJFn0U'
    http = urllib3.PoolManager()
    response = http.request('GET', url + latitud + ',' + longitud + '&radius=' + radio + '&sensor=false' + '&key=' + api_key)
    jdata = json.loads(response.data.decode('utf-8'))
    results = jdata['results']
    referenceList = []
    for elem in results:
        referenceList.append(elem['reference'])
    return referenceList


def getInfo(reference):
    url = 'https://maps.googleapis.com/maps/api/place/details/json?reference='
    api_key = 'AIzaSyDXn3jBP_WNPRZl--vp_ycQfqbX-WJFn0U'
    http = urllib3.PoolManager()
    response = http.request('GET', url + reference + '&sensor=false' + '&key=' + api_key)
    return json.loads(response.data.decode('utf-8'))


def saveInfo(elem):


lat = '37.787930'
lon = '-122.4074990'
radius = '100'