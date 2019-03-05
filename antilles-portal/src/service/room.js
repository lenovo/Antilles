/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from "vue"
import ErrorHandler from '../common/error-handler'
import Collection from '../common/collection'

class Room{
  constructor(){
    this.roomName = "";
    this.roomId = 0;
    this.location = "";
    this.nodeNumber = 0;
    this.powerConsumption = "";
    this.busyNumber = 0;
    this.usedNumber = 0;
    this.offNumber = 0;
    this.freeNumber = 0;
  }

  static parseFromRestApi(obj){
    let room = new Room();
    room.roomName = obj.name;
    room.roomId = obj.id;
    room.location = obj.location;
    room.nodeNumber = obj.node_num;
    room.powerConsumption = obj.power_consumption;
    room.busyNumber = obj.node_busy;
    room.usedNumber = obj.node_used;
    room.offNumber = obj.node_off;
    room.freeNumber = obj.node_free;

    return room;
  }

  get roomName() {
    return this._roomName;
  }
  set roomName(roomName) {
    this._roomName = roomName;
  }
  get roomId() {
    return this._roomId;
  }
  set roomId(roomId) {
    this._roomId = roomId;
  }
  get location() {
    return this._location;
  }
  set location(location) {
    this._location = location;
  }
  get nodeNumber() {
    return this._nodeNumber;
  }
  set nodeNumber(nodeNumber) {
    this._nodeNumber = nodeNumber;
  }
  get powerConsumption() {
    return this._powerConsumption;
  }
  set powerConsumption(powerConsumption) {
    this._powerConsumption = powerConsumption;
  }
  get busyNumber() {
    return this._busyNumber;
  }
  set busyNumber(busyNumber) {
    this._busyNumber = busyNumber;
  }
  get usedNumber() {
    return this._usedNumber;
  }
  set usedNumber(usedNumber) {
    this._usedNumber = usedNumber;
  }
  get offNumber() {
    return this._offNumber;
  }
  set offNumber(offNumber) {
    this._offNumber = offNumber;
  }
  get freeNumber() {
    return this._freeNumber;
  }
  set freeNumber(freeNumber) {
    this._freeNumber = freeNumber;
  }
}

class Rack{
  constructor(){
    this.rackName = "";
    this.rackId = 0;
    this.location = "";
    this.nodeNumber = 0;
    this.busyNumber = 0;
    this.usedNumber = 0;
    this.offNumber = 0;
    this.freeNumber = 0;
    this.energy = 0;
    this.alarmLevel = []
  }

  static parseFromRestApi(obj){
    let rack = new Rack();
    rack.rackName = obj.name;
    rack.rackId = obj.id;
    rack.location = obj.location;
    rack.nodeNumber = obj.node_num;
    rack.busyNumber = obj.node_busy;
    rack.usedNumber = obj.node_used;
    rack.offNumber = obj.node_off;
    rack.freeNumber = obj.node_free;
    rack.energy = obj.energy;
    rack.alarmLevel = obj.alarm_level;
    return rack;
  }

  get rackName() {
    return this._rackName;
  }
  set rackName(rackName) {
    this._rackName = rackName;
  }
  get rackId() {
    return this._rackId;
  }
  set rackId(rackId) {
    this._rackId = rackId;
  }
  get location() {
    return this._location;
  }
  set location(location) {
    this._location = location;
  }
  get nodeNumber() {
    return this._nodeNumber;
  }
  set nodeNumber(nodeNumber) {
    this._nodeNumber = nodeNumber;
  }
  get busyNumber() {
    return this._busyNumber;
  }
  set busyNumber(busyNumber) {
    this._busyNumber = busyNumber;
  }
  get usedNumber() {
    return this._usedNumber;
  }
  set usedNumber(usedNumber) {
    this._usedNumber = usedNumber;
  }
  get offNumber() {
    return this._offNumber;
  }
  set offNumber(offNumber) {
    this._offNumber = offNumber;
  }
  get freeNumber() {
    return this._freeNumber;
  }
  set freeNumber(freeNumber) {
    this._freeNumber = freeNumber;
  }
  get energy() {
    return this._energy;
  }
  set energy(energy) {
    this._energy = energy;
  }
  get alarmLevel() {
    return this._alarmLevel;
  }
  set alarmLevel(alarmLevel) {
    this._alarmLevel = alarmLevel;
  }
}


