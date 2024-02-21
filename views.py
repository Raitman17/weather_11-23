from typing import Optional

import config


def load_page(template_path: str, page_data: Optional[dict] = None) -> str:
    with open(template_path, 'r') as template:
        body = template.read()
    return body.format(**page_data) if page_data else body


def cities_page(cities: list) -> str:
    return load_page(config.TEMPLATE_CITIES, {'cities': cities_html(cities)})


def cities_html(cities: list[tuple]) -> str:
    href = '<a href="/weather?city='
    row_template = '<li>{0}{1}">{2}</a>lat: {3}, lon: {4}</li>'
    rows = []
    for city, lat, lon in cities:
        rows.append(row_template.format(href, spaces_to_plusses(city), city, lat, lon))
    return '\n'.join(rows)


def main_page() -> str:
    return load_page(config.TEMPLATE_MAIN)


def weather_page(weather_data: dict) -> str:
    return load_page(config.TEMPLATE_WEATHER, weather_data)


def weather_dummy_page(cities: list[str]) -> str:
    return load_page(config.TEMPLATE_WEATHER_DUMMY, {'options': make_form_options(cities)})


def make_form_options(options_values: list[str]) -> str:
    return '\n'.join([f'<option value="{option}">{option}</option>' for option in options_values])


def spaces_to_plusses(text: str) -> str:
    return text.replace(' ', '+')


def plusses_to_spaces(text: str) -> str:
    return text.replace('+', ' ')
