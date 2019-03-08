# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from antilles.tools.passwd import fetch_pass

logger = logging.getLogger(__name__)


def _build_app():
    import falcon

    app = falcon.API()

    return app


def _add_route(app, client):
    from .resource import Async, Shell, Console

    app.add_route('/async', Async(client))
    app.add_route('/{name}/shell/sessions', Shell(client))
    app.add_route('/{name}/console/sessions', Console(client))


def _fetch_confluent_account(global_config):
    db_host = global_config.get("db_host", None)
    db_port = global_config.get("db_port", None)
    db_name = global_config.get("db_name", None)

    return fetch_pass(
        keyword="confluent",
        host=db_host,
        port=db_port,
        db=db_name
    )


def app_factory(
        global_config,
        confluent_host='127.0.0.1',
        confluent_port='4005',
        confluent_user=None,
        confluent_pass=None,
        timeout=180
):
    app = _build_app()

    if confluent_user is None or confluent_pass is None:
        confluent_account = _fetch_confluent_account(global_config)
        confluent_user = confluent_account.user
        confluent_pass = confluent_account.passwd

    from .client import ConfluentClient
    client = ConfluentClient(
        host=confluent_host,
        port=int(confluent_port),
        user=confluent_user,
        password=confluent_pass,
        timeout=int(timeout)
    )

    _add_route(app, client)

    return app


def cluster_app_factory(
        global_config,
        nodes_files='/etc/antilles/nodes.csv',
        confluent_port='4005',
        timeout=180
):
    app = _build_app()

    from .config import Configure
    from .client import ClusterConfluentClient

    confluent_account = _fetch_confluent_account(global_config)
    confluent_user = confluent_account.user
    confluent_pass = confluent_account.passwd

    client = ClusterConfluentClient(
        configure=Configure.parse(nodes_files),
        port=int(confluent_port),
        user=confluent_user,
        password=confluent_pass,
        timeout=int(timeout)
    )

    _add_route(app, client)

    return app
