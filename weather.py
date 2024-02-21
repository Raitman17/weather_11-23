import json

import requests

from config import OK, TIMEOUT, WEATHER_KEYS, YANDEX_HEADER, YANDEX_URL


class ForeignApiError(Exception):
    def __init__(self, api_name: str, status_code: int) -> None:
        super().__init__(f'API {api_name} failed with status code {status_code}')


def get_weather(latitude: float, longtitude: float, yandex_key: str) -> dict:
    headers = {YANDEX_HEADER: yandex_key}
    coords = {'lat': latitude, 'lon': longtitude}
    response = requests.get(YANDEX_URL, headers=headers, params=coords, timeout=TIMEOUT)
    if response.status_code != OK:
        raise ForeignApiError('YANDEX.Weather', response.status_code)
    fact = json.loads(response.content)['fact']
    return {key: fact[key] for key in WEATHER_KEYS}
