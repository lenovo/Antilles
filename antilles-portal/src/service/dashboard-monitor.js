/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import Parser from '../common/parser'
import ErrorHandler from '../common/error-handler'
import TableDataFetcherFactory from '../common/table-data-fetcher-factory'
import JobService from './job'
import GPUService from './gpu'
import QueueService from './queue'
import OptlogService from './operation'
import JobTemplateService from './job-template'

function getTemplateEnums() {
  return JobTemplateService.getAllJobTemplates();
}

class Cluster {
  constructor() {
    this.name = '';
    this.shedulerStatus = Boolean;
    this.fileSystemStatus = Boolean;
    this.networkStatus = {};
    this.cpuStatus = {};
    this.memoryStatus = {};
    this.diskStatus = {};
    this.jobStatus = {};
    this.nodeGroupStatus = {};
    this.nodeStatus = {};
    this.gpuStatus = {};
  }
  static parseFromRestApi(jsonObj) {
    var cluster = new Cluster();
    cluster.name = jsonObj.name;
    cluster.shedulerStatus = jsonObj.is_scheduler_workable;
    cluster.fileSystemStatus = jsonObj.is_cluster_fs_workable;
    cluster.networkStatus = jsonObj.throughput;
    cluster.cpuStatus = jsonObj.processors;
    cluster.memoryStatus = jsonObj.memory;
    cluster.diskStatus = jsonObj.diskspace;
    cluster.jobStatus = jsonObj.jobs;
    cluster.nodeGroupStatus = NodeGroupStatus.parseFromRestApi(jsonObj.nodes);
    var state = jsonObj.nodes.state
    cluster.nodeStatus = {
      on:  state.busy.concat(state.idle, state.occupied).reduce(function(a,b){return a+b;}),
      off: state.off.reduce(function(a,b){return a+b;}),
    };
    cluster.gpuStatus = jsonObj.gpu;
    return cluster;
  }
  get name() {
    return this._name;
  }
  set name(name) {
   this._name = name;
  }
  get shedulerStatus() {
    return this._shedulerStatus;
  }
  set shedulerStatus(shedulerStatus) {
   this._shedulerStatus = shedulerStatus;
  }
  get fileSystemStatus() {
    return this._fileSystemStatus;
  }
  set fileSystemStatus(fileSystemStatus) {
   this._fileSystemStatus = fileSystemStatus;
  }
  get networkStatus() {
    return this._networkStatus;
  }
  set networkStatus(networkStatus) {
   this._networkStatus = networkStatus;
  }
  get cpuStatus() {
    return this._cpuStatus;
  }
  set cpuStatus(cpuStatus) {
   this._cpuStatus = cpuStatus;
  }
  get memoryStatus() {
    return this._memoryStatus;
  }
  set memoryStatus(memoryStatus) {
   this._memoryStatus = memoryStatus;
  }
  get diskStatus() {
    return this._diskStatus;
  }
  set diskStatus(diskStatus) {
   this._diskStatus = diskStatus;
  }
  get jobStatus() {
    return this._jobStatus;
  }
  set jobStatus(jobStatus) {
   this._jobStatus = jobStatus;
  }
  get nodeGroupStatus() {
    return this._nodeGroupStatus;
  }
  set nodeGroupStatus(nodeGroupStatus) {
   this._nodeGroupStatus = nodeGroupStatus;
  }
  get nodeStatus() {
    return this._nodeStatus;
  }
  set nodeStatus(nodeStatus) {
   this._nodeStatus = nodeStatus;
  }
  get gpuStatus() {
    return this._gpuStatus;
  }
  set gpuStatus(gpuStatus) {
   this._gpuStatus = gpuStatus;
  }

}

class Status {
  constructor() {
    this.busy = [];
    // this.running = [];
    this.free = [];
    this.off = [];
  }
  static parseFromRestApi(jsonObj) {
    var status = new Status();
    var running = [];
    status.busy = processStatus(jsonObj.busy);
    running = processStatus(jsonObj.occupied);
    status.free = processStatus(jsonObj.idle);
    status.off = processStatus(jsonObj.off);
    for(let i=0;i<status.busy.length;i++) {
      status.busy[i] = status.busy[i] + running[i];
    }
    return status;
  }

