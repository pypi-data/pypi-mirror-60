from os import path
from aiohttp import web
from aiohttp_swagger import swagger_path
from phlasch.db.settings import DB_ENGINE
from phlasch.db.queries import retrieve_link, update_link_visits


@swagger_path(path.join(path.dirname(__file__), 'swagger', 'redirect.yaml'))
async def redirect(request):
    # validate shortcut
    shortcut = request.match_info.get('shortcut')
    if not shortcut:
        raise web.HTTPNotFound()

    # retrieve from database
    engine = request.app[DB_ENGINE]
    async with engine.acquire() as conn:
        row = await retrieve_link(conn, shortcut)
        if row:
            await update_link_visits(conn, row['id'])

    # not found
    if not row:
        raise web.HTTPNotFound()

    # redirect
    return web.HTTPFound(row['address'])
