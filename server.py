import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional as Option

import dotenv
import json
import psycopg

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
        if body:
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

    def do_HEAD(self) -> None:
        self.respond(config.OK)

    def check_if_allowed(self) -> None:
        if not self.path.startswith('/cities'):
            self.respond(config.NOT_ALLOWED, headers=config.ALLOW_HEADER)
            return False
        return True

    def do_POST(self) -> None:
        if not self.check_if_allowed():
            return
        content_len = self.headers.get(config.CONTENT_LEN_HEADER)
        if not (isinstance(content_len, str) and content_len.isdigit()):
            self.respond(config.BAD_REQUEST, f'you should have provided {config.CONTENT_LEN_HEADER}')
            return
        body = json.loads(self.rfile.read(int(content_len)))
        if set(body.keys()) != config.CITY_REQUIRED_KEYS:
            self.respond(config.BAD_REQUEST, f'keys {config.CITY_REQUIRED_KEYS} are required')
            return

        try:
            response = db.add_city(self.db_cursor, self.db_connection, body['name'], body['lat'], body['lon'])
        except psycopg.errors.UniqueViolation:
            self.respond(config.BAD_REQUEST, f'record city={body["name"]} already exists')
            self.db_connection.rollback()
            return

        if response:
            self.respond(config.CREATED, f'record with city {body["name"]} was created')
        else:
            self.respond(config.SERVER_ERROR, f'failed to create record city={body["name"]}')


    def do_DELETE(self) -> None:
        if not self.check_if_allowed():
            return
        query = self.get_query()
        city_key = 'city'
        if city_key not in query.keys():
            self.respond(config.BAD_REQUEST, 'you should have provided city in query')
            return
        if query[city_key] not in [city for city, _, _ in db.get_cities(self.db_cursor)]:
            self.respond(config.BAD_REQUEST, f'city {query[city_key]} is not present in database')
            return
        if db.delete_city(self.db_cursor, self.db_connection, query[city_key]):
            self.respond(config.NO_CONTENT)
        else:
            self.respond(config.SERVER_ERROR, f'city {query[city_key]} was not deleted')
        

if __name__ == '__main__':
    server = HTTPServer((config.HOST, config.PORT), connect_my_handler(MyRequestHandler))
    print(f'Server started at http://{config.HOST}:{config.PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Interrupted by user!')
    finally:
        server.server_close()
