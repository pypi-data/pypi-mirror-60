from urllib.parse import quote_plus
from phlasch.utils import get_env_string, get_env_int


# ------------------------------------------------------------------- database

# get database settings from environment variables
DB_BACKEND = get_env_string('PHLASCH_DB_BACKEND', default='postgresql')
DB_DRIVER = get_env_string('PHLASCH_DB_DRIVER', default='')
DB_USER = get_env_string('PHLASCH_DB_USER', default='postgres')
DB_PASSWORD = get_env_string('PHLASCH_DB_PASSWORD', default='')
DB_HOST = get_env_string('PHLASCH_DB_HOST', default='localhost')
DB_PORT = get_env_int('PHLASCH_DB_PORT', default=5432)
DB_NAME = get_env_string('PHLASCH_DB_NAME', default='postgres')

# quote password so that it can be passed in a url
DB_PASSWORD = quote_plus(DB_PASSWORD)

# calculate intermediary database settings
DB_DIALECT = '{backend}{plus}{driver}'.format(
    backend=DB_BACKEND,
    plus='+' if DB_DRIVER else '',
    driver=DB_DRIVER,
)
DB_AUTH = '{user}{colon}{password}'.format(
    user=DB_USER,
    colon=':' if DB_PASSWORD else '',
    password=DB_PASSWORD,
)
DB_ADDRESS = '{host}{colon}{port}'.format(
    host=DB_HOST,
    colon=':' if DB_PORT else '',
    port=DB_PORT if DB_PORT else '',
)

# get database url used by sqlalchemy from environment variables
# if not set, it will be set automatically
DB_URL = get_env_string(
    'PHLASCH_DB_URL',
    default='{dialect}://{auth}{at}{address}/{database}'.format(
        dialect=DB_DIALECT,
        auth=DB_AUTH,
        at='@' if DB_AUTH and DB_ADDRESS else '',
        address=DB_ADDRESS,
        database=DB_NAME,
    )
)


# ------------------------------------------------------------------------ app

# get the app's sqlalchemy engine key from environment variables
DB_ENGINE = get_env_string('PHLASCH_DB_ENGINE', default='phlasch')
