/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */
import Vue from 'vue'
import ErrorHandler from '../common/error-handler'
import NodeService from './node'

// class GpuMonitor {
//   constructor() {
//     this.startTime  = new Date(0);
//     this.endTime    = new Date();
//     this.step       = 0;
//     this.datasource = [];
//     this.data       = [];
//   }
//   static parseFromRestApi(jsonObj) {
//     var gpuMonitor = new GpuMonitor();
//     gpuMonitor.startTime  = jsonObj.start;
//     gpuMonitor.endTime    = jsonObj.end;
//     gpuMonitor.step       = jsonObj.step;
//     gpuMonitor.datasource = jsonObj.datasource;
//     gpuMonitor.data       = jsonObj.data;
//     return gpuMonitor;
//   }
//   get startTime() {
//     return this._startTime;
//   }
//   set startTime(startTime) {
//    this._startTime = startTime;
//   }
//   get endTime() {
//     return this._endTime;
//   }
//   set endTime(endTime) {
//    this._endTime = endTime;
//   }
//   get step() {
//     return this._step;
//   }
//   set step(step) {
//    this._step = step;
//   }
//   get datasource() {
//     return this._datasource;
//   }
//   set datasource(datasource) {
//    this._datasource = datasource;
//   }
//   get data() {
//     return this._data;
//   }
//   set data(data) {
//    this._data = data;
//   }
//
// }
//
// class GpuProcesses {
//   constructor() {
//     this.id         = 0;
//     this.name       = '';
//     this.usedMemory = 0;
//   }
//   static parseFromRestApi(jsonObj) {
//     var gpuProcesses = new GpuProcesses();
//     gpuProcesses.id         = jsonObj.pid;
//     gpuProcesses.name       = jsonObj.pname;
//     gpuProcesses.usedMemory = jsonObj.usedGpuMemory;
//     return gpuProcesses;
//   }
//   get id() {
//     return this._id;
//   }
//   set id(id) {
//    this._id = id;
//   }
//   get name() {
//     return this._name;
//   }
//   set name(name) {
//    this._name = name;
//   }
//   get usedMemory() {
//     return this._usedMemory;
//   }
//   set usedMemory(usedMemory) {
//    this._usedMemory = usedMemory;
//   }
//
// }
//
// function getGpuMonitorByName(name, gpuId, monitorType, cf, startTime, endTime) {
//   return new Promise((resolve, reject) => {
//     var start = startTime?startTime:'end-1day';
//     var end = endTime?endTime:'now';
//     var api = `/node/${name}/gpu/${gpuId}/monitor/${monitorType}?start=${start}&end=${end}&cf=${cf}`
//     Vue.http.get(api).then((res) => {
//         resolve(GpuMonitor.parseFromRestApi(res.body));
//       },
//       (res) => {
//         ErrorHandler.restApiErrorHandler(res, reject);
//       }
//     );
//   });
// }
//
// function getComputeGpuProcessesByName(hostname, gpuIndex) {
//   return new Promise((resolve, reject) => {
//     var api = `/gpu/${hostname}/${gpuIndex}/processes`
//     Vue.http.get(api).then((res) => {
//         var processes = [];
//         res.body.forEach((item) => {
//           processes.push(GpuProcesses.parseFromRestApi(item));
//         })
//         resolve(processes);
//       },
//       (res) => {
//         ErrorHandler.restApiErrorHandler(res, reject);
//       }
//     );
//   });
// }
//
// function getGpuCoresByNode(hostname) {
//   return {
//     model: 'K80',
//     total: 2
//   };
// }
//
function getGpuStatusByNode(hostname) {
  return new Promise((resolve, reject) => {
    var coreTotal = getGpuCoresByNode(hostname).total;
    var promises = [];
    for(var index=0; index<coreTotal; index++) {
      promises.push(getComputeGpuProcessesByName(hostname, index));
    }
    Promise.all(promises).then((res) => {
      var used = 0;
      var total = coreTotal;
      for(var i=0; i<res.length; i++) {
        if(res[i].length > 0) {
          used += 1;
        }
      }
      resolve({
        used: used,
        total: total
      });
    }, (res) => {
      reject(res);
    });
  });
}

function getGpuStatusByNodes(hostnames) {
  return new Promise((resolve, reject) => {
    var promises = [];
    hostnames.forEach((hostname) => {
      promises.push(getGpuStatusByNode(hostname));
    });
    Promise.all(promises).then((res) => {
      var used = 0;
      var total = 0;
      for(var i=0; i<res.length; i++) {
        used += res[i].used;
        total += res[i].total;
      }
      resolve({
        used: used,
        total: total
      });
    }, (res) => {
      reject(res);
    })
  });
}

function getClusterGpuStatus() {
  return new Promise((resolve, reject) => {
    NodeService.getAllNodes().then((res) => {
      var promises = [];
      res.forEach((node) => {
        promises.push(NodeService.getNodeById(node.id));
      });
      Promise.all(promises).then((res) => {
        var used = 0;
        var total = 0;
        for(var i=0; i<res.length; i++) {
          total += res[i].gpus.length;
          for(var j=0; j<res[i].gpus.length; j++) {
            if(res[i].gpus[j].used) {
              used += 1;
            }
          }
        }
        resolve({
          used: used,
          total: total
        });
      }, (res) => {
        reject(res);
      });
    }, (res) => {
      reject(res);
    })
  });
}

export default {
  getClusterGpuStatus
}
