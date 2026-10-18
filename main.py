import os
import json

import folium
import requests

from geopy import distance
from dotenv import load_dotenv
from flask import Flask


def get_stations():
    with open('charging_stations_by.json', 'r', encoding="UTF8") as file:
        stations = json.load(file)
    return stations


def get_coordinates(apikey, address):
    url = "https://geocode-maps.yandex.ru/1.x"
    params = {
        "geocode": address,
        "apikey": apikey,
        "format": "json"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    geo_objects = response.json()['response']['GeoObjectCollection']['featureMember']
    if not geo_objects:
        return None
    location = geo_objects[0]['GeoObject']['Point']['pos']
    longitude, latitude = location.split(" ")
    return latitude, longitude


def open_map():
    with open('index.html',encoding="UTF-8") as file:
        return file.read()


def main():
    load_dotenv()
    apikey = os.getenv("APIKEY")
    user_place = input("Где вы находитесь: ")
    coordinates = get_coordinates(apikey,user_place)
    stations = get_stations()
    all_info_station = []
    for station in stations:
        station_name = station["name"]
        latitude = station["latitude"]
        longitude = station["longitude"]
        station_coord = latitude,longitude
        dist = distance.distance(coordinates, station_coord).km
        info_station = {
            "title": station_name,
            "distance": dist,
            "latitude": latitude,
            "longitude": longitude  
        }
        all_info_station.append(info_station)
    sorted_stations = sorted(all_info_station, key=lambda x: x['distance'])[:15]
    map = folium.Map(location=coordinates,zoom_start=12)
    for sorted_station in sorted_stations:
        folium.Marker(
            location=[sorted_station["latitude"],sorted_station["longitude"]],
            tooltip="Click me!",
            popup=sorted_station["title"],
            icon=folium.Icon(icon="cloud"),
        ).add_to(map)
    map.save("index.html")
    app = Flask(__name__)
    app.add_url_rule('/', 'station_map', open_map)
    app.run('0.0.0.0')


if __name__ == '__main__':
    main()