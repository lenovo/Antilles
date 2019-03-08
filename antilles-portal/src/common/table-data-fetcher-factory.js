/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import Utils from './utils'
import Collection from './collection'
import ErrorHandler from './error-handler'

// Remote pagination.
class RemotePagingTableDataFetcher {
  constructor() {
    this.restApiPath = '';
    this.restApiPropMap = null;
    this.dataParser = null;
    this.dataProp = 'data';
    this.offsetProp = 'offset';
    this.totalProp = 'total';
  }
  fetch(pageSize, currentPage, sort, filters, search) {
    return new Promise((resolve, reject) => {
      var req = {
          offset: (currentPage - 1) * pageSize,
          length: pageSize,
          filters: filters
      };
      if(sort && sort.prop && sort.prop.length > 0 && sort.order) {
        req.sort = sort;
      }
      if(search && search.props.length > 0 && search.keyword.length > 0) {
        req.search = search;
      }
      if(this.restApiPropMap) {
        if(req.sort) {
          req.sort.prop = this.restApiPropMap(req.sort.prop);
        }
        if(req.filters) {
          req.filters.forEach((filter) => {
            filter.prop = this.restApiPropMap(filter.prop);
          });
        }
        if(req.search) {
          var mappedProps = [];
          req.search.props.forEach((prop) => {
            mappedProps.push(this.restApiPropMap(prop));
          });
          req.search.props = mappedProps;
        }
      }
      var args = JSON.stringify(req)
      Vue.http.get(this.restApiPath, {params: {args: args}}).then((res) => {
          var result = null;
          if(this.dataParser) {
            result = this.dataParser(res.body);
          } else {
            result = res;
          }
          var dataItems = result[this.dataProp];
          resolve({
            data: dataItems,
            total: result[this.totalProp],
            pageSize: pageSize,
            // currentPage: Math.floor(result[this.offsetProp] / pageSize) + 1
            currentPage: currentPage
          });
        },
        (res) => {
          this._status = res.status;
          ErrorHandler.restApiErrorHandler(res, reject);
        }
      );
    });
  }
  get restApiPath() {
    return this._restApiPath;
  }
  set restApiPath(restApiPath) {
   this._restApiPath = restApiPath;
  }
  get restApiPropMap() {
    return this._restApiPropMap;
  }
  set restApiPropMap(restApiPropMap) {
    this._restApiPropMap = restApiPropMap;
  }
  get dataParser() {
    return this._dataParser;
  }
  set dataParser(dataParser) {
   this._dataParser = dataParser;
  }
  get status() {
    return this._status;
  }
}

// Local pagination.
class LocalPagingTableDataFetcher {
  constructor() {
    this.restApiPath = '';
    this.dataParser = null;
    this.dataProp = 'data';
    this.dataSorter = null;
  }
  fetch(pageSize, currentPage, sort, filters, search) {
    return new Promise((resolve, reject) => {
      Vue.http.get(this.restApiPath).then((res) => {
          var result = null;
          if(this.dataParser) {
            result = this.dataParser(res.body);
          } else {
            result = res;
          }
          var dataItems = result[this.dataProp];
          // Do filter
          // filters.forEach((filter) => {
          //   dataItems = Collection.filterObjectsByProp(dataItems, filter.prop, filter.type, filter.values);
          // });
          var filterData = []
          filters.forEach((filter) => {
            var d = Collection.filterObjectsByProp(dataItems, filter.prop, filter.type, filter.values);
            for (var i = 0; i < d.length; i++) {
              var exist = JSON.stringify(filterData).indexOf(JSON.stringify(d[i])) > -1
              if (!exist) {
                filterData.push(d[i])
              }
            }
          });
          if (filters.length > 0) {
            dataItems = filterData
          }
          // Do search
          if(search && search.keyword != '') {
            dataItems = Collection.searchObjectsByProps(dataItems, search.props, search.keyword);
          }
          // Do sort
          if(sort && sort.prop && sort.order) {
            if(this.dataSorter) {
              if(this.dataSorter(dataItems, sort.prop, sort.order) == false) {
                Collection.sortObjectsByProp(dataItems, sort.prop, sort.order);
              }
            } else {
              Collection.sortObjectsByProp(dataItems, sort.prop, sort.order);
            }
          }
          var total = dataItems.length;
          var newPage = currentPage;
          if(pageSize > 0) {
            // Do paging, not enough pages should shift to page 1.
            if(dataItems.length <= (pageSize * (currentPage - 1))) {
              newPage = 1;
            }
            var startIndex = pageSize * (newPage - 1);
            var endIndex = pageSize * newPage;
            dataItems = dataItems.slice(startIndex, endIndex);
          }
          resolve({
            data: dataItems,
            total: total,
            pageSize: pageSize,
            currentPage: newPage
          });
        },
        (res) => {
          this._status = res.status;
          ErrorHandler.restApiErrorHandler(res, reject);
        }
      );
    });
  }
  get restApiPath() {
    return this._restApiPath;
  }
  set restApiPath(restApiPath) {
   this._restApiPath = restApiPath;
  }
  get dataParser() {
    return this._dataParser;
  }
  set dataParser(dataParser) {
   this._dataParser = dataParser;
  }
  get dataProp() {
    return this._dataProp;
  }
  set dataProp(dataProp) {
   this._dataProp = dataProp;
  }
  get dataSorter() {
    return this._dataSorter;
  }
  set dataSorter(dataSorter) {
    this._dataSorter = dataSorter;
  }
  get status() {
    return this._status;
  }
}

