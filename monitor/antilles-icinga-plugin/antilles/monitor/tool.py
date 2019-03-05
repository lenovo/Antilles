# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import argparse
import os
import re
import time
from functools import wraps

# path
cpu_load = '/proc/loadavg'
cpu_dir = '/proc/stat'
memory_dir = '/proc/meminfo'
disk_stat_dir = '/proc/mounts'
network_dir = '/proc/net/dev'
network_vlan_dir = '/proc/net/vlan/'

parser = argparse.ArgumentParser()
try:
    from pynvml import nvmlInit, nvmlShutdown, nvmlDeviceGetCount, \
        nvmlDeviceGetMemoryInfo, nvmlDeviceGetHandleByIndex,\
        nvmlDeviceGetComputeRunningProcesses, nvmlDeviceGetTemperature, \
        NVML_TEMPERATURE_GPU, nvmlDeviceGetUtilizationRates, nvmlDeviceGetName
except Exception:
    pass


def nvidaiDec(func):
    try:
        nvmlInit()
    except Exception:
        pass

    @wraps(func)
    def wrap(*arg, **kwargs):
        try:
            result = func(*arg, **kwargs)
            nvmlShutdown()
        except Exception:
            pass
        else:
            return result

    return wrap


def judgment_vlan():
    if os.path.isdir(network_vlan_dir):
        for path, dirs, files in os.walk(network_vlan_dir):
            return files
    else:
        return 0


def _get_network_result():
    res_list = []

    def read_dir():
        f = open(network_dir, 'r')
        time.sleep(1)
        g = open(network_dir, 'r')
        return f, g

    def get_in_out(obj):
        receive = 0
        transmit = 0
        # Judge and get a list of vlan files
        file_list = judgment_vlan()
        # Remove the first two lines
        net_list = obj.readlines()[2:]
        for net_line in net_list:
            line = net_line.strip()
            if line.startswith('lo') or line.startswith('bond'):
                continue
            judgment = False
            if file_list:
                for file_name in file_list:
                    if line.startswith(file_name):
                        judgment = True
                        break
            if judgment:
                continue
            # ['eth0', '17384789484', '29564973', '0', '0', '0', '0', '0', '0',
            #  '6592672797', '22027141', '0', '0', '0', '0', '0', '0']
            items = line.replace(':', ' ').split()
            receive += int(items[1])
            transmit += int(items[len(items) / 2 + 1])
        res_list.extend([receive, transmit])
        obj.close()
    get_in_out(read_dir()[0])
    get_in_out(read_dir()[1])

    return res_list


def _get_network_info():
    net_list = _get_network_result()
    net_in = net_list[2] - net_list[0]
    net_out = net_list[3] - net_list[1]
    return net_in, net_out


def _get_disk_total():
    disk_total = 0
    disk_free = 0
    dp = open(disk_stat_dir)
    # Deduplicating content through a dictionary
    device_set = set()
    for mount in dp.readlines():
        new_mount = mount
        # Filter the mount path in /proc/mounts
        if not mount.startswith('/dev/') and not mount.startswith('/dev2/') \
                and not mount.startswith('zfs'):
            continue
        # Check the above filtered string again
        mount_list = mount.strip().split()
        if mount_list[2].startswith('smbfs') and mount[0] == '/' and \
                mount[1] == '/':
            continue
        if mount_list[2].startswith('nfs') \
                or mount_list[2].startswith('autofs') \
                or mount_list[2].startswith('gfs') \
                or re.search(r':', mount):
            continue
        i = 1
        # Determine if the items in the string are none
        while i <= 5:
            index = new_mount.strip().find(' ')
            if index == -1:
                break
            else:
                new_mount = new_mount[index+1:]
            i += 1
        if i != 6:
            continue
        if mount_list[3].startswith('ro', 0, 2):
            continue
        if mount_list[0] not in device_set:
            device_set.add(mount_list[0])
            disk_info = os.statvfs(mount_list[1])
            disk_total += \
                1.0 * disk_info.f_bsize * disk_info.f_blocks / (1000 ** 3)
            disk_free += \
                1.0 * disk_info.f_bavail * disk_info.f_bsize / (1000 ** 3)

    return disk_free, disk_total


