from datetime import datetime
from threading import Thread
from influxdb import client

from . import settings


def get_db():
    """Returns an ``InfluxDBClient`` instance."""
    return client.InfluxDBClient(
        settings.INFLUXDB_HOST,
        settings.INFLUXDB_PORT,
        settings.INFLUXDB_USER,
        settings.INFLUXDB_PASSWORD,
        settings.INFLUXDB_DATABASE,
    )


def query(query, params={}, expected_response_code=200,
          database=None, raw=False):
    """Wrapper around ``InfluxDBClient.query()``."""
    db = get_db()
    return db.query(query, params,
                    expected_response_code,
                    database=database or settings.INFLUXDB_DATABASE,
                    raw=raw)


def write(name, values, tags={}, timestamp=None, database=None):
    """ write metrics """
    thread = Thread(target=write_threaded,
                    args=(name, values, tags, timestamp, database))
    thread.start()


def write_threaded(name, values, tags={}, timestamp=None, database=None):
    """ Method to be called via threading module. """
    point = {
        'name': name,
        'tags': tags,
        'fields': values
    }
    if isinstance(timestamp, datetime):
        timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
    if timestamp:
        point['timestamp'] = timestamp
    try:
        get_db().write({
            'database': database or settings.INFLUXDB_DATABASE,
            'points': [point]
        })
    except Exception, e:
        if settings.INFLUXDB_FAIL_SILENTLY:
            pass
        else:
            raise e


def create_database():
    """ creates database if necessary """
    db = get_db()
    response = db.query('SHOW DATABASES', raw=True)
    first_line = response['results'][0]['series'][0]
    try:
        databases = [database[0] for database in first_line['values']]
    except KeyError:
        databases = []
    # if database does not exists, create it
    if settings.INFLUXDB_DATABASE not in databases:
        db.create_database(settings.INFLUXDB_DATABASE)
        print('Created inlfuxdb database {0}'.format(settings.INFLUXDB_DATABASE))
