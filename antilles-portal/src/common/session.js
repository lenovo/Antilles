/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

// Define all session functions
import Utils from './utils'

function getValue(key, defaultValue) {
  var defaultValue = Utils.isUndefined(arguments[1]) ? null : arguments[1];
  if(hasKey(key)) {
    return window.sessionStorage.getItem(key);
  }
  return defaultValue;
}

function setValue(key, value) {
  window.sessionStorage.setItem(key, value);
}

function hasKey(key) {
  for(var i=0; i<window.sessionStorage.length; i++) {
    var temp_key = window.sessionStorage.key(i);
    if(temp_key == key) {
      return true;
    }
  }
  return false;
}

function clear() {
  window.sessionStorage.clear();
}

export default {
  getValue,
  setValue,
  hasKey,
  clear
}
