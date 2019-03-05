# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

logger = logging.getLogger(__name__)


def app_factory(
        global_config,
        appid, secret,
        configure='/var/lib/antilles/wechat_agent.yml',
        timeout=30,
        cached_timeout=3600,
        **local_conf
):
    import falcon
    from wechatpy.client import WeChatClient
    from .resource import Configure, Message

    app = falcon.API()

    client = WeChatClient(
        appid, secret,
        timeout=timeout
    )

    app.add_route(
        '/config', Configure(
            configure,
            client
        )
    )
    app.add_route(
        '/', Message(
            configure,
            client,
            cached_timeout=cached_timeout
        )
    )

    return app
