/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import Vuex from 'vuex'
import authModule from './auth-module'
import elfinderModule from './elfinder-module'
import settings from './settings-module'

// Install Vuex into Vue
Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    auth: authModule,
    elfinder: elfinderModule,
    settings: settings
  }
});

// Export store
export default store
