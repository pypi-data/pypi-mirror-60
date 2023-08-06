import os


# ----------------------------------------------- environment variable getters

# get str from environment variable
def get_env_string(key, default=''):
    return os.environ.get(key, default=default)


# get bool from environment variable
def get_env_bool(key, default=False):
    value = os.environ.get(key)
    return value.lower() in ('1', 'y', 'yes', 'true',) if value else default


# get int from environment variable
def get_env_int(key, default=0):
    value = os.environ.get(key)
    return int(value) if value else default


# get list from environment variable
def get_env_list(key, default=None):
    default = [] if default is None else default
    value = os.environ.get(key)
    return value.split(';') if value else default


# --------------------------------------------------- request variable getters

# get the origin of the request
def get_origin(request, override=''):
    return override if override else f'{request.scheme}://{request.host}'
