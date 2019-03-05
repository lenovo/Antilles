/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import Parser from '../common/parser'
import ErrorHandler from '../common/error-handler'
import TableDataFetcherFactory from '../common/table-data-fetcher-factory'


function downloadWebLog() {
  return new Promise((resolve, reject) => {
    Vue.http.post('/api/logs/collect').then((res) => {
      window.open('/download/'+res.body.name);
    }, (res) => {

    })
  });
}

export default {
  downloadWebLog
}
