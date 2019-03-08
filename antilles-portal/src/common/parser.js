/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

const CurrentTimezoneOffset = new Date().getTimezoneOffset();

function parseTimeFromRestApi(timeStr) {
  if(timeStr) {
    var timeStr = String(timeStr);
    if(timeStr.indexOf('T')>=0 && timeStr.indexOf('Z')>=0) {
      return new Date(Date.parse(timeStr));
    } else if(timeStr.indexOf('-')>=0){
      timeStr = timeStr.replace('-','/').replace('-','/')
      return new Date(Date.parse(timeStr) - CurrentTimezoneOffset*60*1000);
    } else {
      return new Date(timeStr*1000);
    }
  }
  return null;
}

function parseBooleanFromString(str) {
  if(str == 'true') {
    return true;
  }
  return false;
}

export default {
  parseTimeFromRestApi,
  parseBooleanFromString
}