  get busy() {
    return this._busy;
  }
  set busy(busy) {
   this._busy = busy;
  }
  get off() {
    return this._off;
  }
  set off(off) {
   this._off = off;
  }
  get free() {
    return this._free;
  }
  set free(free) {
   this._free = free;
  }
  // get running() {
  //   return this._running;
  // }
  // set running(running) {
  //  this._running = running;
  // }
}
class NodeGroupStatus {
  constructor() {
    this.status = new Status;
    this.group = [];
  }

  static parseFromRestApi(jsonObj) {
    var nodeGroupStatus = new NodeGroupStatus();
    nodeGroupStatus.status = Status.parseFromRestApi(jsonObj.state)
    nodeGroupStatus.group = jsonObj.types>4?jsonObj.types.slice(0, 4):jsonObj.types;
    return nodeGroupStatus;
  }

  get status() {
    return this._status;
  }
  set status(status) {
   this._status = status;
  }
  get group() {
    return this._group;
  }
  set group(group) {
   this._group = group;
  }

}

class JobChart {
  constructor() {
    this.running = 0;
    this.waitong = 0;
    this.time = new Date();
    this.timezone = 0;
  }
  static parseFromRestApi(jsonObj) {
    var jobChart = new JobChart();
    jobChart.running = jsonObj.running;
    jobChart.waiting = jsonObj.waiting;
    jobChart.time = new Date(jsonObj.time*1000);
    jobChart.timezone = jsonObj.timezone;
    return jobChart;
  }

  get running() {
    return this._running;
  }
  set running(running) {
   this._running = running;
  }
  get waitong() {
    return this._waitong;
  }
  set waitong(waitong) {
   this._waitong = waitong;
  }
  get time() {
    return this._time;
  }
  set time(time) {
   this._time = time;
  }
  get timezone() {
    return this._timezone;
  }
  set timezone(timezone) {
   this._timezone = timezone;
  }

}



class Template {
  constructor() {
    this.type = '';
    this.counts = 0
  }
  static parseFromRestApi(jsonObj) {
    var template = new Template();
    template.type = jsonObj.type;
    template.counts = jsonObj.counts
    return template;
  }

  get type() {
    return this._type;
  }
  set type(type) {
   this._type = type;
  }
  get counts() {
    return this._counts;
  }
  set counts(counts) {
   this._counts = counts;
  }

}

function processStatus(status) {
  var arr = [];
  status.length==6?status.forEach((item, index) => {
    index == 0?item += status[5]:index == 2?item += status[4]:'';
    index <= 3?arr.push(item):'';
  }):arr = status;
  return arr;
}

function getDashboardOverview() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/cluster-overview/').then((res) => {
      resolve(Cluster.parseFromRestApi(res.body));
      // Add gpu status
      // var overview = Cluster.parseFromRestApi(res.body);
      // GPUService.getClusterGpuStatus().then((res) => {
      //   overview.gpuStatus = res;
      //   resolve(overview);
      // }, (res) => {
      //   reject(res);
      // });
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

function getDashboardJobList(length, status, role) {
  return JobService.getJoblatest(length, status, role);
}

function getDashboardMessages(length) {
  return OptlogService.getOptlogLatest(length);
}

function getJobChartQueue() {
  return QueueService.getAllQueues();
}

function getDashboardJobChart(time, queue, role, iscompleted) {
  return new Promise((resolve, reject) => {
    var status = !iscompleted?'uncompleted':'completed';
    var api = (role=='admin'|| role == 'operator')?'':'user/';
    Vue.http.get('api/jobhistory/'+api+'?duration='+time+'&num_of_points=7&q_name='+ queue + '&status=' + status).then((res) => {
      var jobChart = []
      res.body.forEach((item) => {
        jobChart.push(JobChart.parseFromRestApi(item))
      })
      resolve(jobChart)
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}


function getUserLatestTemplate() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/jobs/template/recent/').then((res) => {
      var templates = [];
      res.body.forEach((item) => {
        templates.push(Template.parseFromRestApi(item))
      })
      resolve(templates.sort(compare('counts')))
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}
var compare = function (prop) {
    return function (x, y) {
        var before = x[prop];
        var after = y[prop];
        if (!isNaN(Number(before)) && !isNaN(Number(after))) {
            before = Number(before);
            after = Number(after);
        }
        if (before < after) {
            return 1;
        } else if (before > after) {
            return -1;
        } else {
            return 0;
        }
    }
}


export default {
  getDashboardOverview,
  getJobChartQueue,
  getDashboardJobChart,
  getDashboardJobList,
  getUserLatestTemplate,
  getDashboardMessages,
  getTemplateEnums
}
