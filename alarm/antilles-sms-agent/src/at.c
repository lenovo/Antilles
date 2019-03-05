/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */


#include <Python.h>

#include "at.h"
#include "pysms.h"
#include "serialport.h"


int phone_to_pdu(const char *phone, char *pdu, size_t pdusize) {
    int nret = 0;

    if(pdu == NULL || pdu == (char*)-1 || phone == NULL || phone == (char*)-1 ) {
        return -1;
    }
    if(pdusize < 16) {
        return -2;
    }
    if(strlen(phone) < 11) {
        LogErr("phone number is too short");
        return -3;
    }
    char * pd = pdu;
    char * ph = (char*) phone;
    memset(pd,0,16);

    if(*ph == '+') {
        ph++;
    }else {
        pd[0] = '6';
        pd[1] = '8';
        pd+=2;
        nret++;
    }
    while(*ph >= '0' && *ph <= '9' && nret < 7) {
        pd[1] = *ph;ph++;
        nret++;
        if(*ph >= '0' && *ph <= '9') {
            pd[0] = *ph; ph++;
        } else {
            pd[0] = 'F'; break;
        }
        pd +=2;
    }
    return nret;
}

int msg_to_ucs2(const char *msg, int msglen, char *ucs, size_t ucssize) {
    char log_msg[256];
    int i,nret = 0;
    if(ucs == NULL || ucs == (char*)-1 || msg == NULL || msg == (char*)-1 )
        return -1;
    int  conv_len = msglen;
    if(ucssize < conv_len*2) {
        sprintf(log_msg, "UCS buff size(%zu) < %d. %s:%d", ucssize, conv_len*2, __FILE__, __LINE__);
        LogErr(log_msg);
        return -3;
    }
    char * p_conv = (char*)msg;
    char * p_ucs = ucs;
    for(i=0;i<conv_len;i++) {
        snprintf(p_ucs, 10, "%2.2X", (*p_conv)&0xFF); //conv_buf[i]&0xFF);
        p_ucs += 2;
        p_conv++;
    }
    *p_ucs = '\0';
    nret = conv_len;
    return nret;
}

int lim_to_pdu(const char *sca,const char *phone,const char *msg, int msglen, char *pdu, size_t pdusize) {
    int nret = 0;
    char phpdu[2][20] = {{0},{0}};
    int  iph[2] = {0};
    char ucs[1024] = {0};
    if(pdu == NULL || pdu == (char*)-1 || phone == NULL || msg == NULL || phone == (char*)-1 || msg == (char*)-1)
        return -1;
    /* 处理目标号码 */
    iph[0] = phone_to_pdu(phone, phpdu[0],20);
    if(iph[0] < 0)
        return -4;
    /* 处理短信中心 */
    iph[1] = phone_to_pdu(sca, phpdu[1],20);
    /* 处理信息编码 */
    int ucslen = msg_to_ucs2(msg, msglen,ucs,1024);
    if(ucslen <= 0)
        return -5;
    /* 生成PDU */
    char * p_pdu = pdu;
        /** SMSC - 短信中心地址 **/
        if(iph[1] >= 6)
        {
            int len = snprintf( p_pdu, pdusize, "%2.2x91%s", iph[1]+1, phpdu[1]);
            p_pdu +=len;
            /**
             *   [08] SMSC 地址信息的长度
             *   [91] 号码格式 91-国际格式号码,81-国内格式号码
             *   [*]  短信中心号码 683110102105F0
             **/
        }
        else
        {
            p_pdu[0] = '0';
            p_pdu[1] = '0';
            p_pdu +=2;
        }
        nret = 0;
        int len = snprintf( p_pdu, pdusize - (p_pdu - pdu), "11190D91%14s000801%2.2x%s",phpdu[0], ucslen,ucs);
        nret = len/2;
    /**
     *  [11] PDU类型 - 数据报类型 包含TP-MTI(2bit)，TP-RD(1bit)，TP-VPF(2bit)，TP-RP（1bit），TP-UDHI(1bit)，TP-SRR(1bit)
     *          0 0 0 10 0 01
     *          TP-MTI: 01   消息类型指示符,       Bit 1,0：01指示为SMS-SUBMIT类型;
     *          TP-RD： 0    是否拒绝相同重复消息, Bit   2： 0指示短消息中心接受未转发的具有相同TP-MR的消息;
     *          TP-VPF：10   有效期格式,           Bit 4,3：10指示使用相对格式;
     *          TP-SRR：0    Status-Report-Request,Bit   5： 0指示不使用状态报告;
     *          TP-UDHI:0    用户数据头标示,       Bit   6： 0指示这是一个SMS消息，没有用户数据头。EMS消息需要设置;
     *          TP-RP： 0    回复路径,             Bit   7： 0指示没有设置回复路径;
     *  [19] MR - 消息参考值
     *       DA - 目的地址
     *  [0D]    目标地址数字个数,共13个十进制数(不包括91 和’F’)
     *  [91]    目标地址格式
     *  [*]     目标地址 "688116305307F2"
     *  [00] PID - 协议识别号, 00：普通点对点
     *  [08] DCS - 短信息的编码格式, 08：UCS2编码用于发送Unicode 字符
     *  [01] VP  - 短信息的有效时间, 00..8F -（VP＋1）*5分
     *  [08] UDL - 数据内容的长度
     *  [*]  UD  - 具体短信内容 "828265E55FEB4E50"
     **/
    return nret;
}

