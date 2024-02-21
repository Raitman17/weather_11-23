from http.server import HTTPServer, BaseHTTPRequestHandler

import db

HOST, PORT = '127.0.0.1', 8000
OK = 200
MAIN_PAGE = 'index.html'

class MyRequestHandler(BaseHTTPRequestHandler):
    db_connection, db_cursor = db.connect()

    def do_GET(self) -> None:
        self.send_response(OK)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(MAIN_PAGE, 'r') as file:
            page = file.read()
        cities = '<br>'.join(str(city) for city in db.get_cities(self.db_cursor))
        page_with_datetime = page.format(cities=cities)
        self.wfile.write(page_with_datetime.encode())

if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), MyRequestHandler)
    print(f'Server started at http://{HOST}:{PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Interrupted by user!')
    finally:
        server.server_close()
