import os

from casbin import Enforcer

basedir = os.path.abspath(os.path.dirname(__file__))


class PyCasbin(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['flask-pycasbin'] = self

        self._set_default_config(app)
        self._create_casbin_enforcer(app)

    def _set_default_config(self, app):
        app.config.setdefault('CASBIN_MODEL', f'{basedir}/rules/default_model.conf')
        app.config.setdefault('CASBIN_POLICY', f'{basedir}/rules/default_policy.csv')

    def _create_casbin_enforcer(self, app):
        self.enforcer = Enforcer(model=app.config.get('CASBIN_MODEL'),
                                 adapter=app.config.get('CASBIN_POLICY'),
                                 enable_log=True)
