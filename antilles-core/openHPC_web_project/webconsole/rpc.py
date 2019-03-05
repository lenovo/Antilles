# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
import json
import logging
import traceback
import uuid
from django.conf import settings

import pika

logger = logging.getLogger(__name__)


class RPCClient(object):
    def __init__(self):
        self.callback = None
        self.corr_id = None
        self.response = None
        self.url = settings.BROKER_URL

    def on_response(self, ch, method, properties, body):
        msg = json.loads(body)
        if self.corr_id == msg.get("correlation_id"):
            self.response = body
            self.callback(ch, method, properties, body)

    def cast(self, name, message, callback=None):
        connection = pika.BlockingConnection(pika.URLParameters(self.url))
        try:
            channel = connection.channel()
            channel.exchange_declare(exchange="openhpc", exchange_type="topic")
            self.corr_id = str(uuid.uuid4())
            if callback is not None:
                self.response = None
                self.callback = callback
                result = channel.queue_declare(exclusive=True)
                callback_queue = result.method.queue
                channel.basic_consume(self.on_response, no_ack=True,
                                      queue=callback_queue)

                msgjson = json.loads(message)
                msgjson["reply_to"] = callback_queue
                msgjson["correlation_id"] = self.corr_id
                message = json.dumps(msgjson)
                channel.basic_publish(exchange="openhpc", routing_key=name, body=message)
                # sometimes it raised exception while using print, but haven't found the reason.
                # So we use 'try-except' to avoid the issue
                try:
                    logger.debug("exchange:%s routing_name:%s body:%s" % ("openhpc", name, message))
                except:
                    logger.debug(traceback.format_exc())
                while self.response is None:
                    connection.process_data_events()
            else:
                channel.basic_publish(exchange="openhpc", routing_key=name, body=message)
                # sometimes it raised exception while using print, but haven't found the reason.
                # So we use 'try-except' to avoid the issue
                try:
                    logger.debug("exchange:%s routing_name:%s body:%s" % ("openhpc", name, message))
                except:
                    logger.exception('error occured while public message')
        finally:
            connection.close()