def _get_disk_info():
    disk_free, disk_total = _get_disk_total()
    disk_used = disk_total - disk_free
    disk_util = 100.0 * disk_used / disk_total
    return disk_total, disk_used, disk_util


def _get_mem_info():
    mem_used_info = ['MemTotal', 'MemFree', 'Cached', 'Buffers']
    mem_dict = {}
    # By parsing the data, the information in mem_used_info is
    # obtained and expressed in the form of a dictionary.
    with open(memory_dir) as f:
        for mem_info in f:
            name = mem_info.strip().split(':')[0]
            if name in mem_used_info:
                size = int(re.search('\d+', mem_info.strip().
                                     split(':')[1]).group())
                mem_dict.setdefault(name, size)
            if len(mem_dict) == 4:
                break
    memory_used = mem_dict['MemTotal'] - mem_dict['MemFree'] - \
        mem_dict['Cached'] - mem_dict['Buffers']
    memory_util = 100.0 * memory_used / mem_dict['MemTotal']
    memory_total = mem_dict['MemTotal']
    return [memory_used, memory_util, memory_total]


def _get_cpu_util():
    def file_object():
        f = open(cpu_dir, 'r')
        return f

    def totoal_time(file_list):
        times = 0
        for cpu_time in map(int, file_list):
            times += cpu_time
        return times
    # /proc/stat:
    # cpu 109362289 22602 36116382 2483059643 133283 0 2404558 360691 0 0
    # The fourth column is the idle time at a time point,
    # and the total time is all accumulated.
    # first_list = ['109361697', '22601', '36116179', '2483048562',
    #  '133283', '0', '2404546', '360685', '0', '0']
    first_list = re.split('\s+', file_object().readline())[1:-1]
    file_object().close()
    time.sleep(0.1)
    last_list = re.split('\s+', file_object().readline())[1:-1]
    file_object().close()
    first_total_time = totoal_time(first_list)
    last_total_time = totoal_time(last_list)
    total_time_slice = last_total_time - first_total_time
    # Get cpu_free in a time slice
    free_time_slice = int(last_list[3]) - int(first_list[3])
    try:
        cpu_util = 100.0 * (total_time_slice - free_time_slice) \
                   / total_time_slice
    except Exception:
        cpu_util = 'error'
    return cpu_util


def _get_cpu_load():
    f = open(cpu_load, 'r')
    load_avg = f.readline().strip().split()[0]
    return float(load_avg)


def _get_cpu_num():
    cpu_num = 0
    f = open(cpu_dir, 'r')
    content = f.readlines()
    f.close()
    for cpu_info in content:
        if re.match('cpu\d+', cpu_info):
            cpu_num += 1
    return cpu_num


def get_network_info():
    net_in, net_out = _get_network_info()
    print('Ok - Network in|network-in=%dB' % net_in)
    print('Ok - Network out|network-out=%dB' % net_out)
    return 0


def get_disk_info():
    disk_total, disk_used, disk_util = _get_disk_info()
    print('Ok - Disk total|disk-total=%dGB' % disk_total)
    print('Ok - Disk used|disk-used=%dGB' % disk_used)
    print('Ok - Disk util|disk-util={0:.1f}%'.format(disk_util))
    return 0


def get_mem_info():
    memory_used, memory_util, memory_total = _get_mem_info()
    print('Ok - Memory used|memory-used=%dKB' % memory_used)
    print('Ok - Memory util|memory-util={0:.1f}%'.format(memory_util))
    print('Ok - Memory total|memory-total=%dKB' % memory_total)
    return 0


def get_cpu_load():
    print('Ok - Cpu load|cpu-load={}'.format(_get_cpu_load()))
    return 0


def get_cpu_util():
    print("Ok - Cpu util|cpu-util={0:.1f}%".format(_get_cpu_util()))
    return 0


def get_cpu_num():
    print("Ok - Cpu Nums|cpu-num=%d" % (_get_cpu_num()))
    return 0


def _get_gpu_num():
    return int(nvmlDeviceGetCount())


def _get_gpu_mem_pct(gpu_device):
    mem_info = nvmlDeviceGetMemoryInfo(gpu_device)
    return round(100 * mem_info.used / float(mem_info.total), 2)\
        if mem_info.total > 0 else 0


def _get_device_id(index):
    return nvmlDeviceGetHandleByIndex(index)


