import config
from typing import Optional

def load_page(template_path: str, params: Optional[dict] = None) -> str:
    with open(template_path, 'r') as file:
        content = file.read()
    return content.format(**params) if params else content
    

def cities_page(cities: list) -> str:
    return load_page(config.TEMPLATE_CITIES, {'cities': cities_html(cities)})


def cities_html(cities: list[tuple]) -> str:
    href = '<a href="/weather?city='
    return '\n'.join([f'<li>{href}{spaces_to_plusses(city)}">{city}</a> lat: {lat}, lon: {lon} </li>' for city, lat, lon in cities])


def main_page() -> str:
    return load_page(config.TEMPLATE_MAIN)


def weather_page(weather_data: dict) -> str:
    return load_page(config.TEMPLATE_WEATHER, weather_data)


def weather_dummy_page(cities: list[str]) -> str:
    return load_page(config.TEMPLATE_WEATHER_DUMMY, {'options': make_form_options(cities)})


def make_form_options(values: list[str]) -> str:
    return '\n'.join([f'<option value="{value}">{value}</option>' for value in values])


def spaces_to_plusses(text: str) -> str:
    return text.replace(' ', '+')


def plusses_to_spaces(text: str) -> str:
    return text.replace('+', ' ')
