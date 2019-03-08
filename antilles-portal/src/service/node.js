/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import TableDataFetcherFactory from '../common/table-data-fetcher-factory'
import ErrorHandler from '../common/error-handler'
import AlarmPolicyService from './alarm-policy'
import GPUService from './gpu'

const NodeStatusEnums = ['off', 'idle', 'used', 'busy'];
const NodePowerStatusEnums = ['on', 'off'];
const NodeType = ['head', 'login', 'compute', 'io'];

class NodeLocation {
  constructor() {
    this.slot = 0;
    this.height = 0;
    this.width = 0;
    this.rackId = 0;
    this.chassisId = 0;
  }
  static parseFromRestApi(jsonObj) {
    let location = new NodeLocation();
    location.slot = jsonObj.u;
    location.height = parseInt(jsonObj.height);
    location.width = parseFloat(jsonObj.width);
    location.rackId = jsonObj.rack_id;
    location.chassisId = jsonObj.chassis_id;
  }
  get slot() {
    return this._slot;
  }
  set slot(slot) {
   this._slot = slot;
  }
  get height() {
    return this._height;
  }
  set height(height) {
   this._height = height;
  }
  get width() {
    return this._width;
  }
  set width(width) {
   this._width = width;
  }
  get rackId() {
    return this._rackId;
  }
  set rackId(rackId) {
   this._rackId = rackId;
  }
  get chassisId() {
    return this._chassisId;
  }
  set chassisId(chassisId) {
   this._chassisId = chassisId;
  }
}

class Gpu {
  constructor() {
    this.index = 0;
    this.type = '';
    this.used = false;
  }
  get index() {
    return this._index;
  }
  set index(index) {
    this._index = index;
  }
  get type() {
    return this._type;
  }
  set type(type) {
    this._type = type;
  }
  get used() {
    return this._used;
  }
  set used(used) {
    this._used = used;
  }
}

