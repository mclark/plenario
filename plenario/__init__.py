import os
from flask import Flask, render_template, redirect, url_for, request
from raven.contrib.flask import Sentry
from plenario.database import session as db_session
from plenario.models import bcrypt
from plenario.api import api, cache
from plenario.auth import auth, login_manager
from plenario.views import views
from urllib import quote_plus
from plenario.settings import PLENARIO_SENTRY_URL

try:
    sentry = Sentry(dsn=PLENARIO_SENTRY_URL)
except KeyError:
    sentry = None

def create_app():
    app = Flask(__name__)
    app.config.from_object('plenario.settings')
    app.url_map.strict_slashes = False
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    bcrypt.init_app(app)
    if sentry:
        sentry.init_app(app)
    app.register_blueprint(api)
    app.register_blueprint(views)
    app.register_blueprint(auth)
    cache.init_app(app)

    @app.before_request
    def check_maintenance_mode():
        maint = app.config.get('MAINTENANCE')
        if maint and request.path != url_for('views.maintenance') \
            and not 'static' in request.path:
            return redirect(url_for('views.maintenance'))

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def page_not_found(e):
        return render_template('error.html'), 500

    return app

