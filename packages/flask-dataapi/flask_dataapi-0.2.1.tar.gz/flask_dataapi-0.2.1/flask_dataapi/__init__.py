"""
Copyright (C) 2019 Kunal Mehta <legoktm@member.fsf.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from flask import jsonify, render_template


class DataApi:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def render_json(self, template, **kwargs):
        """has function signature of render_template, but jsonify instead"""
        return jsonify(**kwargs)

    def proxy(self, f, mode: str):
        """wrapper around f to insert render_ as first argument"""
        if mode == 'ui':
            name = f.__name__
            render_func = render_template
        elif mode == 'api':
            name = f.__name__ + '_api'
            render_func = self.render_json  # type: ignore
        else:
            raise ValueError('Unknown mode: %s' % mode)

        def func(*args, **kwargs):
            return f(render_func, *args, **kwargs)

        # Override the name so that flask sees the original name
        # used in defining the route instead of "func"
        func.__name__ = name
        return func

    def route(self, path: str, *args, **kwargs):
        """our implementation of @app.route(...)"""
        def decorate(f):
            # Register the original path
            self.app.route(path, *args, **kwargs)(self.proxy(f, 'ui'))
            if path.endswith('/'):
                api_path = path + 'api.json'
            else:
                api_path = path + '.json'
            self.app.route(api_path, *args, **kwargs)(self.proxy(f, 'api'))

        return decorate
