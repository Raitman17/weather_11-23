from http.server import HTTPServer, BaseHTTPRequestHandler

import config
import db
import dotenv
import os
from typing import Optional
import views
import weather

# мы сделаем декоратор класса который подключит нас к базе и загрузит ключ яндекса!
def connect_my_handler(class_: type) -> type:
    dotenv.load_dotenv()
    connection, cursor = db.connect()
    setattr(class_, 'yandex_key', os.environ.get('YANDEX_KEY'))
    setattr(class_, 'db_connection', connection)
    setattr(class_, 'db_cursor', cursor)
    return class_

class MyRequestHandler(BaseHTTPRequestHandler):
    def get_query(self) -> dict:
        query = {}
        qm_index = self.path.find('?')
        if qm_index == -1 or qm_index == len(self.path) - 1:
            return query
        for pair in self.path[qm_index+1:].split('&'):
            key, value = pair.split('=')
            if value.isdigit():
                query[key] = int(value)
                continue
            try:
                float(value)
            except ValueError:
                query[key] = views.plusses_to_spaces(value)
            else:
                query[key] = float(value)
        return query

    def respond(self, 
        status: int,
        body: Optional[str] = None,
        headers: Optional[dict] = None,
    ) -> None:
        self.send_response(status)
        self.send_header(*config.CONTENT_HEADER)
        if headers:
            for header_key, value in headers.items():
                self.send_header(header_key, value)
        self.end_headers()
        self.wfile.write(body.encode())

    def cities_page(self) -> None:
        cities = db.get_cities(self.db_cursor)
        self.respond(config.OK, views.cities_page(cities))

    def main_page(self) -> None:
        self.respond(config.OK, views.main_page())

    def weather_page(self) -> None:
        query = self.get_query()
        if 'city' not in query.keys():
            cities = [city for city, _, _ in db.get_cities(self.db_cursor)]
            self.respond(config.OK, views.weather_dummy_page(cities))
            return
        coords = db.get_coords_by_city(self.db_cursor, query['city'])
        if coords:
            weather_data = weather.get_weather(*coords, self.yandex_key)
            weather_data['city'] = query['city']
            self.respond(config.OK, views.weather_page(weather_data))
        else:
            self.respond(config.BAD_REQUEST, '') # TODO

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
