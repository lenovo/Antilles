/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import ErrorHandler from '../common/error-handler'

class NotifyEmail {
  constructor() {
    this.status = 'on';
    this.ssl = '0';
    this.id = '';
    this.password = '';
    this.address = '';
    this.port = '';
    this.mailbox = ''
  }
  static parseFromRestApi(jsonObj) {
    var notifyEmail = new NotifyEmail();
    notifyEmail.status = jsonObj.enabled ? 'on' : 'off';
    notifyEmail.ssl = jsonObj.ssl == 'NULL' ? '0' : jsonObj.ssl;
    notifyEmail.id = jsonObj.username;
    notifyEmail.password = jsonObj.password;
    notifyEmail.address = jsonObj.server_address;
    notifyEmail.port = String(jsonObj.server_port);
    notifyEmail.mailbox = jsonObj.sender_address;
    return notifyEmail;
  }
  static toRestApi(form) {
    var notifyEmail = {};
    notifyEmail.enabled = form.status == 'on' ? true : false;
    notifyEmail.ssl = form.ssl == '0' ? 'NULL' : form.ssl;
    notifyEmail.username = form.id;
    notifyEmail.password = form.password;
    notifyEmail.server_address = form.address;
    notifyEmail.server_port = parseFloat(form.port);
    notifyEmail.sender_address = form.mailbox;
    return notifyEmail;
  }
  get status() {
    return this._status;
  }
  set status(status) {
   this._status = status;
  }
  get ssl() {
    return this._ssl;
  }
  set ssl(ssl) {
   this._ssl = ssl;
  }
  get id() {
    return this._id;
  }
  set id(id) {
   this._id = id;
  }
  get password() {
    return this._password;
  }
  set password(password) {
   this._password = password;
  }
  get address() {
    return this._address;
  }
  set address(address) {
   this._address = address;
  }
  get port() {
    return this._port;
  }
  set port(port) {
   this._port = port;
  }
  get mailbox() {
    return this._mailbox;
  }
  set mailbox(mailbox) {
   this._mailbox = mailbox;
  }
}

function getNotifyEmail() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/alarm/email').then((res) => {
        resolve(NotifyEmail.parseFromRestApi(res.data));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function updateMail(form) {
  return new Promise((resolve, reject) => {
    var req = NotifyEmail.toRestApi(form);
    Vue.http.post('/api/alarm/email', req).then((res) => {
        resolve(NotifyEmail.parseFromRestApi(res.data));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function testMail(form) {
  return new Promise((resolve, reject) => {
    var config = NotifyEmail.toRestApi(form.config);
    var req = {
      type:'email',
      target:[form.address],
      config
    };
    Vue.http.post('/api/alarm/test', req).then((res) => {
        resolve(NotifyEmail.parseFromRestApi(res.data));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

export default {
  getNotifyEmail,
  updateMail,
  testMail
}
