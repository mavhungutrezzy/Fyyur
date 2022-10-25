import logging
import os
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment

import database
from routes import route_blueprint

from utils.caching import cache


def create_app():

    # *  ----------------------------------------------------------------
    # *  App Config
    # *  ----------------------------------------------------------------

    app = Flask(__name__, static_folder="static")
    moment = Moment(app)
    app.config.from_object("config.DevelopmentConfig")
    database.init_app(app)
    migrate = Migrate(app, database.db)
    cache.init_app(
        app, config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300}
    )
    app.register_blueprint(route_blueprint)

    # *----------------------------------------------------------------------------#
    # * Filters.
    # *----------------------------------------------------------------------------#

    def format_datetime(value, time_format="medium"):
        date = dateutil.parser.parse(value)
        if time_format == "full":
            time_format = "EEEE MMMM, d, y 'at' h:mma"
        elif time_format == "medium":
            time_format = "EE MM, dd, y h:mma"
        return babel.dates.format_datetime(date, time_format, locale="en")

    app.jinja_env.filters["datetime"] = format_datetime

    # *  ----------------------------------------------------------------
    # *  Error Logging
    # *  ----------------------------------------------------------------

    if not app.debug:
        file_handler = FileHandler("error.log")
        file_handler.setFormatter(
            Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info("errors")

    if app.config["ENV"] == "testing":
        with app.app_context():
            database.db.create_all()

    return app


# * ----------------------------------------------------------------------------#
# * Launch.
# * ----------------------------------------------------------------------------#

if __name__ == "__main__":
    create_app().run()
