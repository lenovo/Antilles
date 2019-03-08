/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import Parser from '../common/parser'
import TableDataFetcherFactory from "../common/table-data-fetcher-factory"
import ErrorHandler from '../common/error-handler'

class QueueInfo {
  constructor() {
    this.queueName = '';
    this.queueState = '';
    this.priority = '';
    this.isDefault = '';
    this.userGroups = '';
    this.nodes = '';
    this.updateTime = new Date(0);
  }
  static parseFromRestApi(jsonObj) {
    var scheduler = new QueueInfo();
    var nodeStatus=Object.keys(jsonObj.nodes_list);
    var nodesNumber=Object.values(jsonObj.nodes_total);
    var nodesExpress=[];
    for(var i=0;i<nodeStatus.length;i++){
      nodesExpress.push(nodeStatus[i]+':'+nodesNumber[i])
    }
    scheduler.queueName = jsonObj.queue_name;
    scheduler.queueState = jsonObj.avail;
    scheduler.priority = jsonObj.priority;
    scheduler.isDefault = jsonObj.default==false?'NO':'YES';
    scheduler.userGroups = jsonObj.user_groups;
    scheduler.nodes = nodesExpress.toString().replace(/,|，/g,'/');
    return scheduler;
  }
  get queueName() {
    return this._queueName;
  }
  set queueName(queueName) {
   this._queueName = queueName;
  }
  get queueState() {
    return this._queueState;
  }
  set queueState(queueState) {
   this._queueState = queueState;
  }
  get priority() {
    return this._priority;
  }
  set priority(priority) {
   this._priority = priority;
  }
  get isDefault() {
    return this._isDefault;
  }
  set isDefault(isDefault) {
   this._isDefault = isDefault;
  }
  get userGroups() {
    return this._userGroups;
  }
  set userGroups(userGroups) {
   this._userGroups = userGroups;
  }
  get nodes() {
    return this._nodes;
  }
  set nodes(nodes) {
   this._nodes = nodes;
  }
  get updateTime() {
    return this._updateTime;
  }
  set updateTime(updateTime) {
   this._updateTime = updateTime;
  }
}
function queueInfoTableDataParser(res) {
  var queueInfoDatas = [];
  res.forEach((item) => {
    queueInfoDatas.push(QueueInfo.parseFromRestApi(item));
  });
  return {
    data: queueInfoDatas
  };
}

function getSchedulerTableDataFetcher() {
  return TableDataFetcherFactory.createLocalPagingFetcher('/api/scheduler/queues/', queueInfoTableDataParser, 'data');
}


function createQueue(queueName,nodeList,isdefault,priority,maxTime,overSubscribe,userGroup,queueState){
  return new Promise((resolve, reject) => {
    var req = {
      queue_name: queueName,
      node_list: nodeList,
      default: isdefault,
      priority: parseInt(priority),
      max_time: maxTime,
      over_subscribe: overSubscribe,
      user_groups: userGroup,
      avail: queueState 
    };
    Vue.http.post('/api/scheduler/queues/',req).then((res) => {
        resolve();
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function updateQueue(queueName,nodeList,isdefault,priority,maxTime,overSubscribe,userGroup,queueState){
  return new Promise((resolve, reject) => {
    var req = {
      node_list: nodeList,
      default: isdefault,
      priority: priority,
      max_time: maxTime,
      over_subscribe: overSubscribe,
      user_groups: userGroup,
      avail: queueState
    };
    Vue.http.put('/api/scheduler/queues/' + queueName,JSON.stringify(req)).then((res) => {
        resolve();
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function deleteQueue(queueName){
  return new Promise((resolve, reject) => {
    Vue.http.delete('/api/scheduler/queues/' + queueName).then((res) => {
        resolve();
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getQueue(queueName){
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/scheduler/queues/' + queueName).then((res) => {
        resolve(res.body);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function setQueueState(queueName,action){
  return new Promise((resolve, reject) => {
    var req={
      action: action
    }
    Vue.http.put('/api/scheduler/queues/' + queueName +'/status/',req).then((res) => {
        resolve();
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function setNodesState(action,nodeList){
  return new Promise((resolve, reject) => {
    var req={
      action: action.toLowerCase(),
      node_list: nodeList
    }
    Vue.http.post('api/scheduler/nodes/status/',req).then((res) => {
        resolve();
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getNodesState(nodeList){
  return new Promise((resolve, reject) => {
    var req={
      node_list: nodeList
    }
    Vue.http.get('api/scheduler/nodes/status/',{params:req}).then((res) => {
        resolve(res.body);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

export default {
  getSchedulerTableDataFetcher,
  createQueue,
  updateQueue,
  deleteQueue,
  getQueue,
  setNodesState,
  setQueueState,
  getNodesState
}
