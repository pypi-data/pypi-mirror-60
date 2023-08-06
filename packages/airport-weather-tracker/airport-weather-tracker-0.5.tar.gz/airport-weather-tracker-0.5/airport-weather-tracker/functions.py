import get_data
import requests
import base64

import requests as req
from io import BytesIO


def graph2base64(type, x, y, z):
    graph = ["precipitation_new", "pressure_new", "wind_new", "temp_new"]
    if str(type) not in graph:
        return ""
    if not isinstance(x, int) or not isinstance(y, int) or not isinstance(z, int):
        return "input type problem"
    api_key = "eb99a94c01902a58db4fe797d1737336"
    url = "https://tile.openweathermap.org/map/" + str(type) + "/" + str(z) + "/" + str(y) +"/" +str(x)\
            + ".png?appid=" + api_key
    code = base64.b64encode(BytesIO(req.get(url).content).read())
    b64code = str(code)[2:]
    return b64code

def graphErrorHandle(result):
    if result == "": return "check the type"
    elif result == "input type problem": return "check input x, y, z range and type"
    return result

def download():
    get_data.mainfunction() ## download airport csv file in this path ./data

def csv2list():
    file = "./data/airport-codes.csv"
    us_airports = [['ident', 'name', 'coordinates:x', 'coordinates:y']]
    with open(file) as f:
        for line in f:
            data_line = line.split(',')
            if data_line[5] == 'US':
                cur_airport = [data_line[0], data_line[2], data_line[11], data_line[12]]
                us_airports.append(cur_airport)
    for airport in us_airports:
        airport[2] = airport[2][1:]
        airport[3] = airport[3][:-2]
    return us_airports

def call_by_identifier(id):
    response = ""
    url = "http://api.openweathermap.org/data/2.5/weather?"
    wrong_api = "0d4106e1f9b90af07d06b432e89b255"
    api_key = "0d4106e1f9b90af07d06b432e89b2556"
    us_airports = csv2list()
    for airport in us_airports:
        if id == airport[0]:
            lat = round(float(airport[2]), 3)
            lon = round(float(airport[3]), 3)
            response = requests.get(url + "lat=" + str(lat) + "&lon=" + str(lon) + "&APPID=" + api_key)
            return response
    return ""

def call_by_geo_coor(lat, lon):
    if(lon > 180 or lon < - 180 or lat > 180 or lat < -180):
        return ""
    response = ""
    url = "http://api.openweathermap.org/data/2.5/weather?"
    api_key = "eb99a94c01902a58db4fe797d1737336"
    wrong_api = "0d4106e1f9b90af07d06b432e89b255"
    lat = round(float(lat), 3)
    lon = round(float(lon), 3)

    response = requests.get(url + "lat=" + str(lat) + "&lon=" + str(lon) + "&APPID=" + api_key)
    return response


def error_handle(response):
    if response == "":
        return "something of your input is wrong"
    else:
        return response.json()

