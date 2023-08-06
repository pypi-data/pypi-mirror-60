flask-dataapi
=============

Automatically generate data APIs for your Flask routes, with very little
effort on your part. It should integrate into your existing application with
very few changes required.

Usage
-----

Given the following code::

    from flask import Flask

    app = Flask(__name__)

    @app.route('/foo')
    def foo():
        return render_template('foo.html', foo='bar', baz='boo')

We can automatically generate API functions for this route, rather simply::

    from flask import Flask
    from flask_dataapi import DataApi

    app = Flask(__name__)
    api = DataApi(app)

    @api.route('/foo')
    def foo(render_template):
        return render_template('foo.html', foo='bar', baz='boo')

There are only two changes made. First, we call ``api.route`` for the
decorator, and second, the first argument to the view function is the
``render_template`` function that we'll call.

This will automatically add a second route of ``/foo.json`` that outputs
JSON of the data that was provided to ``render_template``. The route will
have a name of ``foo_api``, so links or other references will use that name,
e.g. ``url_for('foo_api')``.

Motivation
----------
In addition to free code, we also need free data. This makes it trivial to
ensure that all data presented to users is easily extractable by the user.

License
-------
flask-dataapi is available under the terms of the AGPL, version 3 or any later
version.