int modem_open( lptype_modem modem) {
    char log_msg[256];

    unsigned char ReadBuffer[COM_MAX_BUFFER+1];

    if(modem == NULL || modem == (lptype_modem)-1)
        return -1;
    if( modem->serialport.portname == NULL || modem->serialport.portname == (char*)-1)
        return -1;

    if( com_open(&modem->serialport) == -1) {
        sprintf(log_msg, "com_open Fail. %s:%d", __FILE__, __LINE__);
        LogErr(log_msg);
        return -2;
    }
    if(com_setup(&modem->serialport ) == -1) {
        sprintf(log_msg, "com_setup Fail. %s:%d", __FILE__, __LINE__);
        LogErr(log_msg);
        com_close(&modem->serialport);
        return -3;
    }
    send_at_msg(modem, "ATE1\r\0", "ATE", ReadBuffer, COM_MAX_BUFFER);
    sleep(1);

    if(at_test(modem ) == -1) {
        sprintf(log_msg, "at_test Fail. %s:%d", __FILE__, __LINE__);
        LogErr(log_msg);
        com_close(&modem->serialport);
        return -4;
    }
    send_at_msg(modem, "ATE1\r\0", "ATE", ReadBuffer, COM_MAX_BUFFER);
    send_at_msg(modem, "AT+CGMR\r\0", "+CGMR", ReadBuffer, COM_MAX_BUFFER);

    int err_count = 0;
    if(modem->modemtype != MODEM_TYPE_GPRS) {
        com_close(&modem->serialport);
        return -6;
    }
    send_at_msg(modem, "AT+CMGF=0\r\0", "+CMGF" ,ReadBuffer,COM_MAX_BUFFER);
    send_at_msg(modem, "AT+CSCA?\r\0", "+CSCA" ,ReadBuffer,COM_MAX_BUFFER);

    while(strstr((char *)ReadBuffer, "ERROR") != 0) {
        sleep(2);
        send_at_msg(modem, "AT\r\0", "AT" ,ReadBuffer,COM_MAX_BUFFER);
        send_at_msg(modem, "AT+CSCA?\r\0", "+CSCA" ,ReadBuffer,COM_MAX_BUFFER);
        err_count++;
        if(err_count >= 20)
            return -5;
    }

    if(strstr((char *)ReadBuffer, "OK") != 0) {
        /*"+CSCA: "+8613010112500",145    OK"*/
        char * p = strstr((char *)ReadBuffer,"+CSCA:");
        p += 6;
        while(*p != '\"' && *p != '\0')p++;
        if(*p != '\0')p++;
        strncpy( modem->sca,p,16);
        p = modem->sca;
        while(*p != '\"' && *p != '\0')p++;
        *p = '\0';
        sprintf(log_msg, "SCA=\"%s\". %s:%d", modem->sca, __FILE__, __LINE__);
        LogInfo(log_msg);

    }

    return 0;
}

