import aiopg.sa

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    ForeignKey,
    Integer,
    String
    Date,
)

__all__ = ['title', 'user']

meta = MetaData()

title = Table(
    'title', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(70), nullable=False),
    Column('description', String(300), nullable=False)
)

user = Table(
    'user', meta,

    Column('id', Integer, primary_key=True),
    Column('first_name', String(50), nullable=False),
    Column('second_name', String(50), nullable=False),
    Column('hiring date', Date, nullable=False),

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

# example of a database call
async def get_users(conn, user_id):
    result = await conn.execute(user.select().where(user.id == user_id))
    user_record = await result.first()
    if not user_record:
        msg = "Question with id: {} does not exists"
        raise ValueError(f'User with id: {user_id} does not exist')
    return user_record
