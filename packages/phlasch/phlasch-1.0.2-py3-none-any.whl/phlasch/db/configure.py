from aiopg.sa import create_engine
from phlasch.db.settings import DB_URL, DB_ENGINE


# ------------------------------------------------------------------- database

# configure database startup
async def startup_db(app):
    engine = await create_engine(DB_URL)
    app[DB_ENGINE] = engine


# configure database cleanup
async def cleanup_db(app):
    engine = app[DB_ENGINE]
    engine.close()
    await engine.wait_closed()


# ------------------------------------------------------------------------ app

# configure everything
def configure(app):
    app.on_startup.append(startup_db)
    app.on_cleanup.append(cleanup_db)
