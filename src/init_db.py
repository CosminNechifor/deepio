import argparse
import pathlib
import aiopg.sa
import trafaret as T

from trafaret_config import commandline
from sqlalchemy import create_engine

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
)

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

ADMIN_DB_URL = DSN.format(
    user='postgres', password='postgres', database='postgres',
    host='localhost', port=5432
)

TRAFARET = T.Dict({
    T.Key('postgres'):
        T.Dict({
            'database': T.String(),
            'user': T.String(),
            'password': T.String(),
            'host': T.String(),
            'port': T.Int(),
            'minsize': T.Int(),
            'maxsize': T.Int(),
        }),
    T.Key('host'): T.IP,
    T.Key('port'): T.Int(),
})

meta = MetaData()

title_table = Table(
    'title', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(70), nullable=False),
    Column('description', String(300), nullable=False)
)

user_table = Table(
    'user', meta,

    Column('id', Integer, primary_key=True),
    Column('first_name', String(50), nullable=False),
    Column('second_name', String(50), nullable=False),
    Column('hiring_date', Date, nullable=False),

    Column('title_id',
           Integer,
           ForeignKey('title.id', ondelete='CASCADE'))
)


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


async def get_users(conn, user_id):
    result = await conn.execute(
        user_table.select().where(user_table.id == user_id),
    )
    user_record = await result.first()
    if not user_record:
        raise ValueError(f'User with id: {user_id} does not exist')
    return user_record


def get_config(configuration_path, argv=None):
    ap = argparse.ArgumentParser()
    commandline.standard_argparse_options(
        ap,
        default_config=configuration_path,
    )

    options, unknown = ap.parse_known_args(argv)
    config = commandline.config_from_options(options, TRAFARET)

    return config


def create_configuration():
    base_path = pathlib.Path(__file__).parent.parent
    configuration_path = base_path / 'config' / 'configuration.yaml'
    user_config = get_config(
        configuration_path,
        ['-c', configuration_path.as_posix()],
    )

    return user_config


def setup_db(config):
    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']

    admin_engine = create_engine(ADMIN_DB_URL, isolation_level='AUTOCOMMIT')
    conn = admin_engine.connect()
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
    conn.execute("CREATE DATABASE %s ENCODING 'UTF8'" % db_name)
    conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                 (db_name, db_user))
    conn.close()


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[user_table, title_table])


def drop_tables(engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=[user_table, title_table])


def create_test_data(engine):
    conn = engine.connect()
    conn.execute(title_table.insert(), [
        {'id': 2,
         'name': 'asdddd',
         'description': 'asddddqwe',
         },
    ])
    conn.execute(user_table.insert(), [
        {'id': 3,
         'first_name': 'first_name',
         'second_name': 'second_name',
         'hiring_date': '2018-10-27 21:20:32.619+01',
         'title_id': 2},
    ])
    conn.close()


if __name__ == '__main__':
    config = create_configuration()
    setup_db(config['postgres'])
    database_url = DSN.format(**config['postgres'])
    user_engine = create_engine(database_url)
    create_tables(engine=user_engine)
    create_test_data(engine=user_engine)
