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
          database=settings.INFLUXDB_DATABASE, raw=False):
    """Wrapper around ``InfluxDBClient.query()``."""
    db = get_db()
    return db.query(query, params, expected_response_code, database, raw)


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


def create_retention_policies():
    db = get_db()
    response = db.query('SHOW RETENTION POLICIES {0}'.format(settings.INFLUXDB_DATABASE), raw=True)
    first_line = response['results'][0]['series'][0]
    try:
        existing_policies = [policy[0] for policy in first_line['values']]
    except KeyError:
        existing_policies = []
    # create missing retention policies
    for policy in settings.RETENTION_POLICIES:
        duration = policy[0]
        name = 'policy_{0}'.format(duration)
        if name not in existing_policies:
            is_default = duration == settings.DEFAULT_RETENTION_POLICY
            db.create_retention_policy(name,
                                       duration,
                                       replication=1,
                                       database=settings.INFLUXDB_DATABASE,
                                       default=is_default)
            print('Created retention policy {0} for influxdb database {1}'.format(name, settings.INFLUXDB_DATABASE))
