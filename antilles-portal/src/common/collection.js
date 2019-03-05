/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

function sortObjectsByProp(objects, prop, order, compareFunc) {
  function compareProperty(objA, objB) {
    var valA = objA[prop];
    var valB = objB[prop];
    if (!isNaN(Number(valA)) && !isNaN(Number(valB))) {
      valA = Number(valA);
      valB = Number(valB);
    }
    // Default is ASC
    if (valA > valB) {
      return 1;
    } else if (valA < valB) {
      return -1;
    } else {
      return 0;
    }
  };
  if(compareFunc) {
    objects.sort(compareFunc);
  } else {
    objects.sort(compareProperty);
  }
  if(order.indexOf('desc') >= 0) {
    objects.reverse();
  }
}

// Type: in, range
function filterObjectsByProp(objects, prop, type, values) {
  var filterObjects = [];
  objects.forEach((obj) => {
    if(type=='in') {
      if(values.indexOf(obj[prop]) >= 0) {
        filterObjects.push(obj);
      }
    }
    if(type=='range') {
      if(obj[prop]>=values[0] && obj[prop]<=value[1]) {
        filterObjects.push(obj);
      }
    }
  });
  return filterObjects;
}

function searchObjectsByProps(objects, props, keyword) {
  var searchObjects = [];
  objects.forEach((obj) => {
    var match = false;
    props.forEach((prop) => {
      if(obj[prop] && obj[prop].toString().indexOf(keyword) >= 0) {
        match = true;
        // Need to skip from loop
      }
    })
    if(match) {
      searchObjects.push(obj);
    }
  });
  return searchObjects;
}

function removeByValue(arr, val) {
  for(var i=0; i<arr.length; i++) {
    if(arr[i] == val) {
      arr.splice(i, 1);
      break;
    }
  }
}

export default {
  sortObjectsByProp,
  filterObjectsByProp,
  searchObjectsByProps,
  removeByValue
}