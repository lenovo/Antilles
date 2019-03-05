/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */


#ifndef AT_HEADER_H
#define AT_HEADER_H

#include "serialport.h"

#define MODEM_TYPE_GPRS   0
#define MODEM_TYPE_CDMA   1
#define SMS_TEXTMSG_SIZE  58

#define READ_BUFF_LEN   1024
#define READ_BUFF_SIZE  1024
#define WRITE_BUFF_LEN  1024
#define CTRL_Z    "\x00\x1A\n"          /*finish sms input*/
#define CTRL_Z_LEN     3                /*length of CTRL_Z*/

#define CONFIG_FILE     "./serial.conf"
#define CONFIG_APP      "serialport"

#define _DEBUG 0

typedef struct STU_MODEM_PARAM
{
    type_serialport  serialport;
    int             rssil;
    int             ber;
    int             modemtype;
    char            sca[20];
}type_modem, * lptype_modem;


int utf8_unicode(const char *in, size_t instrlen, char *out, size_t outbufsiz);
int lim_to_pdu(const char *sca,const char *phone,const char *msg, int msglen, char *pdu, size_t pdusize);
int phone_to_pdu(const char *phone, char *pdu, size_t pdusize);
int msg_to_ucs2(const char *msg, int msglen, char *ucs, size_t ucssize);

int modem_init( lptype_modem modem);
int modem_setup( lptype_modem modem, char *portname);
int modem_open( lptype_modem modem);
int modem_reopen( lptype_modem modem);
int modem_close( lptype_modem modem);

int at_test(lptype_modem modem);

int modem_get_csq( lptype_modem modem);
int send_at_msg( lptype_modem modem, const char *atsmg, const char *replhead, unsigned char *rinfo, int rsize);
int send_unicode_msg_gprs(lptype_modem modem, const char *phone, const char *msg, int msglen);

/***************************************************************/
void printf_data(const char *exp, const char *attext, int size);
int test_at(void);

#endif /* AT_HEADER_H */