class Row{
  constructor(){
    this.rowName = "";
    this.rowId = 0;
    this.index = 0;
    this.totalNode = 0;
    this.totalRacks = 0;
    this.totalEnergy = 0;
  }

  static parseFromRestApi(obj){
    let row = new Row();
    row.rowName = obj.name;
    row.rowId = obj.id;
    row.index = obj.row_index;
    row.totalNode = obj.total_nodes;
    row.totalRacks = obj.total_racks;
    row.totalEnergy = obj.total_energy;
    return row;
  }

  get rowName() {
    return this._rowName;
  }
  set rowName(rowName) {
    this._rowName = rowName;
  }
  get rowId() {
    return this._rowId;
  }
  set rowId(rowId) {
    this._rowId = rowId;
  }
  get index() {
    return this._index;
  }
  set index(index) {
    this._index = index;
  }
  get totalNode() {
    return this._totalNode;
  }
  set totalNode(totalNode) {
    this._totalNode = totalNode;
  }
  get totalRacks() {
    return this._totalRacks;
  }
  set totalRacks(totalRacks) {
    this._totalRacks = totalRacks;
  }
  get totalEnergy() {
    return this._totalEnergy;
  }
  set totalEnergy(totalEnergy) {
    this._totalEnergy = totalEnergy;
  }
}

function getAllRooms() {
  let req = "";
  return new Promise((resolve, reject) => {
    Vue.http.get("/api/rooms/", req).then((res) => {
      let data = res.body;
      let rooms = [];
      data.rooms.map((item) => {
        rooms.push(Room.parseFromRestApi(item));
      })
      resolve({
        data: rooms
      })
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });

}

function getAllRowListItems() {
  return new Promise((resolve, reject) => {
    this.getAllRows().then((res) => {
      let rows = res.data;
      mapRows(rows).then((rowItems) => {
        rowItems.length>1?Collection.sortObjectsByProp(rowItems, 'index', ''):'';
        resolve({
          data: rowItems
        })
      });
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })

  })
}

function mapRows(rows){
  let rowItems = [];
  let result = Promise.resolve();
  rows.map((row) => {
    result =  result.then(() => {
      return getRowByRowId(row.rowId).then((res) => {
        rowItems.push(res.data);
      });
    })
  })
  return result.then(() => {
    return rowItems;
  })
}

function getRowByRowId(rowId){
  let req = "";
  return new Promise((resolve, reject) => {
    let url = "/api/rows/" + rowId;
    Vue.http.get(url, req).then((res) => {
      let data = res.body;
      if(data.row){
        let racks =[];
        let rowItem = Row.parseFromRestApi(data.row)
        resolve({
          data: rowItem
        })
      }
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

function getAllRows() {
  let req = "";
  return new Promise((resolve, reject) => {
    Vue.http.get("/api/rows/", req).then((res) => {
      let data = res.body;
      let rows =[];
      data.rows.map((item) => {
        rows.push(Row.parseFromRestApi(item));
      })
      resolve({
        data: rows
      })
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}



function getAllRacksByRowId(rowId) {
  let req = "";
  return new Promise((resolve, reject) => {
    let url = "/api/rows/" + rowId;
    Vue.http.get(url, req).then((res) => {
      let data = res.body;
      let racks =[];
      data.row.racks.map((item) => {
        racks.push(Rack.parseFromRestApi(item));
      })
      resolve({
        data: racks
      })
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    })
  });
}

export default {
  getAllRooms,
  getAllRows,
  getAllRacksByRowId,
  getAllRowListItems
}
