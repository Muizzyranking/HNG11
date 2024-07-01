#!/usr/bin/env python3
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


@app.route('/api/hello')
def hello():
    visitor_name = request.args.get('visitor_name', 'Guest')
    response = requests.get('https://api64.ipify.org?format=json').json()
    client_ip = response["ip"]

    location_data = requests.get(f'https://ipapi.co/{client_ip}/json/').json()
    city = location_data.get('city')

    api_key = '3b35d42640aec626e8d122a86e2302a0'
    weather_data = requests.get(
        f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric').json()
    temperature = weather_data['main']['temp']
    temperature = round(temperature)

    response = {
        "client_ip": client_ip,
        "location": city,
        "greeting": f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {city}",
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run()
