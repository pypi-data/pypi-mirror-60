from phlasch.utils import get_env_string


# --------------------------------------------------------------------- routes

# get stats list url from environment variables
STATS_LIST_URL = get_env_string(
    'PHLASCH_STATS_LIST_URL',
    default='stats/list',
)

# get stats retrieve url from environment variables
STATS_RETRIEVE_URL = get_env_string(
    'PHLASCH_STATS_RETRIEVE_URL',
    default='stats/retrieve',
)


# ---------------------------------------------------------------------- views

# get stats origin from environment variables
STATS_ORIGIN = get_env_string(
    'PHLASCH_STATS_ORIGIN',
    default='',
)
