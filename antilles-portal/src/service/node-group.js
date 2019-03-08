/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue';

class NodeGroup {
  constructor(){
    this.id = 0;
    this.name = "";
  }

  static parseFromRestApi(jsonObj){
    let group = new NodeGroup();
    group.id = jsonObj.id;
    group.name = jsonObj.groupname;
    return group;
  }

  get name() {
    return this._name;
  }
  set name(name) {
    this._name = name;
  }
  get id() {
    return this._id;
  }
  set id(id) {
    this._id = id;
  }
}

function getAllNodeGroups() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/nodegroups/').then((res) => {
      var groups = [];
      res.body.groups.forEach((obj) => {
        groups.push(NodeGroup.parseFromRestApi(obj));
      });
      resolve(groups);
    }, (res) => {
      reject(res.body)
    })
  })
}

export default {
  getAllNodeGroups
}
