/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import Parser from '../common/parser'
import Format from '../common/format'
import TableDataFetcherFactory from "../common/table-data-fetcher-factory"
import ErrorHandler from '../common/error-handler'

class User {
  constructor() {
    this.row = 0;
    this.username = '';
    this.role = '';
    this.firstName = '';
    this.lastName = '';
    this.billGroup = '';
    this.email = '';
    this.status = '';
    this.errorMessage = '';
  }
  static parseFromRestApi(jsonObj) {
    var user = new User();
    user.row = jsonObj.row;
    user.username = jsonObj.username;
    user.role = jsonObj.role;
    user.firstName = jsonObj.first_name||'';
    user.lastName = jsonObj.last_name||'';
    user.billGroup = jsonObj.bill_group;
    user.email = jsonObj.email||'';
    user.status = jsonObj.status;
    user.errorMessage = jsonObj.error_message;
    return user;
  }

  get row() {
    return this._row;
  }
  set row(row) {
    this._row = row;
  }
  get username() {
    return this._username;
  }
  set username(username) {
    this._username = username;
  }
  get role() {
    return this._role;
  }
  set role(role) {
    this._role = role;
  }
  get firstName() {
    return this._firstName;
  }
  set firstName(firstName) {
    this._firstName = firstName;
  }
  get lastName() {
    return this._lastName;
  }
  set lastName(lastName) {
    this._lastName = lastName;
  }
  get email() {
    return this._email;
  }
  set email(email) {
    this._email = email;
  }
  get result() {
    return this._result;
  }
  set result(result) {
    this._result = result;
  }
  get status() {
    return this._status;
  }
  set status(status) {
    this._status = status;
  }
  get errorMessage() {
    return this._errorMessage;
  }
  set errorMessage(errorMessage) {
    this._errorMessage = errorMessage;
  }

}

function usersRestApiPropMap(prop) {
  if (prop == 'firstName')
    return 'first_name';
  else if (prop == 'lastName')
    return 'last_name';
  else if (prop == 'billGroup')
    return 'bill_group';
  else if(prop == 'errorMessage')
    return 'error_message'
  else
    return prop;
}


function usersTableDataParser(res) {
  var users = [];
  res.data.forEach((item) => {
    users.push(User.parseFromRestApi(item));
  });
  return {
    offset: res.offset,
    total: res.total,
    data: users
  };
}


function getUsersTableDataFetcher() {
  return TableDataFetcherFactory.createRemotePagingFetcher('/api/users/import/detail', usersRestApiPropMap, usersTableDataParser, 'data', 'offset', 'total');
}


function getUsersImportStatu() {
  return new Promise((resolve, reject) => {
    Vue.http.get('api/users/import').then((res) => {
      if(res.body.last_importing){
        res.body.last_importing.finish_time = Format.formatDateTime(Parser.parseTimeFromRestApi(res.body.last_importing.finish_time));
      }
      resolve(res.body);
    },(err) => {
      ErrorHandler.restApiErrorHandler(err,reject);
    })
  })
}


function getUsersImportDetail() {
  return new Promise((resolve, reject) => {
    var req={
      offset: 0,
      length: 10,
      filters: [],
      sort:{
        prop:'username',
        order:'descending'
      }
    };
    Vue.http.get('api/users/import/detail',{params:{args: JSON.stringify(req)}}).then((res) => {
      resolve(res.body);
    },(err) => {
      ErrorHandler.restApiErrorHandler(err,reject);
    })
  })
}


function cancelUsersImport() {
  return new Promise((resolve, reject) => {
    Vue.http.delete('api/users/import').then((res) => {
      resolve(res.body);
    },(err) => {
      ErrorHandler.restApiErrorHandler(err,reject);
    })
  })
}


function getUsersExport() {
  var req = {
    timezone_offset: new Date().getTimezoneOffset()
  }
  return new Promise((resolve, reject) => {
    Vue.http.post('api/users/export',req).then((res) => {
      resolve(res.body);
    },(err) => {
      ErrorHandler.restApiErrorHandler(err,reject);
    })
  })
}



export default {
  getUsersTableDataFetcher,
  getUsersImportStatu,
  getUsersExport,
  cancelUsersImport,
  getUsersImportDetail
}