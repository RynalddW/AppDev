# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 20:44:17 2020

@author: 100008706
"""

import requests
from urllib.request import urlretrieve
from urllib.parse import urlencode

response = requests.get("https://freegeoip.app/json/")

response_data = response.json()

lon = ('142.110216')
lat = ('-19.461907')

#print(lon, lat)

def weather_url(lon, lat, product="meteo", output="json", unit='metric'):
    from urllib.parse import urlencode
    meteo_url = 'http://www.7timer.info/bin/api.pl?'
    lon_str = str(lon)
    lat_str = str(lat)
    product_str = str(product)
    output_str = str(output)
    unit_str = str(unit)
    
    query_str = urlencode({'lon': lon_str, 'lat': lat_str, "product": product_str, "output": output_str, "unit":unit_str}, doseq=True)
    return meteo_url + query_str

#myweather = requests.get(weather_url(lon, lat))

url = weather_url(lon, lat)
#webbrowser.open(url)

weatherinfo = requests.get(url)
weatherinfo_data = weatherinfo.json()

wind = (weatherinfo_data["dataseries"])

#res = {key: wind[key] for key in wind.keys() & {"speed", "prec_amount"}} 

#res = dict((k, weatherinfo_data[k]) for k in ["speed", "prec_amount"] 
#                                        if k in weatherinfo_data) 
  

print(wind)
print(url)




#http://www.7timer.info/bin/api.pl?lon=28.047&lat=-26.204&product=meteo&output=json




