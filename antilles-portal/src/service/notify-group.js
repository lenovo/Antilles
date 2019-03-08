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

class NotifyGroup {
  constructor() {
    this.id = 0;
    this.name = '';
    this.emails = [];
    this.mobiles = [];
    this.updateTime = new Date(0);
  }
  static parseFromRestApi(jsonObj) {
    var notifyGroup = new NotifyGroup();
    notifyGroup.id = jsonObj.id;
    notifyGroup.name = jsonObj.name;
    notifyGroup.emails = jsonObj.email;
    notifyGroup.mobiles = jsonObj.phone;
    notifyGroup.updateTime = Parser.parseTimeFromRestApi(jsonObj.last_operation_time);
    return notifyGroup;
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
  get emails() {
    return this._emails;
  }
  set emails(emails) {
    this._emails = emails;
  }
  get mobiles() {
    return this._mobiles;
  }
  set mobiles(mobiles) {
    this._mobiles = mobiles;
  }
  get updateTime() {
    return this._updateTime;
  }
  set updateTime(updateTime) {
    this._updateTime = updateTime;
  }
}

function notifyGroupsTableDataParser(res) {
  var notifyGroups = [];
  res.forEach((item) => {
    notifyGroups.push(NotifyGroup.parseFromRestApi(item));
  });
  return {
    data: notifyGroups
  };
}

function getNotifyGroupsTableDataFetcher() {
  return TableDataFetcherFactory.createLocalPagingFetcher('/api/alarm/targets/', notifyGroupsTableDataParser, 'data');
}

function getAllNotifyGroups() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/alarm/targets/').then((res) => {
        var notifyGroups = [];
        res.data.forEach((obj) => {
          notifyGroups.push(NotifyGroup.parseFromRestApi(obj));
        });
        resolve(notifyGroups);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function createNotifyGroup(name, emails, mobiles) {
  return new Promise((resolve, reject) => {
    var req = {
      name: name,
      email: emails,
      phone: mobiles
    };
    Vue.http.post('/api/alarm/targets/', req).then((res) => {
        resolve(NotifyGroup.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function updateNotifyGroup(id, name, emails, mobiles) {
  return new Promise((resolve, reject) => {
    var req = {
      name: name,
      email: emails,
      phone: mobiles
    };
    Vue.http.put('/api/alarm/targets/'+id, req).then((res) => {
        resolve(NotifyGroup.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function deleteNotifyGroup(id) {
  return new Promise((resolve, reject) => {
    Vue.http.delete('/api/alarm/targets/'+id).then((res) => {
        resolve(NotifyGroup.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

export default {
  getNotifyGroupsTableDataFetcher,
  getAllNotifyGroups,
  createNotifyGroup,
  updateNotifyGroup,
  deleteNotifyGroup
}
