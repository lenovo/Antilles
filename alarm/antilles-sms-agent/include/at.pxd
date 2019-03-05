"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

cdef extern from "at.h":
    enum: MODEM_TYPE_GPRS

    ctypedef struct type_serialport:
        char portname[256]
        int speed
        int databits
        int stopbits
        char parity
        int flow
        int fd
        int outtime

    ctypedef struct type_modem:
        type_serialport serialport
        int modemtype

    cdef int modem_open(type_modem* modem)
    cdef int modem_close(type_modem* modem)

    cdef int send_unicode_msg_gprs(type_modem* modem, const char *phone, const char *msg, int msglen)


