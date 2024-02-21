from http.server import HTTPServer, BaseHTTPRequestHandler

import config
import db
from typing import Optional

class MyRequestHandler(BaseHTTPRequestHandler):
    db_connection, db_cursor = db.connect()

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

    def do_GET(self) -> None:
        with open(config.TEMPLATE_MAIN, 'r') as file:
            page = file.read()
        cities = '<br>'.join(str(city) for city in db.get_cities(self.db_cursor))
        page_with_datetime = page.format(cities=cities)
        self.respond(config.OK, page_with_datetime)

if __name__ == '__main__':
    server = HTTPServer((config.HOST, config.PORT), MyRequestHandler)
    print(f'Server started at http://{config.HOST}:{config.PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Interrupted by user!')
    finally:
        server.server_close()
