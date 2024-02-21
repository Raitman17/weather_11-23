import config
from typing import Optional

def load_page(template_path: str, params: Optional[dict] = None) -> str:
    with open(template_path, 'r') as file:
        content = file.read()
    return content.format(**params) if params else content
    

def cities_page(cities: list) -> str:
    return load_page(config.TEMPLATE_CITIES, {'cities': cities_html(cities)})


def cities_html(cities: list[tuple]) -> str:
    return '\n'.join([f'<li>{city} lat: {lat}, lon: {lon} </li>' for city, lat, lon in cities])


def main_page() -> str:
    return load_page(config.TEMPLATE_MAIN)


def weather_page(weather_data: dict) -> str:
    return load_page(config.TEMPLATE_WEATHER, weather_data)
