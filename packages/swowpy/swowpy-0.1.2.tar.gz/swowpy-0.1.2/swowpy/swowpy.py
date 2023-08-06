#Small wrapper for openweathermap
import requests
import json

class Swowpy:

    def __init__(self,api_key,city):

        self.key = api_key
        self.city = city

    def _create_url(self,city,measure):
        if measure == "weather":
            URL = "http://api.openweathermap.org/data/2.5/weather?q="
            URL += city
            URL += "&appid=" + self.key
            return URL

    def weather(self):
        URL = self._create_url(self.city,"weather")
        response = requests.get(url = URL)
        return response.json()

    def temperature(self,**kwargs):
        URL = self._create_url(self.city,"weather")
        response = requests.get(url = URL)
        if kwargs['unit'] == "Celsius":
            print("Celsius")
            return float(response.json()['main']['temp'])-273.15

        else: 
            return response.json()['main']['temp']    

        
