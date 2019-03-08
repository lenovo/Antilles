/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import ErrorHandler from '../common/error-handler'

let RackDefines = [];

class RackLocation {
  constructor() {
    this.rowIndex = 0;
    this.colIndex = 0;
  }
  static parseFromRestApi(jsonObj){
    let location = new RackLocation()
    location.rowIndex = jsonObj.row_index;
    location.colIndex = jsonObj.col_index;
    return location;
  }
  get rowIndex() {
    return this._rowIndex;
  }
  set rowIndex(rowIndex) {
   this._rowIndex = rowIndex;
  }
  get colIndex() {
    return this._colIndex;
  }
  set colIndex(colIndex) {
   this._colIndex = colIndex;
  }

}
class ChassisLocation {
  constructor() {
    this.rackId = 0;
    this.u = 0;
  }
  static parseFromRestApi(jsonObj) {
    let location = new ChassisLocation();
    location.rackId = jsonObj.rack_id;
    location.u = jsonObj.u;
    return location;
  }
  get rackId() {
    return this._rackId;
  }
  set rackId(rackId) {
   this._rackId = rackId;
  }
  get u() {
    return this._u;
  }
  set u(u) {
   this._u = u;
  }
}
class NodeLocation {
  constructor() {
    this.u = 0;
    this.height = 0;
    this.width = 0;
    this.rackId = 0;
    this.chassisId = 0;
  }
  static parseFromRestApi(jsonObj) {
    let location = new NodeLocation();
    location.u = jsonObj.u;
    location.height = jsonObj.height? parseInt(jsonObj.height) : 0;
    location.width = jsonObj.width? parseFloat(jsonObj.width) : 0;
    location.rackId = jsonObj.rack_id;
    location.chassisId = jsonObj.chassis_id;
    return location;
  }
  get u() {
    return this._u;
  }
  set u(u) {
   this._u = u;
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
class Chassis {
  constructor() {
    this.id = 0;
    this.name = '';
    this.frontimage = '';
    this.machinetype = '';
    this.location = new ChassisLocation();
  }
  static parseFromRestApi(jsonObj) {
    var chassis = new Chassis();
    chassis.id = jsonObj.id;
    chassis.name = jsonObj.name;
    chassis.machinetype = jsonObj.machinetype;
    chassis.location = ChassisLocation.parseFromRestApi(jsonObj.location);
    fillRackDefine(chassis, getRackDefineById('chassis', jsonObj.machinetype));
    return chassis;
  }
  get id() {
    return this._id;
  }
  set id(id) {
   this._id = id;
  }
  get name() {
    return this._name;
  }
  set name(name) {
   this._name = name;
  }
  get frontimage() {
    return this._frontimage;
  }
  set frontimage(frontimage) {
   this._frontimage = frontimage;
  }
  get machinetype() {
    return this._machinetype;
  }
  set machinetype(machinetype) {
   this._machinetype = machinetype;
  }
  get location() {
    return this._location;
  }
  set location(location) {
   this._location = location;
  }


}
class Switch {
  constructor() {
    this.id = 0;
    this.hostname = '';
    this.frontimage = '';
    this.machinetype = '';
    this.status = '';
    this.location = new NodeLocation();
  }
  static parseFromRestApi(jsonObj) {
    var rackswitch = new Switch();
    rackswitch.id = jsonObj.id;
    rackswitch.hostname = jsonObj.hostname;
    rackswitch.machinetype = jsonObj.machinetype;
    rackswitch.status = jsonObj.power_status;
    rackswitch.location = NodeLocation.parseFromRestApi(jsonObj.location);
    fillRackDefine(rackswitch, getRackDefineById('switch', jsonObj.machinetype));
    return rackswitch;
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
  get frontimage() {
    return this._frontimage;
  }
  set frontimage(frontimage) {
   this._frontimage = frontimage;
  }
  get machinetype() {
    return this._machinetype;
  }
  set machinetype(machinetype) {
   this._machinetype = machinetype;
  }
  get status() {
    return this._status;
  }
  set status(status) {
   this._status = status;
  }
  get location() {
    return this._location;
  }
  set location(location) {
   this._location = location;
  }


}
class Node {
  constructor() {
    this.id = 0;
    this.hostname = '';
    this.status = '';
    this.machinetype = '';
    this.frontimage = '';
    this.location = new NodeLocation();
    this.energy = '';
    this.temperature = '';
    this.network = ',';
    this.load = '';
    this.diskUsed = '';
    this.memoryUsed = '';
    this.cpuUsed = '';
    this.cpuCoreUsed = '';
    this.alarm = null
  }
  static parseFromRestApi(jsonObj){
    let node = new Node();
    node.id = jsonObj.id;
    node.hostname = jsonObj.hostname;
    node.status = jsonObj.power_status;
    node.machinetype = jsonObj.machinetype;
    node.location = NodeLocation.parseFromRestApi(jsonObj.location);
    node.energy = jsonObj.energy;
    node.temperature = jsonObj.temperature;
    node.network = jsonObj.network;
    node.load = jsonObj.load;
    node.diskUsed = jsonObj.disk_usage;
    node.memoryUsed = jsonObj.memory_usage;
    node.cpuUsed = jsonObj.cpu_usage;
    node.cpuCoreUsed = jsonObj.cpu_core_used;
    node.alarm = jsonObj.alarm_level;
    fillRackDefine(node, getRackDefineById('node', jsonObj.machinetype));
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
  get machinetype() {
    return this._machinetype;
  }
  set machinetype(machinetype) {
   this._machinetype = machinetype;
  }
  get frontimage() {
    return this._frontimage;
  }
  set frontimage(frontimage) {
   this._frontimage = frontimage;
  }
  get location() {
    return this._location;
  }
  set location(location) {
   this._location = location;
  }
  get energy() {
    return this._energy;
  }
  set energy(energy) {
   this._energy = energy;
  }
  get temperature() {
    return this._temperature;
  }
  set temperature(temperature) {
   this._temperature = temperature;
  }
  get network() {
    return this._network;
  }
  set network(network) {
   this._network = network;
  }
  get load() {
    return this._load;
  }
  set load(load) {
   this._load = load;
  }
  get diskUsed() {
    return this._diskUsed;
  }
  set diskUsed(diskUsed) {
   this._diskUsed = diskUsed;
  }
  get memoryUsed() {
    return this._memoryUsed;
  }
  set memoryUsed(memoryUsed) {
   this._memoryUsed = memoryUsed;
  }
  get cpuUsed() {
    return this._cpuUsed;
  }
  set cpuUsed(cpuUsed) {
   this._cpuUsed = cpuUsed;
  }
  get cpuCoreUsed() {
    return this._cpuCoreUsed;
  }
  set cpuCoreUsed(cpuCoreUsed) {
   this._cpuCoreUsed = cpuCoreUsed;
  }
  get alarm() {
    return this._alarm;
  }
  set alarm(alarm) {
   this._alarm = alarm;
  }


}
class Rack {
  constructor() {
    this.id = 0;
    this.name = '';
    this.nodeCount = 0;
    this.nodeBusy = 0;
    this.nodeFree = 0;
    this.nodeOff = 0;
    this.nodeUsed = 0;
    this.energy = '';
    this.frontimage = '';
    this.location = new RackLocation();
    this.chassis = [];
    this.switches = [];
    this.nodes = [];
  }
  static parseFromRestApi(jsonObj, rackDefine){
    let rack = new Rack()
    rack.id = jsonObj.id;
    rack.name = jsonObj.name;
    rack.nodeCount = jsonObj.node_num;
    rack.nodeBusy = jsonObj.node_busy;
    rack.nodeFree = jsonObj.node_free;
    rack.nodeOff = jsonObj.node_off;
    rack.nodeUsed = jsonObj.node_used;
    rack.energy = jsonObj.energy;
    rack.location = RackLocation.parseFromRestApi(jsonObj.location)
    fillRackDefine(rack, getRackDefineById('rack', 'rack'));
    jsonObj.nodes.forEach((node) => {
      rack.nodes.push(Node.parseFromRestApi(node))
    })
    jsonObj.switches?jsonObj.switches.forEach((item) => {
      rack.switches.push(Switch.parseFromRestApi(item))
    }):'';
    jsonObj.chassis?jsonObj.chassis.forEach((chassis) => {
      rack.chassis.push(Chassis.parseFromRestApi(chassis))
    }):'';

    return rack;
  }

  get id() {
    return this._id;
  }
  set id(id) {
   this._id = id;
  }
  get name() {
    return this._name;
  }
  set name(name) {
   this._name = name;
  }
  get nodeCount() {
    return this._nodeCount;
  }
  set nodeCount(nodeCount) {
   this._nodeCount = nodeCount;
  }
  get nodeBusy() {
    return this._nodeBusy;
  }
  set nodeBusy(nodeBusy) {
   this._nodeBusy = nodeBusy;
  }
  get nodeFree() {
    return this._nodeFree;
  }
  set nodeFree(nodeFree) {
   this._nodeFree = nodeFree;
  }
  get nodeOff() {
    return this._nodeOff;
  }
  set nodeOff(nodeOff) {
   this._nodeOff = nodeOff;
  }
  get nodeUsed() {
    return this._nodeUsed;
  }
  set nodeUsed(nodeUsed) {
   this._nodeUsed = nodeUsed;
  }
  get energy() {
    return this._energy;
  }
  set energy(energy) {
   this._energy = energy;
  }
  get location() {
    return this._location;
  }
  set location(location) {
   this._location = location;
  }
  get chassis() {
    return this._chassis;
  }
  set chassis(chassis) {
   this._chassis = chassis;
  }
  get switches() {
    return this._switches;
  }
  set switches(switches) {
   this._switches = switches;
  }
  get nodes() {
    return this._nodes;
  }
  set nodes(nodes) {
   this._nodes = nodes;
  }
}

function compareRackByCode(rackDefine, code) {
  if(rackDefine.code == code || (rackDefine.aliasCodes && rackDefine.aliasCodes.indexOf(code) >= 0)) {
    return true;
  }
  return false;
}

function getRackDefineById(type, code) {
  for(var i=0; i<RackDefines.length; i++) {
    if(RackDefines[i].type == type && compareRackByCode(RackDefines[i], code)) {
      return RackDefines[i];
    }
  }
  return null;
}

function fillRackDefine(obj, define) {
  obj.frontimage = define.frontimage;
  obj.padding = define.padding;
  obj.width_height = define.width_height;
  obj.uheight = define.uheight;
  obj.gap = define.gap;
  if(obj.location && define.location) {
    obj.location.width = define.location.width;
    obj.location.height = define.location.height;
  }
  return obj;
}

function getInitRackImageDefine() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/static/data/rack.json').then((res) => {
      RackDefines = eval('(' + res.bodyText + ')');
      resolve(RackDefines);
    }, (res) => {
      reject(res);
    })
  });
}
function getRackById(rackId) {
  return new Promise((resolve, reject) => {
    getInitRackImageDefine().then((res) => {
      Vue.http.get('/api/racks/' + rackId).then((res) => {
        resolve(Rack.parseFromRestApi(res.body.rack));
      },(res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      });
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  })
}
function getAllRacks() {
  return new Promise((resolve, reject) => {
      Vue.http.get('/api/racks/').then((res) => {
        resolve(res.data.racks);
      },(res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      });
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
}
//
// function getRackById(rackId) {
//   return new Promise((resolve, reject) => {
//     Vue.http.get('/static/data/rack.json').then((r) => {
//         RackDefines = eval('(' + r.bodyText + ')');
//         Vue.http.get('/api/racks/' + rackId).then((res) => {
//             resolve(Rack.parseFromRestApi(res.body.rack));
//           },
//           (res) => {
//             ErrorHandler.restApiErrorHandler(res, reject);
//           }
//         );
//       }, (res) => {
//         ErrorHandler.restApiErrorHandler(res, reject);
//       }
//     );
//
//   });
// }

export default {
  getRackById,
  getAllRacks
}
