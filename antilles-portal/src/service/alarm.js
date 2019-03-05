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
import TableDataFetcherFactory from '../common/table-data-fetcher-factory'

const AlarmStatusEnums = ['present', 'confirmed', 'resolved'];

class Alarm {
  constructor() {
    this.id = 0;
    this.policyId = '';
    this.policyName = '';
    this.policyLevel = '';
    this.status = '';
    this.createTime = new Date(0);
    this.nodeId = 0;
    this.nodeName = '';
    this.gpuId = '';
    this.comment = '';
  }
  static parseFromRestApi(jsonObj) {
    var alarm = new Alarm();
    alarm.id = jsonObj.id;
    alarm.policyId = jsonObj.policy__id;
    alarm.policyName = jsonObj.policy__name;
    alarm.policyLevel = jsonObj.policy__level.toLowerCase();
    alarm.status = jsonObj.status.toLowerCase();
    alarm.createTime = Parser.parseTimeFromRestApi(jsonObj.create_time);
    alarm.nodeId = 0;
    alarm.gpuId = jsonObj.gpu_index;
    alarm.nodeName = jsonObj.node;
    alarm.comment = jsonObj.comment;
    return alarm;
  }
  get id() {
    return this._id;
  }
  set id(id) {
   this._id = id;
  }
  get id() {
    return this._id;
  }
  set id(id) {
   this._id = id;
  }
  get policyId() {
    return this._policyId;
  }
  set policyId(policyId) {
   this._policyId = policyId;
  }
  get policyName() {
    return this._policyName;
  }
  set policyName(policyName) {
   this._policyName = policyName;
  }
  get policyLevel() {
    return this._policyLevel;
  }
  set policyLevel(policyLevel) {
   this._policyLevel = policyLevel;
  }
  get status() {
    return this._status;
  }
  set status(status) {
   this._status = status;
  }
  get createTime() {
    return this._createTime;
  }
  set createTime(createTime) {
   this._createTime = createTime;
  }
  get nodeId() {
    return this._nodeId;
  }
  set nodeId(nodeId) {
   this._nodeId = nodeId;
  }
  get nodeName() {
    return this._nodeName;
  }
  set nodeName(nodeName) {
   this._nodeName = nodeName;
  }
  get gpuId() {
    return this._gpuId;
  }
  set gpuId(gpuId) {
   this._gpuId = gpuId;
  }
  get comment() {
    return this._comment;
  }
  set comment(comment) {
   this._comment = comment;
  }
}

class AlarmPrompt {
  constructor() {
    this.count = 0;
    this.isSound = Boolean;
  }

  static parseFromRestApi(jsonObj) {
    var alarmPrompt = new AlarmPrompt();
    alarmPrompt.count = jsonObj.count;
    alarmPrompt.isSound = jsonObj.sound;
    return alarmPrompt;
  }

  get count() {
    return this._count;
  }
  set count(count) {
   this._count = count;
  }
  get isSound() {
    return this._isSound;
  }
  set isSound(isSound) {
   this._isSound = isSound;
  }

}
function buildFilters(idList, statusList, policyLevelList, timeRange) {
  var filters = [];
  if(idList) {
    filters.push({prop: "id", type: "in", values: idList});
  }
  if(statusList) {
    filters.push({prop: "status", type: "in", values: statusList});
  }
  if(policyLevelList) {
    filters.push({prop: "policy__level", type: "in", values: policyLevelList});
  }
  if(timeRange) {
    filters.push({prop: "create_time", type: "range", values: timeRange});
  }
  return filters
}

function processByFilters(filters, action) {
  return new Promise((resolve, reject) => {
    var req = {
      filters: filters,
      action: action
    };
    Vue.http.post('/api/alarm/status', req).then((res) => {
        resolve(res.body);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}


function alarmsTableDataParser(res) {
  var alarms = [];
  res.data.forEach((item) => {
    alarms.push(Alarm.parseFromRestApi(item));
  });
  return {
    offset: res.offset,
    total: res.total,
    data: alarms
  };
}

function alarmsRestApiPropMap(prop) {
  if (prop == 'id')
    return 'id';
  else if (prop == 'policyId')
    return 'policy__id';
  else if (prop == 'policyName')
    return 'policy__name';
  else if (prop == 'policyLevel')
    return 'policy__level';
  else if (prop == 'status')
    return 'status';
  else if (prop == 'createTime')
    return 'create_time';
  else if (prop == 'nodeName')
    return 'node';
  else if (prop == 'gpuId')
    return 'gpu_index';
  else if (prop == 'comment')
    return 'comment';
  else if (prop == 'nodeName')
    return 'node';
  else
    return '';
}


function getAlarmTableDataFetcher() {
  return TableDataFetcherFactory.createRemotePagingFetcher('/api/alarm/alarm', alarmsRestApiPropMap, alarmsTableDataParser, 'data', 'offset', 'total');
}
function confirmAlarms(idList, statusList, policyLevelList, timeRange) {
  return processByFilters(buildFilters(idList, statusList, policyLevelList, timeRange), 'confirm');
}
function fixAlarms(idList, statusList, policyLevelList, timeRange) {
  return processByFilters(buildFilters(idList, statusList, policyLevelList, timeRange), 'solve');
}
function deleteAlarms(idList, statusList, policyLevelList, timeRange) {
  return processByFilters(buildFilters(idList, statusList, policyLevelList, timeRange), 'delete');
}


function updateAlarmComment(id, comment) {
  return new Promise((resolve, reject) => {
    var req = {
      comment: comment
    };
    Vue.http.post('/api/alarm/'+id+'/comment/', req).then((res) => {

        resolve(res.body);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getAlarmSound() {
  return new Promise((resolve, reject) => {
    Vue.http.get('api/alarm/sound/').then((res) => {
      resolve(AlarmPrompt.parseFromRestApi(res.body))
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

export default {
  AlarmStatusEnums,
  getAlarmTableDataFetcher,
  confirmAlarms,
  fixAlarms,
  deleteAlarms,
  updateAlarmComment,
  getAlarmSound
}
