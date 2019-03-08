#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

cimport at

import logging

logger = logging.getLogger(__name__)

cdef public void LogErr(const char *msg):
    logger.error(msg)

cdef public void LogDebug(const char *msg):
    logger.debug(msg)

cdef public void LogInfo(const char *msg):
    logger.info(msg)


class ModemError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'Modem Error: {}'.format(self.message)


cdef class Modem:
    cdef at.type_modem modem

    def __init__(self, const char* path):
        cdef at.type_serialport* serialport = &self.modem.serialport;

        serialport.portname[:]=path
        serialport.speed = 9600
        serialport.databits = 8
        serialport.stopbits = 1
        serialport.parity = 'N'
        serialport.flow = 0
        serialport.fd = 0
        serialport.outtime = 150

        self.modem.modemtype = at.MODEM_TYPE_GPRS

        logger.info(
            'modem configed:\n' \
            'modem_type: %d(0:MODEM_TYPE_GPRS; 1:MODEM_TYPE_CDMA)\n' \
            'serialport_name: %s\n' \
            'serialport_speed: %d\n' \
            'serialport_databits: %d\n' \
            'seriaport_stopbits: %d\n' \
            'seriaport_parity: %c(N/n:PARITY_NONE; O/o:PARITY_ODD; E/e:PARITY_EVEN; S/s:PARITY_SPACE)\n' \
            'seriaport_flow: %d',
            self.modem.modemtype,
            serialport.portname,
            serialport.speed,
            serialport.databits,
            serialport.stopbits,
            serialport.parity,
            serialport.flow
        )

    def open(self):
        if at.modem_open(&self.modem) != 0:
            raise ModemError('modem open fail')

    def close(self):
        at.modem_close(&self.modem)

    def send_msg(self, const char* phone, msg):
        msg = msg.decode('utf-8').encode('utf-16-be')
        if at.send_unicode_msg_gprs(&self.modem, phone, msg, len(msg)) != 0:
            raise ModemError('modem send_msg fail')

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()