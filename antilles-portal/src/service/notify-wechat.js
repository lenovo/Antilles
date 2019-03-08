/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import ErrorHandler from '../common/error-handler'

class NotifyWechat {
  constructor() {
    this.status = 'on';
  }
  static parseFromRestApi(jsonObj) {
    var notifyWechat = new NotifyWechat();
    notifyWechat.status = jsonObj.enabled ? 'on' : 'off';
    return notifyWechat;
  }
  static toRestApi(form) {
    var notifyWechat = {};
    notifyWechat.enabled = form.status == 'on' ? true : false;
    return notifyWechat;
  }
  get status() {
    return this._status;
  }
  set status(status) {
   this._status = status;
  }
}

function getWechatImage() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/alarm/wechat/qrcode', {responseType: 'blob'}).then((res) => {
        resolve(res.blob());

      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getWechat() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/alarm/wechat').then((res) => {
        resolve(NotifyWechat.parseFromRestApi(res.data));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function updateWechat(form) {
  return new Promise((resolve, reject) => {
    var req = NotifyWechat.toRestApi(form);
    Vue.http.post('/api/alarm/wechat', req).then((res) => {
        resolve(NotifyWechat.parseFromRestApi(res.data));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function testWechat(form) {
  return new Promise((resolve, reject) => {
    var config = NotifyWechat.toRestApi(form);
    var req = {
      type:'wechat',
      target:'',
      config
    };
    Vue.http.post('/api/alarm/test', req).then((res) => {
        resolve(NotifyWechat.parseFromRestApi(res.data));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

export default {
  getWechatImage,
  getWechat,
  updateWechat,
  testWechat
}
