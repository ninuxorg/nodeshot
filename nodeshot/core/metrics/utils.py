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


def query(query, params={}, epoch=None,
          expected_response_code=200, database=None):
    """Wrapper around ``InfluxDBClient.query()``."""
    db = get_db()
    database = database or settings.INFLUXDB_DATABASE
    return db.query(query, params, epoch, expected_response_code, database=database)


def write_async(name, values, tags={}, timestamp=None, database=None):
    """ write metrics """
    thread = Thread(target=write,
                    args=(name, values, tags, timestamp, database))
    thread.start()


def write(name, values, tags={}, timestamp=None, database=None):
    """ Method to be called via threading module. """
    point = {
        'measurement': name,
        'tags': tags,
        'fields': values
    }
    if isinstance(timestamp, datetime):
        timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
    if timestamp:
        point['time'] = timestamp
    try:
        get_db().write({'points': [point]},
                       {'db': database or settings.INFLUXDB_DATABASE})
    except Exception, e:
        if settings.INFLUXDB_FAIL_SILENTLY:
            pass
        else:
            raise e


def create_database():
    """ creates database if necessary """
    db = get_db()
    response = db.query('SHOW DATABASES')
    items = list(response.get_points('databases'))
    databases = [database['name'] for database in items]
    # if database does not exists, create it
    if settings.INFLUXDB_DATABASE not in databases:
        db.create_database(settings.INFLUXDB_DATABASE)
        print('Created inlfuxdb database {0}'.format(settings.INFLUXDB_DATABASE))
