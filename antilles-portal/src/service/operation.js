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
import UserService from './user'

const ModuleEnums = [
  {
    value: 'user',
    children:[
      {value: 'create'},
      {value: 'update'},
      {value: 'delete'},
    ]
  },
  {
    value: 'job',
    children:[
      {value: 'create'},
      {value: 'rerun'},
      {value: 'cancel'},
      {value: 'delete'},
    ]
  },
  {
    value: 'node',
    children:[
      {value: 'turn_on'},
      {value: 'turn_off'},
    ]
  },
  {
    value: 'alarm',
    children:[
      {value: 'confirm'},
      {value: 'solve'},
      {value: 'delete'},
      {value: 'comment'},
    ]
  },
  {
    value: 'policy',
    children:[
      {value: 'create'},
      {value: 'update'},
      {value: 'delete'},
    ]
  },
  {
    value: 'billgroup',
    children:[
      {value: 'create'},
      {value: 'update'},
      {value: 'delete'},
    ]
  },
  {
    value: 'deposit',
    children:[
      {value: 'recharge'},
      {value: 'chargeback'},
    ]
  },
];

class Target {
  constructor() {
    this.id = 0;
    this.name = '';
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
}

class Operation {
  constructor() {
    this.logId = 0;
    this.userName = '';
    this.action = '';
    this.actionTime = new Date(0);
    this.target = [];
    this.module = '';
  }
  static parseFromRestApi(jsonObj) {
    var operation = new Operation();
    operation.logId = jsonObj.id;
    operation.userName = jsonObj.operator;
    operation.action = getOperationEnums(jsonObj.operation);
    operation.actionTime = Parser.parseTimeFromRestApi(jsonObj.operate_time);
    operation.module = getModuleEnums(jsonObj.module);
    let _target = jsonObj.target;
    _target.forEach((item) => {
      operation.target.push({
        id: item.id,
        name: item.name
      })
    })
    return operation;
  }

  get logId() {
    return this._logId;
  }
  set logId(logId) {
   this._logId = logId;
  }
  get userName() {
    return this._userName;
  }
  set userName(userName) {
   this._userName = userName;
  }
  get action() {
    return this._action;
  }
  set action(action) {
   this._action = action;
  }
  get actionTime() {
    return this._actionTime;
  }
  set actionTime(actionTime) {
   this._actionTime = actionTime;
  }
  get target() {
    return this._target;
  }
  set target(target) {
   this._target = target;
  }
  get module() {
    return this._module;
  }
  set module(module) {
   this._module = module;
  }

}
function getModuleEnums(modul) {
  const  modules = {
    user:"user",
    job:"job",
    node:"node",
    alarm:"alarm",
    policy:"policy",
    billgroup:"billgroup",
    deposit:"deposit"
  }
  return modules[modul]
}
function getOperationEnums(operation) {
  const  operations = {
    create: "create",
    update: "update",
    cancel: "cancel",
    rerun: "rerun",
    delete: "delete",
    comment: "comment",
    turn_on: "turn_on",
    turn_off: "turn_off",
    confirm: "confirm",
    solve: "solve",
    recharge: "recharge",
    chargeback: "chargeback"
  }
  return operations[operation]
}


function operationsTableDataParser(res) {
  var operations = [];
  res.data.forEach((item) => {
    operations.push(Operation.parseFromRestApi(item));
  });
  return {
    offset: res.offset,
    total: res.total,
    data: operations
  };
}

function operationsRestApiPropMap(prop) {
  if (prop == 'logId')
    return 'id';
  else if (prop == 'userName')
    return 'operator';
  else if (prop == 'action')
    return 'operation';
  else if (prop == 'actionTime')
    return 'operate_time';
  else if (prop == 'module')
    return 'module';
  else if (prop == 'target')
    return 'target';
  else
    return '';
}


function getOperationTableDataFetcher() {
  return TableDataFetcherFactory.createRemotePagingFetcher('/api/optlog/', operationsRestApiPropMap, operationsTableDataParser, 'data', 'offset', 'total');
}

function getOptlogLatest(length) {
  return new Promise((resolve, reject) => {
    var params = {
			counts: length
		};
    Vue.http.get('/api/optlog/latest/', {params: params}).then((res) => {
      var operations = [];
      res.body.data.forEach((item) => {
        operations.push(Operation.parseFromRestApi(item))
      })
      resolve(operations)
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

export default {
  ModuleEnums,
  getOperationTableDataFetcher,
  getOptlogLatest
}
