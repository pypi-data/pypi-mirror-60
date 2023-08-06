from os import path
from aiohttp import web
from aiohttp_swagger import swagger_path
from phlasch.utils import get_origin
from phlasch.db.settings import DB_ENGINE
from phlasch.db.queries import list_links, retrieve_link
from phlasch.stats.settings import STATS_ORIGIN


@swagger_path(
    path.join(path.dirname(__file__), 'swagger', 'stats_list.yaml')
)
async def stats_list(request):
    # list from database
    engine = request.app[DB_ENGINE]
    async with engine.acquire() as conn:
        rows = await list_links(conn)

    origin = get_origin(request, STATS_ORIGIN)

    # return stats list
    return web.json_response([
        {
            **row,
            'url': f'{origin}/{row["shortcut"]}',
            'origin': origin,
        } for row in rows
    ])


@swagger_path(
    path.join(path.dirname(__file__), 'swagger', 'stats_retrieve.yaml')
)
async def stats_retrieve(request):
    # validate shortcut
    shortcut = request.match_info.get('shortcut')
    if not shortcut:
        return web.json_response({
            'shortcut': 'this field does not exist.',
        }, status=404)

    # retrieve from database
    engine = request.app[DB_ENGINE]
    async with engine.acquire() as conn:
        row = await retrieve_link(conn, shortcut)

    # not found
    if not row:
        return web.json_response({
            'shortcut': 'this field does not exist.',
        }, status=404)

    origin = get_origin(request, STATS_ORIGIN)

    # return stats retrieve
    return web.json_response({
        **row,
        'url': f'{origin}/{row["shortcut"]}',
        'origin': origin,
    })
