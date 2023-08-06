from phlasch.utils import get_env_string


# ---------------------------------------------------------------------- utils

# get shortener base from environment variables
SHORTENER_BASE = get_env_string(
    'PHLASCH_SHORTENER_BASE',
    default='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
)


# --------------------------------------------------------------------- routes

# get shortener url from environment variables
SHORTENER_SHORTEN_URL = get_env_string(
    'PHLASCH_SHORTENER_SHORTEN_URL',
    default='shortener/shorten',
)


# ---------------------------------------------------------------------- views

# get shortener origin from environment variables
SHORTENER_ORIGIN = get_env_string(
    'PHLASCH_SHORTENER_ORIGIN',
    default='',
)
