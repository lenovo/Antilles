# -*- coding: utf-8 -*-
"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django_pastedeploy_settings import get_configured_django_wsgi_app
from antilles.tools.passwd import fetch_pass


def make_application(global_config, **local_conf):

    db_host = global_config.get("db_host", None)
    db_port = global_config.get("db_port", None)
    db_name = global_config.get("db_name", None)

    # Set db user and db password
    db_account = fetch_pass(
        keyword="postgres",
        host=db_host,
        port=db_port,
        db=db_name
    )
    global_config["db_user"] = db_account.user
    global_config["db_pass"] = db_account.passwd

    # Set influxdb user and password
    influx_account = fetch_pass(
        keyword="influxdb",
        host=db_host,
        port=db_port,
        db=db_name
    )
    global_config["influx_username"] = influx_account.user
    global_config["influx_password"] = influx_account.passwd

    # Set confluent user and password
    confluent_account = fetch_pass(
        keyword="confluent",
        host=db_host,
        port=db_port,
        db=db_name
    )
    global_config["confluent_user"] = confluent_account.user
    global_config["confluent_pass"] = confluent_account.passwd

    app = get_configured_django_wsgi_app(global_config, **local_conf)

    return app