// Local pagination with no refresh
class FixLocalPagingTableDataFetcher {
  constructor() {
    this.data = null;
    this.dataSorter = null;
  }
  fetch(pageSize, currentPage, sort, filters, search) {
    return new Promise((resolve, reject) => {
        var dataItems = [];
        if(this.data) {
          this.data.forEach((item) => {
            dataItems.push(item);
          });
        }
        // Do filter
        // filters.forEach((filter) => {
        //   dataItems = Collection.filterObjectsByProp(dataItems, filter.prop, filter.type, filter.values);
        // });
        var filterData = []
        filters.forEach((filter) => {
          var d = Collection.filterObjectsByProp(dataItems, filter.prop, filter.type, filter.values);
          for (var i = 0; i < d.length; i++) {
            var exist = JSON.stringify(filterData).indexOf(JSON.stringify(d[i])) > -1
            if (!exist) {
              filterData.push(d[i])
            }
          }
        });
        if (filters.length > 0) {
          dataItems = filterData
        }
        // Do search
        if(search && search.keyword != '') {
          dataItems = Collection.searchObjectsByProps(dataItems, search.props, search.keyword);
        }
        // Do sort
        if(sort && sort.prop && sort.order) {
          if(this.dataSorter) {
            if(this.dataSorter(dataItems, sort.prop, sort.order) == false) {
              Collection.sortObjectsByProp(dataItems, sort.prop, sort.order);
            }
          } else {
            Collection.sortObjectsByProp(dataItems, sort.prop, sort.order);
          }
        }
        var total = dataItems.length;
        var newPage = currentPage;
        if(pageSize > 0) {
          // Do paging, not enough pages should shift to page 1.
          if(dataItems.length <= (pageSize * (currentPage - 1))) {
            newPage = 1;
          }
          var startIndex = pageSize * (newPage - 1);
          var endIndex = pageSize * newPage;
          dataItems = dataItems.slice(startIndex, endIndex);
        }
        resolve({
          data: dataItems,
          total: total,
          pageSize: pageSize,
          currentPage: newPage
        });
    });
  }
  get data() {
    return this._data;
  }
  set data(data) {
   this._data = data;
  }
  get dataSorter() {
    return this._dataSorter;
  }
  set dataSorter(dataSorter) {
    this._dataSorter = dataSorter;
  }
  get status() {
    return null;
  }
}

function createRemotePagingFetcher(restApiPath, restApiPropMap, dataParser, dataProp, offsetProp, totalProp) {
  var fetcher = new RemotePagingTableDataFetcher();
  fetcher.restApiPath = restApiPath;
  if(restApiPropMap) {
    fetcher.restApiPropMap = restApiPropMap;
  }
  if(dataParser) {
    fetcher.dataParser = dataParser;
  }
  if(dataProp) {
    fetcher.dataProp = dataProp;
  }
  if(offsetProp) {
    fetcher.offsetProp = offsetProp;
  }
  if(totalProp) {
    fetcher.totalProp = totalProp;
  }
  return fetcher;
}

function createLocalPagingFetcher(restApiPath, dataParser, dataProp, dataSorter) {
  var fetcher = new LocalPagingTableDataFetcher();
  fetcher.restApiPath = restApiPath;
  if(dataParser) {
    fetcher.dataParser = dataParser;
  }
  if(dataProp) {
    fetcher.dataProp = dataProp;
  }
  if(dataSorter) {
    fetcher.dataSorter = dataSorter;
  }
  return fetcher;
}

function createFixLocalPagingFetcher(data, dataSorter) {
  var fetcher = new FixLocalPagingTableDataFetcher();
  fetcher.data = data;
  if(dataSorter) {
    fetcher.dataSorter = dataSorter;
  }
  return fetcher;
}

export default {
  createRemotePagingFetcher,
  createLocalPagingFetcher,
  createFixLocalPagingFetcher
}
