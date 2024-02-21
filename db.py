import psycopg
import os
import query

def connect() -> tuple[psycopg.Connection, psycopg.Cursor]:
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
    cursor.execute(query.GET_CITIES)
    cities = cursor.fetchall()
    return cities

def get_coords_by_city(cursor: psycopg.Cursor, city_name: str) -> tuple:
    cursor.execute(query.GET_COORDS_BY_CITY, params=(city_name,))
    return cursor.fetchone()