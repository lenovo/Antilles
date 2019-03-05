/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import Parser from '../common/parser'
import TableDataFetcherFactory from "../common/table-data-fetcher-factory"
import ErrorHandler from '../common/error-handler'

class BillGroup {
  constructor() {
    this.id = 0;
    this.name = '';
    this.chargeRate = 1.0;
    this.totalComputingTime = 0;
    this.accountConsumed = 0.00;
    this.accountBalance = 0.00;
    this.description = '';
    this.updateTime = new Date(0);
  }
  static parseFromRestApi(jsonObj) {
    var billGroup = new BillGroup();
    billGroup.id = jsonObj.id;
    billGroup.name = jsonObj.name;
    billGroup.chargeRate = jsonObj.charge_rate;
    billGroup.totalComputingTime = jsonObj.used_time;
    billGroup.accountConsumed = jsonObj.used_credits;
    billGroup.accountBalance = jsonObj.balance;
    billGroup.description = jsonObj.description;
    billGroup.updateTime = Parser.parseTimeFromRestApi(jsonObj.last_operation_time);
    return billGroup;
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
  get chargeRate() {
    return this._chargeRate;
  }
  set chargeRate(chargeRate) {
   this._chargeRate = chargeRate;
  }
  get totalComputingTime() {
    return this._totalComputingTime;
  }
  set totalComputingTime(totalComputingTime) {
   this._totalComputingTime = totalComputingTime;
  }
  get accountConsumed() {
    return this._accountConsumed;
  }
  set accountConsumed(accountConsumed) {
   this._accountConsumed = accountConsumed;
  }
  get accountBalance() {
    return this._accountBalance;
  }
  set accountBalance(accountBalance) {
   this._accountBalance = accountBalance;
  }
  get description() {
    return this._description;
  }
  set description(description) {
   this._description = description;
  }
  get updateTime() {
    return this._updateTime;
  }
  set updateTime(updateTime) {
   this._updateTime = updateTime;
  }
}

function billGroupsTableDataParser(res) {
  var billGroups = [];
  res.forEach((item) => {
    billGroups.push(BillGroup.parseFromRestApi(item));
  });
  return {
    data: billGroups
  };
}

function getBillGroupsTableDataFetcher() {
  return TableDataFetcherFactory.createLocalPagingFetcher('/api/billgroups', billGroupsTableDataParser, 'data');
}

function getAllBillGroups() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/billgroups').then((res) => {
        var billGroups = [];
        res.body.forEach((obj) => {
          billGroups.push(BillGroup.parseFromRestApi(obj));
        });
        resolve(billGroups);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getBillGroupById(id) {
  return new Promise((resolve, reject) => {
    Vue.http.get(`/api/billgroups/${id}`).then((res) => {
        resolve(BillGroup.parseFromRestApi(res.body.data));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function createBillGroup(name, chargeRate, accountInitAmount, description) {
  return new Promise((resolve, reject) => {
    var req = {
      name: name,
      charge_rate: chargeRate,
      balance: accountInitAmount,
      description: description
    };
    Vue.http.post('/api/billgroups', req).then((res) => {
        resolve(BillGroup.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function updateBillGroup(id, name, chargeRate, description) {
  return new Promise((resolve, reject) => {
    var req = {
      name: name,
      charge_rate: chargeRate,
      description: description
    };
    Vue.http.patch(`/api/billgroups/${id}`, req).then((res) => {
        resolve(BillGroup.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function deleteBillGroup(id) {
  return new Promise((resolve, reject) => {
    Vue.http.delete(`/api/billgroups/${id}`).then((res) => {
        resolve(BillGroup.parseFromRestApi(res.body));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function operateAccount(billGroupId, changeAmount) {
  return new Promise((resolve, reject) => {
    var req = {
      user: window.gApp.$store.state.auth.username,
      bill_group: billGroupId,
      credits: changeAmount
    };
    Vue.http.post('/api/deposit/', req).then((res) => {
      resolve(BillGroup.parseFromRestApi(res.body.bill_group));
    },
    (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    });
  });
}

export default {
  BillGroup,
  getBillGroupsTableDataFetcher,
  getAllBillGroups,
  getBillGroupById,
  createBillGroup,
  updateBillGroup,
  deleteBillGroup,
  operateAccount
}
