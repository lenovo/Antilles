/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

// Define all utils functions

function isEmptyObject(obj) {
  for (var key in obj) {
    return false;
  }
  return true;
}

function isUndefined(obj) {
  if(typeof(obj) == "undefined") {
    return true;
  }
  return false;
}

function deepCopy(obj) {
  return JSON.parse(JSON.stringify(obj));
}

export default {
  isEmptyObject,
  isUndefined,
  deepCopy
}