int modem_close(lptype_modem modem) {
    if(modem == NULL || modem == ( lptype_modem)-1)
        return -1;
    return com_close(&modem->serialport);
}

int modem_get_csq(lptype_modem modem) {
    unsigned char ReadBuffer[COM_MAX_BUFFER+1];
    if(modem == NULL || modem == ( lptype_modem)-1)
        return -1;
    if(modem->serialport.fd <= 0)
        return -2;
    send_at_msg(modem, "AT+CSQ\r\0", "+CSQ" ,ReadBuffer,COM_MAX_BUFFER);

    if(strstr((char *)ReadBuffer,"ERROR") != 0) {
        modem->rssil = 99;
        modem->ber   = 99;
        return -6;
    }

    if(strstr((char *)ReadBuffer,"OK") != 0) {
        char   s_rssil[20];
        char * p_ber;
        char * p = strstr((char *)ReadBuffer,"+CSQ:");
        p += 5;
        while(*p != ' ' && *p != '\0')p++;
        strncpy( s_rssil,p,20);
        p = s_rssil;
        while(*p != ',' && *p != '\0')p++;
        *p = '\0';p++;
        p_ber = p;
        while(*p >= '0' && *p <= '9')p++;
        *p = '\0';
        modem->rssil = atoi(s_rssil);
        modem->ber   = atoi(p_ber);
        return 0;
    }
    return -3;
}

int at_test(lptype_modem modem) {
    int count = 0;
    unsigned char ReadBuffer[COM_MAX_BUFFER+1];
    unsigned char WriteBuffer[COM_MAX_BUFFER+1] = "AT\r\0";
    ssize_t rCount = 0;
    ssize_t wCount = 0;

    if(modem == NULL || modem == ( lptype_modem)-1)
        return -1;
    while (count < 10) {
        count++;
        sleep(1);
        memset(ReadBuffer, '\0', COM_MAX_BUFFER+1);
        rCount = com_read( &modem->serialport, ReadBuffer, COM_MAX_BUFFER);
        if(rCount > 0) {
            printf_data("Read com", (char *)ReadBuffer,(int)rCount);
            if((strstr((char *)ReadBuffer,"AT") != NULL) && (strstr((char *)ReadBuffer,"OK") != NULL))
                break;
        }
        sleep(1);

        wCount = com_write( &modem->serialport,WriteBuffer,strlen((char *)WriteBuffer));
        if(wCount > 0) {
          printf_data( "Wrote com", (char *)WriteBuffer,(int)wCount);
        }
    }
    if(count < 10)
        return 0;
    return -1;
}

int send_at_msg(lptype_modem modem, const char *atsmg, const char *replhead, unsigned char *rinfo, int rsize) {
    ssize_t rCount = 0;
    ssize_t wCount = 0;
    if(modem == NULL || modem == ( lptype_modem)-1)
        return -1;
    wCount = com_write( &modem->serialport,(unsigned char*)atsmg,strlen((char *)atsmg));
    if(wCount <= 0) {
        return -1;
    }
    sleep(2);
    memset(rinfo,'\0',rsize);
    rCount = com_read( &modem->serialport,rinfo,rsize-1);
    if(rCount > 0) {
        return 0;
    }
    return -1;
}


