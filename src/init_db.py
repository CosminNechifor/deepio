import argparse
import pathlib

from sqlalchemy import create_engine, MetaData

# from src.tools.db import user

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

ADMIN_DB_URL = DSN.format(
    user='postgres', password='postgres', database='postgres',
    host='localhost', port=5432
)
print(ADMIN_DB_URL)

# admin_engine = create_engine(ADMIN_DB_URL, isolation_level='AUTOCOMMIT')


def get_config_path():
    path = pathlib.Path(__file__).parent.parent
    print(path)

# USER_CONFIG_PATH = BASE_DIR / 'config' / 'polls.yaml'
# USER_CONFIG = get_config(['-c', USER_CONFIG_PATH.as_posix()])
# USER_DB_URL = DSN.format(**USER_CONFIG['postgres'])
# user_engine = create_engine(USER_DB_URL)
#
# TEST_CONFIG_PATH = BASE_DIR / 'config' / 'polls_test.yaml'
# TEST_CONFIG = get_config(['-c', TEST_CONFIG_PATH.as_posix()])
# TEST_DB_URL = DSN.format(**TEST_CONFIG['postgres'])
# test_engine = create_engine(TEST_DB_URL)

if __name__ == '__main__':
    get_config_path()
