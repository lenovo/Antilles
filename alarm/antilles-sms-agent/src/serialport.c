/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

#include <Python.h>
#include <sys/ioctl.h>
#include <fcntl.h>   // file control defination
#include <termios.h> // PPSIX terminal control defination

#include "pysms.h"
#include "serialport.h"

int com_open(lptype_serialport lp_serialport) {
    char log_msg[256];

    if (lp_serialport == NULL || lp_serialport == (lptype_serialport)-1)
        return -1;
    if (lp_serialport->portname == NULL || lp_serialport->portname == (char *)-1)
        return -1;

    int fd = open(lp_serialport->portname, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (-1 == fd) {
        sprintf(log_msg, "cannot open serialport %s. %s:%d", lp_serialport->portname, __FILE__, __LINE__);
        LogErr(log_msg);
        return -1;
    }

    if (-1 == com_setioblockflag(fd, BLOCK_IO)) {
        sprintf(log_msg, "IO set error!. %s:%d", __FILE__, __LINE__);
        LogErr(log_msg);
        return -1;
    }
    lp_serialport->fd = fd;

    sprintf(log_msg, "open serial port %s. %s:%d", lp_serialport->portname, __FILE__, __LINE__);
    LogInfo(log_msg);
    return 0;
}

int com_close(lptype_serialport lp_serialport) {
    char log_msg[256];

    if (lp_serialport == NULL || lp_serialport == (lptype_serialport)-1)
        return -1;
    if (lp_serialport->fd < 0)
        return -1;
    if (lp_serialport->fd == 0)
        return 0;
    if (close(lp_serialport->fd) == -1)
        return -1;
    lp_serialport->fd = 0;
    sprintf(log_msg, "close serial port %s. %s:%d", lp_serialport->portname, __FILE__, __LINE__);
    LogInfo(log_msg);
    return 0;
}

int com_setioblockflag(int fd, int value) {
    int oldflags;
    // int result;
    char log_msg[256];

    if (-1 == fd) {
        return -1;
    }
    oldflags = fcntl(fd, F_GETFL,0);

    if (-1 == oldflags) {
        sprintf(log_msg, "get IO flag error. %s:%d", __FILE__, __LINE__);
        LogErr(log_msg);
        return -1;
    }

    if (value == BLOCK_IO)
        oldflags &= ~O_NONBLOCK;
    else
        oldflags |= O_NONBLOCK;

    return fcntl(fd, F_SETFL, oldflags);
}

int com_getinquebytecount(int fd,int *bytecount) {
    int bytes = 0;

    if (-1 == fd) {
        return -1;
    }

    if (ioctl(fd, FIONREAD, &bytes) != -1) {
        *bytecount = bytes;
        return 0;
    }

    return -1;
}

int com_setup(lptype_serialport lp_serialport) {
    struct termios options;

    if (-1 == lp_serialport->fd)
        return -1;

    if (-1 == tcgetattr(lp_serialport->fd, &options))
        return -1;

    switch (lp_serialport->speed) {
    case 300:
        options.c_cflag = B300;
        break;
    case 600:
        options.c_cflag = B600;
        break;
    case 1200:
        options.c_cflag = B1200;
        break;
    case 2400:
        options.c_cflag = B2400;
        break;
    case 4800:
        options.c_cflag = B4800;
        break;
    case 9600:
        options.c_cflag = B9600;
        break;
    case 19200:
        options.c_cflag = B19200;
        break;
    case 38400:
        options.c_cflag = B38400;
        break;
    case 57600:
        options.c_cflag = B57600;
        break;
    case 115200:
        options.c_cflag = B115200;
        break;
    default:
        options.c_cflag = B19200;
        break;
    }

    switch (lp_serialport->databits) {
    case 5:
        options.c_cflag &= ~CSIZE;
        options.c_cflag |= CS5;
        break;
    case 6:
        options.c_cflag &= ~CSIZE;
        options.c_cflag |= CS6;
        break;
    case 7:
        options.c_cflag &= ~CSIZE;
        options.c_cflag |= CS7;
        break;
    case 8:
        options.c_cflag &= ~CSIZE;
        options.c_cflag |= CS8;
        break;
    default:
        options.c_cflag &= ~CSIZE;
        options.c_cflag |= CS8;
        break;
    }

    switch (lp_serialport->parity) {  //取得奇偶校验
    case 'n':
    case 'N':
        options.c_cflag &= ~PARENB;              // 无奇偶效验
        options.c_iflag &= ~(INPCK  | ISTRIP);   // 禁用输入奇偶效验
        options.c_iflag |= IGNPAR;               // 忽略奇偶效验错误
        break;
    case 'o':
    case 'O':
        options.c_cflag |= (PARENB | PARODD);    // 启用奇偶效验且设置为奇效验
        options.c_iflag |= (INPCK  | ISTRIP);    // 启用奇偶效验检查并从接收字符串中脱去奇偶校验位
        options.c_iflag &= ~IGNPAR;              // 不忽略奇偶效验错误
        break;
    case 'e':
    case 'E':
        options.c_cflag |= PARENB;               // 启用奇偶效验
        options.c_cflag &= ~PARODD;              // 设置为偶效验
        options.c_iflag |= (INPCK  | ISTRIP);    // 启用奇偶效验检查并从接收字符串中脱去奇偶校验位
        options.c_iflag &= ~IGNPAR;              // 不忽略奇偶效验错误
        break;
    case 'S':
    case 's':  /*as no parity*/
        options.c_cflag &= ~PARENB;              // 无奇偶效验
        options.c_cflag &= ~CSTOPB;
        options.c_iflag &= ~(INPCK  | ISTRIP);   // 禁用输入奇偶效验
        options.c_iflag |= IGNPAR;               // 忽略奇偶效验错误
        break;
    default:
        options.c_cflag &= ~PARENB;              // 无奇偶效验
        options.c_iflag &= ~(INPCK  | ISTRIP);   // 禁用输入奇偶效验
        options.c_iflag |= IGNPAR;               // 忽略奇偶效验错误
        break;
    }

    switch (lp_serialport->stopbits) {  //取得停止位个数
    case 1:
        options.c_cflag &= ~CSTOPB;               // 一个停止位
        break;
    case 2:
        options.c_cflag |= CSTOPB;                // 2个停止位
        break;
    default:
        options.c_cflag &= ~CSTOPB;               // 默认一个停止位
        break;
    }

    switch (lp_serialport->flow) {  //取得流控制
    case 0:
        options.c_cflag &= ~CRTSCTS;                // 停用硬件流控制
        options.c_iflag &= ~(IXON | IXOFF | IXANY); // 停用软件流控制
        options.c_cflag |= CLOCAL;                  // 不使用流控制
        break;
    case 1:
        options.c_cflag &= ~CRTSCTS;                // 停用硬件流控制
        options.c_cflag &= ~CLOCAL;                 // 使用流控制
        options.c_iflag |= (IXON | IXOFF | IXANY);  // 使用软件流控制
        break;
    case 2:
        options.c_cflag &= ~CLOCAL;                 // 使用流控制
        options.c_iflag &= ~(IXON | IXOFF | IXANY); // 停用软件流控制
        options.c_cflag |= CRTSCTS;                 // 使用硬件流控制
        break;
    default:
        options.c_cflag &= ~CRTSCTS;                // 停用硬件流控制
        options.c_iflag &= ~(IXON | IXOFF | IXANY); // 停用软件流控制
        options.c_cflag |= CLOCAL;                  // 不使用流控制
        break;
    }

    options.c_cflag |= CREAD;                     // 启用接收器
    options.c_iflag |= IGNBRK;                    // 忽略输入行的终止条件
    options.c_oflag = 0;                          // 非加工方式输出
    options.c_lflag = 0;                          // 非加工方式
    //options.c_lflag     &= ~(ICANON | ECHO | ECHOE | ISIG);
    //options.c_oflag     &= ~OPOST;
    //如果串口输入队列没有数据，程序将在read调用处阻塞
    options.c_cc[VMIN]  = 1;
    options.c_cc[VTIME] = 0;

    if(tcsetattr(lp_serialport->fd, TCSANOW, &options) == -1)    // 保存配置并立刻生效
        return -1;

    //清空串口输入输出队列
    tcflush(lp_serialport->fd, TCOFLUSH);
    tcflush(lp_serialport->fd, TCIFLUSH);

    return 0;
}

ssize_t com_read(lptype_serialport lp_serialport, unsigned char *readbuffer, ssize_t readsize) {
    char log_msg[256];

    ssize_t rcount = 0;
    ssize_t dwbytesread = 0;
    int inquebytecount = 0;

    if (lp_serialport->fd < 0) {
        sprintf(log_msg, "file description is not valid. %s:%d", __FILE__, __LINE__);
        LogErr(log_msg);
        return -1;
    }

    if (readbuffer == NULL) {
        sprintf(log_msg, "read buf is NULL. %s:%d", __FILE__, __LINE__);
        LogErr(log_msg);
        return -1;
    }

    if (readsize > COM_MAX_BUFFER)
        dwbytesread = COM_MAX_BUFFER;
    else
        dwbytesread = readsize;

    memset(readbuffer, '\0', dwbytesread);

    if (com_getinquebytecount(lp_serialport->fd, &inquebytecount) != -1) {
        dwbytesread = UART_MIN(dwbytesread, inquebytecount);
    }

    if (!dwbytesread)
        return -1;

    rcount = read(lp_serialport->fd, readbuffer, dwbytesread);
    if (rcount < 0) {
        sprintf(log_msg, "read error. %s:%d", __FILE__, __LINE__);
        LogErr(log_msg);
        return -1;
    }

    return rcount;
}

ssize_t com_write(lptype_serialport lp_serialport, unsigned char *writebuffer, ssize_t writesize) {
    char log_msg[256];

    ssize_t wcount = 0;
    ssize_t dwbyteswrite = writesize;

    if (lp_serialport->fd < 0) {
        sprintf(log_msg, "file description is not valid. %s:%d", __FILE__, __LINE__);
        LogErr(log_msg);
        return -1;
    }

    if ((dwbyteswrite > COM_MAX_BUFFER) || (!dwbyteswrite))
        return -1;

    wcount = write(lp_serialport->fd, writebuffer, dwbyteswrite);
    if (wcount < 0) {
        sprintf(log_msg, "write error. %s:%d", __FILE__, __LINE__);
        LogErr(log_msg);
        return -1;
    }
    while (-1 == tcdrain(lp_serialport->fd));
    return wcount;
}
