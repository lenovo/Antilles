/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import Parser from '../common/parser'
import ErrorHandler from '../common/error-handler'
import Format from "../common/format"

const DataCategoryEnums = ['load', 'cpu', 'ram', 'disk', 'network', 'energy', 'temperature', 'job'];
const HeatDataCategoryEnums = ['load', 'cpu', 'ram', 'disk', 'network', 'energy', 'temperature', 'job'];

const DataDigitMap = {
  'load': 2,
  'util': 1,
  'cpu': 1,
  'ram': 1,
  'disk': 1,
  'energy': 0,
  'temperature': 0,
  'network': 1,
  'job': 0
}

const unitEnums = {
  cpu: '%',
  ram: '%',
  disk: '%',
  temperature: '℃',
  network: 'MB/s',
  energy: 'W',
  load: '',
  job: ''
}

class ServiceStatus {
  constructor() {
    this.shedulerStatus = '';
    this.fileSystemStatus = '';
  }
  static parseFromRestApi(jsonObj) {
    var serviceStatus = new ServiceStatus();
    serviceStatus.shedulerStatus = jsonObj.scheduler_status;
    serviceStatus.fileSystemStatus = jsonObj.shared_storage_status;
    return serviceStatus;
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
}

class TimeSeriesItem {
  constructor() {
    this.time = new Date(0);
    this.values = [];
  }
  static parseFromRestApi(jsonObj, category) {
    var item = new TimeSeriesItem();
    item.time = new Date(jsonObj.time * 1000);
    if(typeof(jsonObj.value) == 'string') {
      var valStrs = jsonObj.value.split(',');
      valStrs.forEach((valStr) => {
        item.values.push(Format.formatNumber(Number(valStr), DataDigitMap[category]));
      });
    } else if(typeof(jsonObj.value) == 'number') {
      item.values.push(Format.formatNumber(jsonObj.value, DataDigitMap[category]));
    } else {
      item.values.push('-')
      // console.log('Invalid value type');
    }
    return item;
  }
  get time() {
    return this._time;
  }
  set time(time) {
   this._time = time;
  }
  get values() {
    return this._values;
  }
  set values(values) {
   this._values = values;
  }
}

class Heat{
  constructor(){
    this.id = 0;
    this.hostname = "";
    this.value = 0;
  }
  static parseFromRestApi(obj){
    let heat = new Heat();
    heat.id = obj.id;
    heat.hostname = obj.hostname;
    if(obj.value != null) {
      heat.value = parseInt(obj.value);
    } else {
      heat.value = null;
    }
    return heat;
  }
  get id() {
    return this._id;
  }
  set id(id) {
    this._id = id;
  }
  get hostname() {
    return this._hostname;
  }
  set hostname(hostname) {
    this._hostname = hostname;
  }
  get value() {
    return this._value;
  }
  set value(value) {
    this._value = value;
  }
}

class NodeGpuHeat {
  constructor() {
    this.id = '';
    this.hostname = '';
    this.values = [];
    this.used = [];
  }
  static parseFromRestApi(jsonObj) {
    let heat = new NodeGpuHeat();
    heat.id = jsonObj.id;
    heat.hostname = jsonObj.hostname;
    heat.values = jsonObj.value;
    heat.used = jsonObj.used;
    return heat;
  }
  get id() {
    return this._id;
  }
  set id(id) {
   this._id = id;
  }
  get hostname() {
    return this._hostname;
  }
  set hostname(hostname) {
   this._hostname = hostname;
  }
  get values() {
    return this._values;
  }
  set values(values) {
   this._values = values;
  }
  get used() {
    return this._used;
  }
  set used(used) {
   this._used = used;
  }
}

function getRestApiCategory(category) {
  if (category == 'cpu') {
    return 'cpu';
  }
  if (category == 'ram') {
    return 'memory';
  }
  if (category == 'disk') {
    return 'disk';
  }
  if (category == 'network') {
    return 'network';
  }
  if (category == 'temperature') {
    return 'temperature';
  }
  if (category == 'load') {
    return 'load';
  }
  if (category == 'energy') {
    return 'energy';
  }
  if (category == 'job') {
    return 'job';
  }
  if (category == 'util') {
    return 'util';
  }
}

function makeTimeSeries(current, history, category) {
  var series = [];
  history.forEach((item) => {
    series.push(TimeSeriesItem.parseFromRestApi(item, category));
  });
  if(current){
    var currentItem = {
      value: current,
      time: Math.round(new Date().getTime() / 1000)
    }
    series.push(TimeSeriesItem.parseFromRestApi(currentItem, category));
  }
  return series;
}

function getLatestData(sourceType, sourceId, category, timeUnit, timeCount, startTime) {
  return new Promise((resolve, reject) => {
    var req = {};
    var url = "";
    if(sourceType == 'nodegpus') {
      var temp = sourceId.split(':');
      var nodeId = temp[0];
      var gpuIndex = temp[1].substring(3, temp[1].length);
      url = '/api/nodes/' + nodeId + '/gpu/' + gpuIndex;
    } else {
      url = '/api/' + sourceType + '/' + sourceId;
    }
    if(startTime) {
      let timeStamp = Date.parse(startTime) / 1000;
      url = url + '/tendency/' + timeUnit + '/' + getRestApiCategory(category) + '/?starttime=' + timeStamp
    } else {
      url = url + '/tendency/' + timeUnit + '/' + getRestApiCategory(category) + '/';
    }
    Vue.http.get(url, req).then((res) => {
        var timeSeries = makeTimeSeries(res.body.current, res.body.history, category);

        resolve({
          id: sourceId,
          data: timeSeries,
          current: res.body.current
        });
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getGroupHeatData(groupId, dataCategory) {
  let _url = "/api/nodegroups/" + groupId + "/heat/latest/" + getRestApiCategory(dataCategory) + "/";
  return new Promise((resolve, reject) => {
    let req = "";
    Vue.http.get(_url, req).then((res) => {
      let heats = [];
      res.body.heat.map((item) => {
        heats.push(Heat.parseFromRestApi(item));
      });
      resolve({
        data: heats
      });
    }, (res) => {
      reject(res);
    })
  })
}

function getNodeDataByHour(nodeId, category, latestHours) {
  return getLatestData('nodes', nodeId, category, 'hour', latestHours);
}

function getNodeDataByDay(nodeId, category, latestDays) {
  return getLatestData('nodes', nodeId, category, 'day', latestDays);
}

function getNodeDataByWeek(nodeId, category, latestWeeks) {
  return getLatestData('nodes', nodeId, category, 'week', latestWeeks);
}

function getNodeDataByMonth(nodeId, category, latestMonths) {
  return getLatestData('nodes', nodeId, category, 'month', latestMonths);
}

function getNodeGroupDataByHour(nodeGroupId, category, latestHours, startTime) {
  return getLatestData('nodegroups', nodeGroupId, category, 'hour', latestHours, startTime);
}

function getNodeGroupDataByDay(nodeGroupId, category, latestDays, startTime) {
  return getLatestData('nodegroups', nodeGroupId, category, 'day', latestDays, startTime);
}

function getNodeGroupDataByWeek(nodeGroupId, category, latestWeeks, startTime) {
  return getLatestData('nodegroups', nodeGroupId, category, 'week', latestWeeks, startTime);
}

function getNodeGroupDataByMonth(nodeGroupId, category, latestMonths, startTime) {
  return getLatestData('nodegroups', nodeGroupId, category, 'month', latestMonths, startTime);
}

function getNodeGpuDataByHour(nodeId, gpuIndex, category, latestHours) {
  return getLatestData('nodegpus', nodeId+":gpu"+gpuIndex, category, 'hour', latestHours);
}

function getNodeGpuDataByDay(nodeId, gpuIndex, category, latestDays) {
  return getLatestData('nodegpus', nodeId+":gpu"+gpuIndex, category, 'day', latestDays);
}

function getNodeGpuDataByWeek(nodeId, gpuIndex, category, latestWeeks) {
  return getLatestData('nodegpus', nodeId+":gpu"+gpuIndex, category, 'week', latestWeeks);
}

function getNodeGpuDataByMonth(nodeId, gpuIndex, category, latestMonths) {
  return getLatestData('nodegpus', nodeId+":gpu"+gpuIndex, category, 'month', latestMonths);
}

function getNodeGpuDataByGroup(groupId, category, offset) {
  return new Promise((resolve, reject) => {
    var size = offset.pageSize;
    var current = offset.currentPage;
    var api = `/api/nodegroups/${groupId}/gpu/heat/latest/${category}/?offset=${size}&currentPage=${current}`;
    Vue.http.get(api).then((res) => {
      var nodesGpus = [];
      res.body.nodes.forEach((nodeGpus) => {
        nodesGpus.push(NodeGpuHeat.parseFromRestApi(nodeGpus));
      });
      resolve({
        pageSize: res.body.offset,
        currentPage: res.body.currentPage,
        total: res.body.total,
        nodesGpus: nodesGpus
      });
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

function getNodeGpuDataByJob(jobId, category, offset) {
  return new Promise((resolve, reject) => {
    var size = offset.pageSize;
    var current = offset.currentPage;
    var api = `/api/jobs/${jobId}/gpu/heat/latest/${category}/?offset=${size}&currentPage=${current}`;
    Vue.http.get(api).then((res) => {
      var nodesGpus = [];
      res.body.nodes.forEach((nodeGpus) => {
        nodesGpus.push(NodeGpuHeat.parseFromRestApi(nodeGpus));
      });
      resolve({
        pageSize: res.body.offset,
        currentPage: res.body.currentPage,
        total: res.body.total,
        nodesGpus: nodesGpus
      });
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

function getServiceStatus() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/cluster/service-overview/').then((res) => {
      resolve(ServiceStatus.parseFromRestApi(res.body));
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

export default {
  DataCategoryEnums,
  HeatDataCategoryEnums,
  unitEnums,
  getServiceStatus,
  getGroupHeatData,
  getNodeDataByHour,
  getNodeDataByDay,
  getNodeDataByWeek,
  getNodeDataByMonth,
  getNodeGroupDataByHour,
  getNodeGroupDataByDay,
  getNodeGroupDataByWeek,
  getNodeGroupDataByMonth,
  getNodeGpuDataByGroup,
  getNodeGpuDataByJob,
  getNodeGpuDataByHour,
  getNodeGpuDataByDay,
  getNodeGpuDataByWeek,
  getNodeGpuDataByMonth
}
