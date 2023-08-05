from __future__ import absolute_import, print_function

from pathlib import Path

from invenio_app.factory import instance_path
from invenio_app.wsgi import application as invenio_application

from .version import __version__


class ProfilingMiddleware:
    def __init__(self, application):
        self.application = application
        self.initialized = False

    def __call__(self, *args, **kwargs):
        if not self.initialized:
            self.initialize()
        return self.application(*args, **kwargs)

    def initialize(self):
        from werkzeug.middleware import profiler
        config_instance_path = instance_path()
        config_file = [
            line.strip()
            for line in (Path(config_instance_path) / 'invenio.cfg').read_text().split('\n')
            if 'OAREPO_PROFILER_' in line
        ]
        vars = {}
        exec('\n'.join(config_file), vars, vars)
        if vars.get('OAREPO_PROFILER_ENABLED'):
            profile_dir = vars.get('OAREPO_PROFILER_PATH', '/tmp/oarepo-profiler')
            if not Path(profile_dir).exists():
                Path(profile_dir).mkdir(parents=True)
            self.application = profiler.ProfilerMiddleware(self.application, profile_dir=profile_dir)
        self.initialized = True


application = ProfilingMiddleware(invenio_application)

__all__ = ('__version__', 'application')
