/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import TableDataFetcherFactory from "../common/table-data-fetcher-factory"
import ErrorHandler from '../common/error-handler'
import Parser from '../common/parser'
import Vue from 'vue'

class AlarmScript {
  constructor() {
    this.name = '';
    this.fileSize = 0;
    this.createTime = new Date(0);
  }
  static parseFromRestApi(jsonObj) {
    var alarmScript = new AlarmScript();
    alarmScript.name = jsonObj.name;
    alarmScript.fileSize = jsonObj.size;
    alarmScript.createTime = Parser.parseTimeFromRestApi(jsonObj.modify_time);
    return alarmScript;
  }
  get name() {
    return this._name;
  }
  set name(name) {
    this._name = name;
  }
  get fileSize() {
    return this._fileSize;
  }
  set fileSize(fileSize) {
    this._fileSize = fileSize;
  }
  get createTime() {
    return this._createTime;
  }
  set createTime(createTime) {
    this._createTime = createTime;
  }
}

function alarmScriptsTableDataParser(res) {
  var scripts = [];
  res.forEach((item) => {
    scripts.push(AlarmScript.parseFromRestApi(item));
  });
  return {
    data: scripts
  };
}

function getAlarmScriptsTableDataFetcher() {
  return TableDataFetcherFactory.createLocalPagingFetcher('/api/alarm/scripts/', alarmScriptsTableDataParser, 'data');
}

function getAllAlarmScripts() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/alarm/scripts/').then((res) => {
        var scripts = [];
        res.body.forEach((obj) => {
          scripts.push(obj.name);
        });
        resolve(scripts);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

export default {
  getAlarmScriptsTableDataFetcher,
  getAllAlarmScripts
}