def _get_gpu_process(gpu_device):
    return len(nvmlDeviceGetComputeRunningProcesses(gpu_device))


def _get_gpu_temp(gpu_device):
    return nvmlDeviceGetTemperature(gpu_device, NVML_TEMPERATURE_GPU)


def _get_gpu_type(gpu_device):
    return nvmlDeviceGetName(gpu_device)


def _get_gpu_util(gpu_device):
    return nvmlDeviceGetUtilizationRates(gpu_device).gpu


@nvidaiDec
def get_gpu_util():
    for index in range(_get_gpu_num()):
        print("Ok - Gpu util|gpu-util_{0}={1:.1f}%"
              .format(str(index), _get_gpu_util(_get_device_id(index))))
    return 0


@nvidaiDec
def get_gpu_type():
    for index in range(_get_gpu_num()):
        print("Ok - Gpu type|gpu-type_%s[%s]=%d"
              % (str(index), _get_gpu_type(_get_device_id(index)), index))
    return 0


@nvidaiDec
def get_gpu_mem_pct():
    for index in range(_get_gpu_num()):
        print("Ok - Gpu mem pct|gpu-memory-util_{0}={1:.1f}%"
              .format(index, _get_gpu_mem_pct(_get_device_id(index))))
    return 0


@nvidaiDec
def get_gpu_process():
    for index in range(_get_gpu_num()):
        print("Ok - Gpu process|gpu-process_%d=%d"
              % (index, _get_gpu_process(_get_device_id(index))))
    return 0


@nvidaiDec
def get_gpu_temp():
    for index in range(_get_gpu_num()):
        print("Ok - Gpu temp|gpu-temp_%d=%d"
              % (index, _get_gpu_temp(_get_device_id(index))))
    return 0


@nvidaiDec
def get_gpu_num():
    print("Ok - Gpu Nums|gpu-num=%d" % (_get_gpu_num(),))
    return 0


@nvidaiDec
def get_gpu_use_num():
    i = 0
    for index in range(_get_gpu_num()):
        if _get_gpu_process(_get_device_id(index)):
            i += 1
    print("Ok - Gpu use nums|gpu-used-num=%d;" % (i,))
    return 0


def call_functions(func_dict, *args):
    def call(func):
        for value in func.values():
            value()
    call(func_dict)
    if args:
        for funcs in args:
            call(funcs)
    return 0


def add_argument():
    parser.add_argument('-g', '--gpu', action='store_true',
                        help='''
                                get all gpu information;
                             '''
                        )
    parser.add_argument('-c', '--cpu', action='store_true',
                        help='''
                                get all cpu information;
                             '''
                        )
    parser.add_argument('-m', '--memory', action='store_true',
                        help='''
                                get all memory information;
                             '''
                        )
    parser.add_argument('-d', '--disk', action='store_true',
                        help='''
                                get all disk information;
                            '''
                        )
    parser.add_argument('-n', '--network', action='store_true',
                        help='''
                                get all network information;
                             '''
                        )
    parser.add_argument('-a', '--all', action='store_true',
                        help='''
                                get all monitoring information;
                             '''
                        )


def main():
    function_dict_gpu = {
        'mem_pct': get_gpu_mem_pct,
        'num': get_gpu_num,
        'process': get_gpu_process,
        'temp': get_gpu_temp,
        'type': get_gpu_type,
        'use_num': get_gpu_use_num,
        'util': get_gpu_util
    }
    function_dict_cpu = {
        'util': get_cpu_util,
        'num': get_cpu_num,
        'load-average': get_cpu_load
    }
    function_dict_memory = {
        'info': get_mem_info
    }
    function_dict_disk = {
        'info': get_disk_info
    }
    function_dict_network = {
        'info': get_network_info
    }

    add_argument()
    parser.parse_args()

    args = parser.parse_args()
    if args.all:
        call_functions(function_dict_cpu, function_dict_memory,
                       function_dict_gpu, function_dict_disk,
                       function_dict_network)
    else:
        if args.gpu:
            call_functions(function_dict_gpu)
        if args.memory:
            call_functions(function_dict_memory)
        if args.cpu:
            call_functions(function_dict_cpu)
        if args.disk:
            call_functions(function_dict_disk)
        if args.network:
            call_functions(function_dict_network)
