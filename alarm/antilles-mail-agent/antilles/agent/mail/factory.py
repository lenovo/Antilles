# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

logger = logging.getLogger(__name__)


def app_factory(
        global_config,
        configure='/var/lib/antilles/mail-agent.yml',
        timeout=60,
        **local_conf
):
    import falcon
    from .resource import Configure, Message

    app = falcon.API()

    app.add_route(
        '/config', Configure(configure)
    )
    app.add_route(
        '/', Message(
            configure,
            timeout=timeout
        )
    )

    return app
