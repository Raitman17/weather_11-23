import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional as Option

import dotenv
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
        city = query[city_key]
        coords = db.get_coords_by_city(self.db_cursor, city)
        if coords:
            weather_data = weather.get_weather(*coords, self.yandex_key)
            weather_data[city_key] = city
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

    def check_allowed(self) -> bool:
        return self.path.startswith('/cities')

    def check_auth(self) -> bool:
        if config.AUTH_HEADER not in self.headers.keys():
            return False
        return db.check_token(self.db_cursor, self.headers[config.AUTH_HEADER])

    def allow(self) -> bool:
        if not self.check_allowed():
            self.respond(config.NOT_ALLOWED, headers=config.ALLOW_HEADER)
            return False
        return True

    def auth(self) -> bool:
        if not self.check_auth():
            self.respond(config.FORBIDDEN)
            return False
        return True

    def allow_and_auth(self) -> bool:
        if not self.allow():
            return False
        return self.auth()

    def get_json_body(self) -> dict | None:
        content_len = self.headers.get(config.CONTENT_LEN_HEADER)
        if not (isinstance(content_len, str) and content_len.isdigit()):
            self.respond(config.BAD_REQUEST, f'should have provided {config.CONTENT_LEN_HEADER}')
            return None
        try:
            return json.loads(self.rfile.read(int(content_len)))
        except json.JSONDecodeError as error:
            self.respond(config.BAD_REQUEST, f'failed parsing json: {error}')
            return None

    def do_POST(self) -> None:
        if not self.allow_and_auth():
            return
        body = self.get_json_body()
        if body is None:
            return
        if set(body.keys()) != config.CITY_REQUIRED_KEYS:
            self.respond(config.BAD_REQUEST, f'keys {config.CITY_REQUIRED_KEYS} are required')
            return

        keys = [body[key] for key in config.CITY_KEYS]
        try:
            response = db.add_city(self.db_cursor, self.db_connection, *keys)
        except psycopg.errors.UniqueViolation:
            self.respond(config.OK, f'record city={body["name"]} already exists')
            self.db_connection.rollback()
            return

        if response:
            self.respond(config.CREATED, f'record with city {body["name"]} was created')
        else:
            self.respond(config.SERVER_ERROR, f'failed to create record city={body["name"]}')

    def do_DELETE(self) -> None:
        if not self.allow_and_auth():
            return
        query = self.get_query()
        city_key = 'name'
        if city_key not in query.keys():
            self.respond(config.BAD_REQUEST, 'you should have provided city in query')
            return
        if query[city_key] not in db.get_cities_names(self.db_cursor):
            self.respond(config.ACCEPTED, f'city {query[city_key]} is not present in database')
            return
        if db.delete_city(self.db_cursor, self.db_connection, query[city_key]):
            self.respond(config.NO_CONTENT)
        else:
            self.respond(config.SERVER_ERROR, f'city {query[city_key]} was not deleted')

    def do_PUT(self) -> None:
        if not self.allow_and_auth():
            return
        query = self.get_query()
        city_key = 'name'
        if city_key not in query.keys() or db.check_city(self.db_cursor, query[city_key]):
            self.do_POST()
            return
        city = query[city_key]
        body = self.get_json_body()
        for attr in body.keys():
            if attr not in config.CITY_REQUIRED_KEYS:
                self.respond(config.BAD_REQUEST, f'key {attr} is not defined for instance')
                return
        if db.update_city(self.db_cursor, self.db_connection, body, city):
            self.respond(config.OK, f'city {city} was updated')
        else:
            self.respond(config.SERVER_ERROR, f'city {city} was not updated')


if __name__ == '__main__':
    server = HTTPServer((config.HOST, config.PORT), connect_my_handler(MyRequestHandler))
    print(f'Server started at http://{config.HOST}:{config.PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Interrupted by user!')
    finally:
        server.server_close()
