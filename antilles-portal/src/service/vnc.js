/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import TableDataFetcherFactory from "../common/table-data-fetcher-factory"
import ErrorHandler from '../common/error-handler'
import Parser from '../common/parser'
import Vue from 'vue'

class VNC {
  constructor() {
    this.id = '';
    this.name = '';
    this.host = '';
    this.port = 0;
    this.username = '';
    this.pid = 0;
    this.index = '';
    this.status = '';
    this.operation = '';
    this.token = '';
  }
  static parseFromRestApi(jsonObj) {
    var vnc = new VNC();
    vnc.id = jsonObj.id;
    vnc.name = jsonObj.name;
    vnc.host = jsonObj.host;
    vnc.port = jsonObj.port;
    vnc.username = jsonObj.username;
    vnc.pid = jsonObj.pid;
    vnc.index = jsonObj.index;
    vnc.status = jsonObj.status;
    vnc.operation = jsonObj.operation;
    vnc.token = jsonObj.token;
    return vnc;
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
  get host() {
    return this._host;
  }
  set host(host) {
   this._host = host;
  }
  get port() {
    return this._port;
  }
  set port(port) {
   this._port = port;
  }
  get username() {
    return this._username;
  }
  set username(username) {
   this._username = username;
  }
  get pid() {
    return this._pid;
  }
  set pid(pid) {
   this._pid = pid;
  }
  get index() {
    return this._index;
  }
  set index(index) {
   this._index = index;
  }
  get status() {
    return this._status;
  }
  set status(status) {
   this._status = status;
  }
  get operation() {
    return this._operation;
  }
  set operation(operation) {
   this._operation = operation;
  }
  get token(){
    return this._token;
  }
  set token(token){
    this._token = token;
  }
}

function vncTableDataParser(res) {
  var vncs = [];
  res.forEach(function(item){
    vncs.push(VNC.parseFromRestApi(item));
  });
  return {
    data:vncs
  }
}

function getVNCTableDataFetcher(username) {
  var url = '/api/vnc/sessions';
      url += username?'/'+username:'';
  return TableDataFetcherFactory.createLocalPagingFetcher(url, vncTableDataParser, 'data');
}

function deleteVNC(id){
  return new Promise((resolve, reject) => {
    Vue.http.delete('/api/vnc/session/'+id).then((res) => {
        resolve(res);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

export default {
  getVNCTableDataFetcher,
  deleteVNC
}