int send_unicode_msg_gprs(lptype_modem modem, const char *phone, const char *msg, int msglen) {
    char log_msg[256];
    int i;
    unsigned char ReadBuffer[COM_MAX_BUFFER+1];
    char pdu[1024] = {0};
    sprintf(log_msg, "phone=\"%s\". %s:%d", phone, __FILE__, __LINE__);
    LogInfo(log_msg);

    printf_data("unicode_msg", msg , msglen);
    int pdulen = lim_to_pdu(modem->sca, phone, msg, msglen, pdu, 1024);
    sprintf(log_msg, "PDU=\"%s\". %s:%d", pdu, __FILE__, __LINE__);
    LogInfo(log_msg);
    if (pdulen<0){
        return -4;
    }

    char buf[128] = {0};
    char buf2[1024] = {0};
    sleep(1);
    send_at_msg(modem, "AT\r\0", "AT", ReadBuffer, COM_MAX_BUFFER);
    send_at_msg(modem, "AT\r\0", "AT", ReadBuffer, COM_MAX_BUFFER);
    send_at_msg(modem, "AT+CMGF=0\r\0", "+CMGF", ReadBuffer, COM_MAX_BUFFER);
    sleep(1);

    snprintf(buf, 128, "AT+CMGS=%3.3d\r\n", pdulen);
    int cmd_len = snprintf(buf2, 1024, "%s\x1a", pdu);


    send_at_msg(modem, buf, ">", ReadBuffer, COM_MAX_BUFFER);
    printf_data( "dce_send", (char *)ReadBuffer, strlen((char *)ReadBuffer));
    if(strstr((char *)ReadBuffer,"ERROR") != 0) {
        sprintf(log_msg, "message length is too long. %s:%d", __FILE__, __LINE__);
        LogErr(log_msg);
        return -2;
    }

    ssize_t rCount = 0;
    ssize_t wCount = 0;
    wCount = com_write( &modem->serialport, (unsigned char*)buf2, cmd_len);
    if(wCount <= 0) {
        return -1;
    }
    sleep(1);
    memset(ReadBuffer,'\0',COM_MAX_BUFFER);
    rCount = com_read( &modem->serialport,ReadBuffer,COM_MAX_BUFFER-1);
    printf_data( "dce_send", (char *)ReadBuffer, rCount);

    unsigned char * pRead = &ReadBuffer[rCount -1];
    while(pRead > ReadBuffer && *pRead != '\0')
        pRead--;
    if (*pRead == '\0')
        pRead++;
    if (strstr((char *)pRead,"ERROR") != 0)
        return -3;
    if (strstr((char *)pRead,"OK") != 0)
        return 0;
    for (i=0;i<5;i++) {
        ssize_t rCount = 0;
        sleep(1);
        memset(ReadBuffer,'\0',COM_MAX_BUFFER);
        rCount = com_read( &modem->serialport,ReadBuffer,COM_MAX_BUFFER-1);
        pRead = &ReadBuffer[rCount -1];
        while(pRead > ReadBuffer && *pRead != '\0')
            pRead--;
        if (*pRead == '\0')
            pRead++;
        if (strstr((char *)pRead,"ERROR") != 0)
            return -3;
        if (strstr((char *)pRead,"OK") != 0)
            return 0;
        printf_data( "ReadBuffer", (char *)ReadBuffer, rCount);
    }
    sleep(2);
    return 0;
}


void printf_data(const char *exp, const char *attext, int size)
{
    int i=0;
    char  buff[4096];
    char *p = (char*)attext;
    char * pbuff;
    int  isize = 4096;
    char log_msg[256];

    int len;
    pbuff = buff;
    for(i=0;i<size;i++)
    {
        if(*p == '\x0d')
            len = snprintf(pbuff, isize, "%s", "<CR>");
        else if(*p == '\x0a')
            len = snprintf(pbuff, isize, "%s", "<LF>");
        else if(*p == '\x00')
            len = snprintf(pbuff, isize, "%s", "{00}");
        else if(*p == '\x1a')
            len = snprintf(pbuff, isize, "%s", "<ctrl-Z>");
        else if(*p == '\x1b')
            len = snprintf( pbuff, isize, "<ESC>");
        else if(*p >= 0x20 && *p <= 0x7e)
            len = snprintf( pbuff, isize, "%c",*p & 0xff);
        else
        {
            len = snprintf( pbuff, isize, "{0x%2.2x}",*p & 0xff);
        }
        pbuff += len;
        isize -= len;
        p++;
    }
    *pbuff = '\0';
    sprintf(log_msg, "%s(%d):{%s}", exp, size, buff);
    LogInfo(log_msg);
}
