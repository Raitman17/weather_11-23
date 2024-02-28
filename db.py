import os

import psycopg

import query


def connect() -> tuple[psycopg.Connection, psycopg.Cursor]:
    default_port = 5555
    port = os.environ.get('PG_PORT')
    credentials = {
        'host': os.environ.get('PG_HOST', default='127.0.0.1'),
        'port': int(port) if port.isdigit() else default_port,
        'dbname': os.environ.get('PG_DBNAME', default='test'),
        'user': os.environ.get('PG_USER', default='test'),
        'password': os.environ.get('PG_PASSWORD'),
    }
    connection = psycopg.connect(**credentials)
    cursor = connection.cursor()
    return connection, cursor


def get_cities(cursor: psycopg.Cursor) -> list[tuple]:
    cursor.execute(query.GET_CITIES)
    return cursor.fetchall()


def get_cities_names(cursor: psycopg.Cursor) -> list[str]:
    cursor.execute(query.GET_CITIES)
    return [city for city, _, _ in cursor.fetchall()]


def get_coords_by_city(cursor: psycopg.Cursor, city_name: str) -> tuple:
    cursor.execute(query.GET_COORDS_BY_CITY, params=(city_name,))
    return cursor.fetchone()


def change_db(
    cursor: psycopg.Cursor, conn: psycopg.Connection,
    db_query: str, query_params: tuple,
) -> bool:
    cursor.execute(db_query, params=query_params)
    conn.commit()
    return bool(cursor.rowcount)


def add_city(
    cursor: psycopg.Cursor, conn: psycopg.Connection,
    city_name: str, lat: float, lon: float,
) -> bool:
    return change_db(cursor, conn, query.INSERT_CITY, (city_name, lat, lon))


def delete_city(
    cursor: psycopg.Cursor, conn: psycopg.Connection,
    city_name: str,
) -> bool:
    return change_db(cursor, conn, query.DELETE_CITY, (city_name,))


def update_params(new_attrs: list) -> str:
    return ', '.join(f'{attr}=%s' for attr in new_attrs)


def update_city(
    cursor: psycopg.Cursor, conn: psycopg.Connection,
    new_attrs: dict, city_name: str,
) -> bool:
    query_params, values_params = [], []
    for attr, new_value in new_attrs.items():
        query_params.append(attr)
        values_params.append(new_value)
    values_params.append(city_name)
    query_update = query.UPDATE_CITY.format(params=update_params(query_params))
    cursor.execute(query_update, params=values_params)
    conn.commit()
    return bool(cursor.rowcount)


def check_token(cursor: psycopg.Cursor, token: str) -> bool:
    cursor.execute(query.CHECK_TOKEN, params=(token,))
    return bool(cursor.fetchone()[0])


def check_city(cursor: psycopg.Cursor, city: str) -> bool:
    cursor.execute(query.CHECK_TOKEN, params=(city,))
    return bool(cursor.fetchone()[0])
