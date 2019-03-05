/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import ErrorHandler from '../common/error-handler'

class Queue {
  constructor() {
    this.index = 0;
    this.name = '';
    this.state='',
    this.totalNodes='',
    this.totalCores='',
    this.maxNodes='',
    this.maxCoresPerNode='',
    this.defineMemoryPerNode='',
    this.maxMemoryPerNode='',
    this.walltime=''
  }
  static parseFromRestApi(jsonObj) {
    var queue = new Queue();
    queue.index = jsonObj.id;
    queue.name = jsonObj.name;
    queue.state = jsonObj.state;
    queue.totalCores = jsonObj.cores;
    queue.totalNodes = jsonObj.nodes;
    queue.walltime = jsonObj.run_time;
    queue.maxNodes = jsonObj.max_nodes;
    queue.maxCoresPerNode = jsonObj.max_cores_per_node;
    queue.defineMemoryPerNode = jsonObj.def_mem_per_node;
    queue.maxMemoryPerNode = jsonObj.max_mem_per_node;
    return queue;
  }
  get index() {
    return this._index;
  }
  set index(index) {
   this._index = index;
  }
  get name() {
    return this._name;
  }
  set name(name) {
   this._name = name;
  }
  get state() {
    return this._state;
  }
  set state(state) {
   this._state = state;
  }
  get totalCores() {
    return this._totalCores;
  }
  set totalCores(totalCores) {
   this._totalCores = totalCores;
  }
  get totalNodes() {
    return this._totalNodes;
  }
  set totalNodes(totalNodes) {
   this._totalNodes = totalNodes;
  }
  get walltime() {
    return this._walltime;
  }
  set walltime(walltime) {
   this._walltime = walltime;
  }
  get maxNodes() {
    return this._maxNodes;
  }
  set maxNodes(maxNodes) {
   this._maxNodes = maxNodes;
  }
  get maxCoresPerNode() {
    return this._maxCoresPerNode;
  }
  set maxCoresPerNode(maxCoresPerNode) {
   this._maxCoresPerNode = maxCoresPerNode;
  }
  get defineMemoryPerNode() {
    return this._defineMemoryPerNode;
  }
  set defineMemoryPerNode(defineMemoryPerNode) {
   this._defineMemoryPerNode = defineMemoryPerNode;
  }
  get maxMemoryPerNode() {
    return this._maxMemoryPerNode;
  }
  set maxMemoryPerNode(maxMemoryPerNode) {
   this._maxMemoryPerNode = maxMemoryPerNode;
  }
}

function getAllQueues() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/queues/').then((res) => {
        var queues = [];
        res.body.forEach((obj) => {
          queues.push(Queue.parseFromRestApi(obj));
        });
        resolve(queues);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

export default {
	getAllQueues
}
