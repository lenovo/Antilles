/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Session from '../common/session'


const storage =(function() {
  try {
     return 'localStorage' in window && window['localStorage'] !== null ? self.localStorage : self.cookie;
  } catch (e) {
     return self.cookie;
  }
})();

function setStorageOrCookie(key, val) {
  return storage[key] = val;
}

const state = {
  hash: '',
  dialogHash: ''
}

const mutations = {
  setHash(state, payload){
    state.hash = payload.hash;
    state.dialogHash = payload.dialogHash;
    setStorageOrCookie('elfinder-lastdir', payload.hash);
    setStorageOrCookie('elfinder-lastdireditor', payload.dialogHash);
  }
}

const actions = {
  init(context) {
		context.commit('setHash', {
			hash: setStorageOrCookie('elfinder-lastdir', ''),
      dialogHash: setStorageOrCookie('elfinder-lastdireditor', '')
		});
	},
  setStorage(context, hash) {
    context.commit('setHash', {
			hash: setStorageOrCookie('elfinder-lastdir', hash),
      dialogHash: setStorageOrCookie('elfinder-lastdireditor', hash)
		});
  },
  clear(context) {
    context.commit('setHash', {
			hash: setStorageOrCookie('elfinder-lastdir', ''),
      dialogHash: setStorageOrCookie('elfinder-lastdireditor', '')
		});
  }
}

const getters = {
  isFileManager: state => {
    if (!state.hash) {
      return false;
    } else {
      return true;
    }
  }
}


const elfinderModule = {
	namespaced: true,
  state: state,
  mutations: mutations,
  getters: getters,
  actions: actions
}

export default elfinderModule
