import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional as Option

import dotenv

import config
import db
import views
import weather


def connect_my_handler(class_: type) -> type:
    dotenv.load_dotenv()
    connection, cursor = db.connect()
    attributes = {
        'yandex_key': os.environ.get('YANDEX_KEY'),
        'db_connection': connection,
        'db_cursor': cursor,
    }
    for name, attr in attributes.items():
        setattr(class_, name, attr)
    return class_


class MyRequestHandler(BaseHTTPRequestHandler):
    def get_query(self) -> dict:
        query = {}
        qm_index = self.path.find('?')
        if qm_index == -1 or qm_index == len(self.path) - 1:
            return query
        for pair in self.path[qm_index+1:].split('&'):
            key, attr = pair.split('=')
            if attr.isdigit():
                query[key] = int(attr)
                continue
            try:
                float(attr)
            except ValueError:
                query[key] = views.plusses_to_spaces(attr)
            else:
                query[key] = float(attr)
        return query

    def respond(self, code: int, body: Option[str] = None, headers: Option[dict] = None) -> None:
        self.send_response(code)
        self.send_header(*config.CONTENT_HEADER)
        if headers:
            for header_key, header_value in headers.items():
                self.send_header(header_key, header_value)
        self.end_headers()
        self.wfile.write(body.encode())

    def cities_page(self) -> None:
        cities = db.get_cities(self.db_cursor)
        self.respond(config.OK, views.cities_page(cities))

    def main_page(self) -> None:
        self.respond(config.OK, views.main_page())

    def weather_page(self) -> None:
        city_key = 'city'
        query = self.get_query()
        if city_key not in query.keys():
            cities = [city for city, _, _ in db.get_cities(self.db_cursor)]
            self.respond(config.OK, views.weather_dummy_page(cities))
            return
        coords = db.get_coords_by_city(self.db_cursor, query[city_key])
        if coords:
            weather_data = weather.get_weather(*coords, self.yandex_key)
            weather_data[city_key] = query[city_key]
            self.respond(config.OK, views.weather_page(weather_data))
        else:
            self.respond(config.BAD_REQUEST, '')  # TODO

    def do_GET(self) -> None:
        if self.path.startswith('/weather'):
            self.weather_page()
        elif self.path.startswith('/cities'):
            self.cities_page()
        else:
            self.main_page()


if __name__ == '__main__':
    server = HTTPServer((config.HOST, config.PORT), connect_my_handler(MyRequestHandler))
    print(f'Server started at http://{config.HOST}:{config.PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Interrupted by user!')
    finally:
        server.server_close()
