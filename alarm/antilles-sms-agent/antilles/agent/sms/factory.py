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
        configure='/var/lib/antilles/sms-agent.yml',
        db='/var/lib/antilles/sms-agent.db',
        **local_conf
):
    import falcon
    from concurrent.futures import ThreadPoolExecutor
    from .util import Counter
    from .resource import Configure, Message

    counter = Counter(db)

    app = falcon.API()

    app.add_route(
        '/config', Configure(configure, counter)
    )
    app.add_route(
        '/', Message(configure, counter, ThreadPoolExecutor(max_workers=1))
    )

    return app
