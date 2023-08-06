from os import path
from alembic.config import main


def revision(app, message):
    main(argv=[
        '-c', path.join(path.dirname(__file__), 'alembic.ini'),
        '--name', app,
        'revision', '-m', message,
        '--autogenerate'
    ])


def history(app):
    main(argv=[
        '-c', path.join(path.dirname(__file__), 'alembic.ini'),
        '--name', app,
        'history',
        '--verbose',
    ])


def upgrade(app, rev):
    main(argv=[
        '-c', path.join(path.dirname(__file__), 'alembic.ini'),
        '--name', app,
        'upgrade', rev,
    ])


def downgrade(app, rev):
    main(argv=[
        '-c', path.join(path.dirname(__file__), 'alembic.ini'),
        '--name', app,
        'downgrade', rev,
    ])
