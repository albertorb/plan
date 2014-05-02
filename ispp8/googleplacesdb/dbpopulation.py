__author__ = 'Mike'
import urllib3

http = urllib3.PoolManager()
response = http.request('GET', 'http://www.google.com')
print (response.status)