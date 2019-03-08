# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""


def app_factory(global_config):
    from resource import VncManagerList, VncManagerDetail
    import falcon

    app = falcon.API()

    session_data = dict()

    app.add_route('/sessions', VncManagerList(session_data))
    app.add_route('/sessions/{username}', VncManagerList(session_data))
    app.add_route('/session', VncManagerDetail(session_data))
    app.add_route('/session/{id}', VncManagerDetail(session_data))
    app.add_route('/lookup', VncManagerDetail(session_data))

    return app
