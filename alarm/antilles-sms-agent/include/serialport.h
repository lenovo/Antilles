/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */


#ifndef SERIA_PORT_HEADER_H
#define SERIA_PORT_HEADER_H

#define UART_MIN(A,B)  ((A) < (B) ? (A):(B))
#define COM_MAX_BUFFER   512

#define BLOCK_IO    0
#define NONBLOCK_IO 1

typedef struct STU_DCE_PARAM
{
    char portname[256];
    int  speed;
    int  databits;
    int  stopbits;
    char parity;
    int  flow;
    int  fd;
    int  outtime;
}type_serialport, * lptype_serialport;

int dce_init(lptype_serialport lp_serialport);
int com_open(lptype_serialport lp_serialport);
int com_close(lptype_serialport lp_serialport);
int com_setioblockflag(int fd, int value);

int com_getinquebytecount(int fd,int *bytecount);
int com_setup(lptype_serialport lp_serialport);
ssize_t com_read(lptype_serialport lp_serialport, unsigned char *readbuffer, ssize_t readsize);
ssize_t com_write(lptype_serialport lp_serialport, unsigned char *writebuffer, ssize_t writesize); 


#endif /* SERIA_PORT_HEADER_H */