import requests
import json
from config import OK, YANDEX_HEADER, YANDEX_URL, WEATHER_KEYS
import os


class ForeignApiError(Exception):
    def __init__(self, api_name: str, status_code: int) -> None:
        super().__init__(f'API {api_name} failed with status code {status_code}')

def get_weather(latitude: float, longtitude: float) -> dict:
    KEY = os.environ.get('YANDEX_KEY')
    headers = {YANDEX_HEADER: KEY}
    params = {'lat': latitude, 'lon': longtitude}
    response = requests.get(YANDEX_URL, headers=headers, params=params)
    if response.status_code != OK:
        raise ForeignApiError('YANDEX.Weather', response.status_code)
    fact = json.loads(response.content)['fact']
    return {key: fact[key] for key in WEATHER_KEYS}