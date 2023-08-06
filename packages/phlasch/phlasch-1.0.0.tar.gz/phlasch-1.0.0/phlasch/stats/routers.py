from aiohttp import web
from phlasch.stats.settings import STATS_LIST_URL, STATS_RETRIEVE_URL
from phlasch.stats.views import stats_list, stats_retrieve


routes = [
    web.get(
        f'/{STATS_LIST_URL}',
        stats_list,
        name='stats_list',
    ),
    web.get(
        f'/{STATS_RETRIEVE_URL}/{{shortcut}}',
        stats_retrieve,
        name='stats_retrieve',
    ),
]
