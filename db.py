import psycopg
import dotenv
import os

def connect() -> tuple[psycopg.Connection, psycopg.Cursor]:
    dotenv.load_dotenv()
    port = os.environ.get('PG_PORT')
    credentials = {
        'host': os.environ.get('PG_HOST', default='127.0.0.1'),
        'port': int(port) if port.isdigit() else 5555,
        'dbname': os.environ.get('PG_DBNAME', default='test'),
        'user': os.environ.get('PG_USER', default='test'),
        'password': os.environ.get('PG_PASSWORD'),
    }
    connection = psycopg.connect(**credentials)
    cursor = connection.cursor()
    return connection, cursor

def get_cities(cursor: psycopg.Cursor) -> list[tuple]:
    cursor.execute('select * from city;')
    cities = cursor.fetchall()
    return cities
