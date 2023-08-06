from phlasch.stats.routers import routes


# ------------------------------------------------------------------------ app

# configure everything
def configure(app):
    app.add_routes(routes)