class Node {
  constructor() {
    this.id = 0;
    this.hostname = '';
    this.status = '';
    this.powerStatus = '';
    this.type = '';
    this.osIP = '';
    this.bmcIP = '';
    this.machineType = '';
    this.frontImageUrl = '';
    this.groups = [];
    this.cpuUsed = 0.0;
    this.cpuTotal = 0;
    this.ramUsed = 0;
    this.ramTotal = 0;
    this.diskUsed = 0;
    this.diskTotal = 0;
    this.alarmPolicyLevel = '';
    this.location = new NodeLocation();
    this.gpus = [];
  }
  static parseFromRestApi(jsonObj){
    let node = new Node();
    node.id = jsonObj.id;
    node.hostname = jsonObj.hostname;
    node.status = jsonObj.status.toLowerCase()=='used'?'busy':jsonObj.status.toLowerCase();
    node.powerStatus = jsonObj.power_status.toLowerCase();
    node.type = jsonObj.type.toLowerCase();
    node.osIP = jsonObj.mgt_ipv4;
    node.bmcIP = jsonObj.bmc_ipv4;
    node.machineType = jsonObj.machinetype;
    node.frontImageUrl = jsonObj.frontimage;
    node.groups = jsonObj.groups;
    node.cpuUsed = 0.0;
    node.cpuTotal = jsonObj.processors_total;
    node.ramUsed = jsonObj.memory_used * 1024;
    node.ramTotal = jsonObj.memory_total * 1024;
    node.diskUsed = jsonObj.disk_used * 1024 * 1024 * 1024;
    node.diskTotal = jsonObj.disk_total * 1024 * 1024 * 1024;
    node.alarmPolicyLevel = jsonObj.alarm_level == null ? null : AlarmPolicyService.AlarmLevelToParse[String(jsonObj.alarm_level)];
    node.location = jsonObj.location?NodeLocation.parseFromRestApi(jsonObj.location):'';
    node.gpus = [];
    if(jsonObj.gpus) {
      for(var i=0; i<jsonObj.gpus.type.length; i++) {
        var gpu = new Gpu();
        gpu.index = i;
        gpu.type = jsonObj.gpus.type[i];
        gpu.used = jsonObj.gpus.used[i] == 1 ? true : false;
        node.gpus.push(gpu);
      }
    }
    return node;
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
  get status() {
    return this._status;
  }
  set status(status) {
   this._status = status;
  }
  get powerStatus() {
    return this._powerStatus;
  }
  set powerStatus(powerStatus) {
   this._powerStatus = powerStatus;
  }
  get type() {
    return this._type;
  }
  set type(type) {
   this._type = type;
  }
  get osIP() {
    return this._osIP;
  }
  set osIP(osIP) {
   this._osIP = osIP;
  }
  get bmcIP() {
    return this._bmcIP;
  }
  set bmcIP(bmcIP) {
   this._bmcIP = bmcIP;
  }
  get machineType() {
    return this._machineType;
  }
  set machineType(machineType) {
   this._machineType = machineType;
  }
  get frontImageUrl() {
    return this._frontImageUrl;
  }
  set frontImageUrl(frontImageUrl) {
   this._frontImageUrl = frontImageUrl;
  }
  get groups() {
    return this._groups;
  }
  set groups(groups) {
   this._groups = groups;
  }
  get cpuUsed() {
    return this._cpuUsed;
  }
  set cpuUsed(cpuUsed) {
   this._cpuUsed = cpuUsed;
  }
  get cpuTotal() {
    return this._cpuTotal;
  }
  set cpuTotal(cpuTotal) {
   this._cpuTotal = cpuTotal;
  }
  get ramUsed() {
    return this._ramUsed;
  }
  set ramUsed(ramUsed) {
   this._ramUsed = ramUsed;
  }
  get ramTotal() {
    return this._ramTotal;
  }
  set ramTotal(ramTotal) {
   this._ramTotal = ramTotal;
  }
  get diskUsed() {
    return this._diskUsed;
  }
  set diskUsed(diskUsed) {
   this._diskUsed = diskUsed;
  }
  get diskTotal() {
    return this._diskTotal;
  }
  set diskTotal(diskTotal) {
   this._diskTotal = diskTotal;
  }
  get alarmPolicyLevel() {
    return this._alarmPolicyLevel;
  }
  set alarmPolicyLevel(alarmPolicyLevel) {
   this._alarmPolicyLevel = alarmPolicyLevel;
  }
  get location() {
    return this._location;
  }
  set location(location) {
   this._location = location;
  }
  get gpuUsed() {
    return this._gpuUsed;
  }
  set gpuUsed(gpuUsed) {
   this._gpuUsed = gpuUsed;
  }
  get gpuTotal() {
    return this._gpuTotal;
  }
  set gpuTotal(gpuTotal) {
   this._gpuTotal = gpuTotal;
  }
  get gpuModel() {
    return this._gpuModel;
  }
  set gpuModel(gpuModel) {
    this._gpuModel = gpuModel;
  }
}

function nodesTableDataParser(res) {
  var nodes = [];
  res.data.forEach((item) => {
    nodes.push(Node.parseFromRestApi(item));
  });
  return {
    offset: res.offset,
    total: res.total,
    data: nodes
  };
}

function nodesRestApiPropMap(prop) {
  if(prop=='powerStatus')
    return 'power_status';
  if(prop=='osIP')
    return 'mgt_ipv4';
  if(prop=='bmcIP')
    return 'bmc_ipv4';
  if(prop=='machineType')
    return 'machinetype';
  if(prop=='cpuTotal')
    return 'processors_total';
  if(prop=='ramUsed')
    return 'memory_used';
  if(prop=='ramTotal')
    return 'memory_total';
  if(prop=='diskUsed')
    return 'disk_used';
  if(prop=='diskTotal')
    return 'disk_total';
  if(prop=='alarmPolicyLevel')
    return 'alarm_level';
  return prop;
}

function getNodesTableDataFetcher() {
  return TableDataFetcherFactory.createRemotePagingFetcher('/api/nodes/', nodesRestApiPropMap, nodesTableDataParser, 'data', 'offset', 'total');
}

function powerOnNode(nodeId, nextDevice) {
  var req = {
    operation: 'turn_on'
  };
  if(nextDevice) {
    req.bootmode = 'uefi';
    req.nextdevice = nextDevice;
    req.persistent = 'False';
  }
  return new Promise((resolve, reject) => {
    Vue.http.put('/api/nodes/'+ nodeId + '/', req).then((res) => {
        resolve(nodeId);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function powerOffNode(nodeId) {
  var req = {
    operation: "turn_off"
  }
  return new Promise((resolve, reject) => {
    Vue.http.put('/api/nodes/'+ nodeId + '/', req).then((res) => {
        resolve(nodeId);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getNodeById(id) {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/nodes/' + id).then((res) => {
      var node = Node.parseFromRestApi(res.body.node);
      resolve(node);
    },(res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

function getAllNodes(type) {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/nodes/nodelist/?type='+type).then((res) => {
      var data = [];
      res.body.nodelist.forEach((node) => {
        data.push({
          hostname: node.name,
          id: node.id
        });
      })
      resolve(data)
    },(res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

function getNodeConsoleServiceUrl(hostname) {
  return '/api/nodes/' + hostname + '/console/sessions/';
}

function getNodeShellServiceUrl(hostname) {
  return '/api/nodes/' + hostname + '/shell/sessions/';
}

export default {
  getNodesTableDataFetcher,
  powerOnNode,
  powerOffNode,
  getNodeById,
  getAllNodes,
  NodeStatusEnums,
  NodePowerStatusEnums,
  NodeType,
  getNodeConsoleServiceUrl,
  getNodeShellServiceUrl
}
