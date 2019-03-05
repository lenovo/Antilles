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
import BillGroupService from './bill-group'

const UserRoleEnums = ['admin', 'operator', 'staff'];

class User {
  constructor() {
    this.id = 0;
    this.username = '';
    this.role = '';
    this.firstName = '';
    this.lastName = '';
    this.email = '';
    this.billGroup = false;
    this.userGroup = false;
    this.billGroupId = 0;
    this.billGroupName = '';
    this.userGroupName = '';
    this.status = '';
    this.loginTime = null;
    this.createTime = new Date(0);
    this.updateTime = new Date(0);
    this.freezed = false;
    this.thawTime = new Date(0);
  }
  static parseFromRestApi(jsonObj) {
    var user = new User();
    user.id = jsonObj.id;
    user.username = jsonObj.username;
    user.role = jsonObj.role=='user' ? 'staff' : jsonObj.role;
    user.firstName = jsonObj.first_name||'';
    user.lastName = jsonObj.last_name||'';
    user.email = jsonObj.email||'';
    user.billGroup = jsonObj.bill_group?BillGroupService.BillGroup.parseFromRestApi(jsonObj.bill_group):false;
    user.userGroup = jsonObj.os_group?jsonObj.os_group:false;
    user.billGroupId = jsonObj.bill_group?jsonObj.bill_group.id:0;
    user.billGroupName = jsonObj.bill_group?jsonObj.bill_group.name:'';
    user.userGroupName = jsonObj.os_group?jsonObj.os_group.name:'';
    user.loginTime = jsonObj.last_login ? Parser.parseTimeFromRestApi(jsonObj.last_login) : null;
    user.createTime = Parser.parseTimeFromRestApi(jsonObj.date_joined);
    user.updateTime = Parser.parseTimeFromRestApi(jsonObj.last_operation_time);
    user.freezed = jsonObj.is_freezed;
    user.thawTime = Parser.parseTimeFromRestApi(jsonObj.effective_time);
    return user;
  }
  get realName() {
    if(this._firstName && this._lastName) {
      return this._firstName + ' ' + this._lastName;
    }
    return '';
  }
  get id() {
    return this._id;
  }
  set id(id) {
   this._id = id;
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
  get billGroup() {
    return this._billGroup;
  }
  set billGroup(billGroup) {
   this._billGroup = billGroup;
  }
  get userGroup() {
    return this._userGroup;
  }
  set userGroup(userGroup) {
   this._userGroup = userGroup;
  }
  get billGroupId() {
    return this._billGroupId;
  }
  set billGroupId(billGroupId) {
   this._billGroupId = billGroupId;
  }
  get billGroupName() {
    return this._billGroupName;
  }
  set billGroupName(billGroupName) {
   this._billGroupName = billGroupName;
  }
  get userGroupName() {
    return this._userGroupName;
  }
  set userGroupName(userGroupName) {
   this._userGroupName = userGroupName;
  }
  get status() {
    return this._status;
  }
  set status(status) {
   this._status = status;
  }
  get loginTime() {
    return this._loginTime;
  }
  set loginTime(loginTime) {
   this._loginTime = loginTime;
  }
  get createTime() {
    return this._createTime;
  }
  set createTime(createTime) {
   this._createTime = createTime;
  }
  get updateTime() {
    return this._updateTime;
  }
  set updateTime(updateTime) {
   this._updateTime = updateTime;
  }
  get freezed() {
    return this._freezed;
  }
  set freezed(freezed) {
   this._freezed = freezed;
  }
  get thawTime() {
    return this._thawTime;
  }
  set thawTime(thawTime) {
   this._thawTime = thawTime;
  }

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

function usersRestApiPropMap(prop) {
  if (prop == 'id')
    return 'id';
  else if (prop == 'username')
    return 'username';
  else if (prop == 'role')
    return 'role';
  else if (prop == 'loginTime')
    return 'last_login';
  else if (prop == 'thawTime')
    return 'effective_time';
  else if (prop == 'billGroupName')
    return 'bill_group';
  else if (prop == 'freezed')
    return 'is_freezed';
  else
    return '';
}

function getUsersTableDataFetcher() {
  return TableDataFetcherFactory.createRemotePagingFetcher('/api/users', usersRestApiPropMap, usersTableDataParser, 'data', 'offset', 'total');
}

function getAllUsers() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/users').then((res) => {
        var users = [];
        res.body.forEach((obj) => {
          users.push(User.parseFromRestApi(obj));
        });
        resolve(users);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getUserById(id) {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/users/' + id).then((res) => {
        var user = User.parseFromRestApi(res.body);
        resolve(user);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getUserRoleDisplayName(role) {
  if(role == 'admin') {
    return window.gApp.$t('User.Role.Admin');
  }
  if(role == 'operator') {
    return window.gApp.$t('User.Role.Operator');
  }
  if(role == 'staff') {
    return window.gApp.$t('User.Role.Staff');
  }
  return '';
}

function createUser(username, role, firstName, lastName, billGroupId, email, userGroupName, password) {
  return new Promise((resolve, reject) => {
    var req = {
      username: username,
      role: role=='staff' ? 'user' : role,
      first_name: firstName,
      last_name: lastName,
      bill_group: billGroupId,
      email: email
    };
    if(window.gApp.$store.state.auth.ldapManaged) {
      req.os_group = userGroupName,
      req.password = password
    }
    Vue.http.post('/api/users', req).then((res) => {
        resolve(User.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function updateUser(id, role, firstName, lastName, billGroupId, email, userGroupName) {
  return new Promise((resolve, reject) => {
    var req = {
      role: role=='staff' ? 'user' : role,
      first_name: firstName,
      last_name: lastName,
      bill_group: billGroupId,
      email: email
    };
    if(window.gApp.$store.state.auth.ldapManaged) {
      req.os_group = userGroupName;
    }
    Vue.http.patch(`/api/users/${id}?query_by_id=true`, req).then((res) => {
        resolve(User.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function deleteUser(id) {
  return new Promise((resolve, reject) => {
    Vue.http.delete(`/api/users/${id}?query_by_id=true`).then((res) => {
        var user = new User();
        user.id = id;
        resolve(user);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function importUser(username, role, firstName, lastName, billGroupId, email, homeDirectory) {
  return new Promise((resolve, reject) => {
    var req = {
      username: username,
      role: role=='staff' ? 'user' : role,
      bill_group: billGroupId,
      email: email,
      first_name: firstName,
      last_name: lastName,
      // userhome: homeDirectory
    };
    Vue.http.put('/api/users/'+username, req).then((res) => {
        resolve(User.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function changeUserPassword(id, password) {
  return new Promise((resolve, reject) => {
    var req = {
      password: password
    };
    Vue.http.put(`/api/users/${id}/password?query_by_id=true`, req).then((res) => {
        var user = new User();
        user.id = id;
        resolve(user);
        //resolve(User.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getUserFreezedByName(id) {
  return new Promise((resolve, reject) => {
    Vue.http.get(`/api/users/${id}/freezed/`).then((res) => {
      resolve({
        freezed: res.body.is_frozen,
        thawTime: Parser.parseTimeFromRestApi(res.body.effective_time)
      })
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

function freezedUserByName(id, days, hours) {
  return new Promise((resolve, reject) => {
    var req = {
      days: Number(days) || 0,
      hours: Number(hours) || 0
    }
    Vue.http.post(`/api/users/${id}/freezed/`, req).then((res) => {
      resolve({
        freezed: res.body.is_frozen,
        thawTime: Parser.parseTimeFromRestApi(res.body.effective_time)
      })
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

function unfreezedUserByName(id) {
  return new Promise((resolve, reject) => {
    Vue.http.delete(`/api/users/${id}/freezed/`).then((res) => {
      resolve('')
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

function getUserImportList() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/users/unimported/').then((res) => {
        var userList = res.body?res.body:[];
        resolve(userList);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}
export default {
  UserRoleEnums,
  getUsersTableDataFetcher,
  getAllUsers,
  getUserRoleDisplayName,
  createUser,
  updateUser,
  deleteUser,
  importUser,
  changeUserPassword,
  getUserById,
  freezedUserByName,
  unfreezedUserByName,
  getUserImportList
}
