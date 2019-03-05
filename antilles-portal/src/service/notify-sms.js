/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import ErrorHandler from '../common/error-handler'

class NotifySMS {
  constructor() {
    this.status = 'on';
    this.port = 'ttyS0';
    this.modem = 'GPRS';
    this.limit = 300;
    this.number = '';
  }
  static parseFromRestApi(jsonObj) {
    var notifySMS = new NotifySMS();
    notifySMS.status = jsonObj.enabled ? 'on' : 'off';
    notifySMS.port = jsonObj.serial_port;
    notifySMS.modem = jsonObj.modem;
    notifySMS.limit = jsonObj.daily_limit;
    notifySMS.number = jsonObj.sended;
    return notifySMS;
  }
  static toRestApi(form) {
    var notifySMS = {};
    notifySMS.enabled = form.status == 'on' ? true : false;
    notifySMS.serial_port = form.port;
    notifySMS.modem = form.modem;
    notifySMS.daily_limit = form.limit;
    notifySMS.sended = form.number;
    return notifySMS;
  }
  get status() {
    return this._status;
  }
  set status(status) {
   this._status = status;
  }
  get port() {
    return this._port;
  }
  set port(port) {
   this._port = port;
  }
  get modem() {
    return this._modem;
  }
  set modem(modem) {
   this._modem = modem;
  }
  get limit() {
    return this._limit;
  }
  set limit(limit) {
   this._limit = limit;
  }
  get number() {
    return this._number;
  }
  set number(number) {
   this._number = number;
  }
}

function getNotifySMS() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/alarm/sms').then((res) => {
        resolve(NotifySMS.parseFromRestApi(res.data));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function updateSMS(form) {
  return new Promise((resolve, reject) => {
    var req = NotifySMS.toRestApi(form);
    Vue.http.post('/api/alarm/sms', req).then((res) => {
        resolve(NotifySMS.parseFromRestApi(res.data));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function testSMS(form) {
  return new Promise((resolve, reject) => {
    var config = NotifySMS.toRestApi(form.config);
    var req = {
      type:'sms',
      target:[form.number],
      config
    };
    Vue.http.post('/api/alarm/test', req).then((res) => {
        resolve(NotifySMS.parseFromRestApi(res.data));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

export default {
  getNotifySMS,
  updateSMS,
  testSMS
}
