/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import Parser from '../common/parser'
import TableDataFetcherFactory from "../common/table-data-fetcher-factory"
import ErrorHandler from '../common/error-handler'

class UserGroup {
  constructor() {
    this.name = '';
    this.id = '';
  }
  static parseFromRestApi(jsonObj) {
    var userGroup = new UserGroup();
    userGroup.name = jsonObj.name;
    userGroup.id = jsonObj.gid;
    return userGroup;
  }
  get name() {
    return this._name;
  }
  set name(name) {
    this._name = name;
  }
  get id() {
    return this._id;
  }
  set id(id) {
    this._id = id;
  }
}

function userGroupsTableDataParser(res) {
  var userGroups = [];
  res.forEach((item) => {
    userGroups.push(UserGroup.parseFromRestApi(item));
  });
  return {
    data: userGroups
  };
}

function getUserGroupsTableDataFetcher() {
  return TableDataFetcherFactory.createLocalPagingFetcher('/api/osgroups', userGroupsTableDataParser, 'data');
}

function getAllUserGroups() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/osgroups').then((res) => {
        var userGroups = [];
        res.body.forEach((obj) => {
          userGroups.push(UserGroup.parseFromRestApi(obj));
        });
        resolve(userGroups);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function createUserGroup(name) {
  return new Promise((resolve, reject) => {
    var req = {
      name: name
    };
    Vue.http.post('/api/osgroups', req).then((res) => {
        resolve(UserGroup.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function updateUserGroup(name, newName) {
  return new Promise((resolve, reject) => {
    var req = {
      name: newName
    };
    Vue.http.put('/api/osgroups/'+name, req).then((res) => {
        resolve(UserGroup.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function deleteUserGroup(name) {
  return new Promise((resolve, reject) => {
    Vue.http.delete(`/api/osgroups/${encodeURIComponent(name)}`).then((res) => {
        var userGroup = new UserGroup();
        userGroup.name = name;
        resolve(UserGroup.parseFromRestApi(userGroup));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

export default {
  getUserGroupsTableDataFetcher,
  getAllUserGroups,
  createUserGroup,
  updateUserGroup,
  deleteUserGroup
}
