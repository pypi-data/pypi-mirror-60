import requests
from datetime import date, datetime
import random
import logging

class ApodPy:
    date = date.today()
    explanation = ""
    hdurl = ""
    media_type: ""
    service_version: ""
    title: ""
    url = ""

    def __init__(self, api_key):
        self.api_key = api_key
    
    def make_request(self, hd, date=date.today()):
        url = 'https://api.nasa.gov/planetary/apod?api_key=' + self.api_key
        try:
            response = requests.get(url = url, params={'date': date, 'hd': hd, 'api_key': self.api_key},)
            return self.parse_codes(response)
        except Exception as e:
            logging.error(e)
            return
    
    def to_json(self, response):
        response = response.json()
        self.date = response['date']
        self.explanation = response['explanation']
        self.hdurl = response['hdurl']
        self.media_type = response['media_type']
        self.title = response['title']
        self.url = response['url']
        return response
    
    def parse_codes(self, response):
        if response.status_code == 200:
            return self.to_json(response)
        else:
            logging.error("An error occurred. Error code: {}".format(response.status_code))
            return 





