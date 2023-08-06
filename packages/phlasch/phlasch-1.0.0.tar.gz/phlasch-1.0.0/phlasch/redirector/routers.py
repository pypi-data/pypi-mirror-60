from aiohttp import web
from phlasch.redirector.views import redirect


routes = [
    web.get(
        '/{shortcut}',
        redirect,
        name='redirect',
    ),
]
