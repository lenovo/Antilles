/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

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
function getStorageOrCookie(key) {
  return storage[key]
}

function getDefaultLangCode() {
  const browserLang = (navigator.language || navigator.browserLanguage).toLowerCase();
  if(browserLang.indexOf('zh') >= 0) {
    return 'zh';
  }else {
    return 'en';
  }
}

const state = {
  isSound:        storage['isSound'],
  utilColor:  storage['utilColor'],
  gpuutil:       storage['gpuutil'],
  memoryColor:    storage['memoryColor'],
  gpumemory:         storage['gpumemory'],
  temperatureColor:   storage['temperatureColor'],
  gputemperature:        storage['gputemperature'],
  show3D: storage['show3D'],
  breadcrumbBarName: storage['breadcrumbBarName'],
  mobilePolicy: storage['mobilePolicy'],
  langCode:storage['langCode'] || getDefaultLangCode(),
  currency: storage['currency']
}

const mutations = {
  setUserConfig(state, payload){
    for (var attr in payload) {
      state[attr] = payload[attr];
      setStorageOrCookie(attr,  payload[attr]);
    }
  }
}

const actions = {
  init(context) {
		context.commit('setUserConfig', {
			isSound:        getStorageOrCookie('isSound') || false,
      gpuutil:       getStorageOrCookie('gpuutil') || '80, 95',
      utilColor:  getStorageOrCookie('utilColor') || false,
      gpumemory:         getStorageOrCookie('gpumemory') || '95, 100',
      memoryColor:    getStorageOrCookie('memoryColor') || false,
      gputemperature:        getStorageOrCookie('gputemperature') || '0, 100',
      temperatureColor:   getStorageOrCookie('temperatureColor') || false,
      show3D: getStorageOrCookie('show3D') || false,
      breadcrumbBarName: getStorageOrCookie('breadcrumbBarName') || '',
      langCode:getStorageOrCookie('langCode') || getDefaultLangCode(),
      mobilePolicy: getStorageOrCookie('mobilePolicy') || 'US',
      currency: getStorageOrCookie('currency') || '$'
		});
	},
  setStorage(context, payload) {
		context.commit('setUserConfig', payload);
  },
  setAlarmSound(context, isSound) {
    context.commit('setUserConfig', {
			isSound: setStorageOrCookie('isSound', isSound)
		});
  },
  setGpuutilColor(context, utilColor) {
    context.commit('setUserConfig', {
      utilColor: setStorageOrCookie('utilColor', utilColor)
		});
  },
  setGpuutil(context, gpuutil) {
    context.commit('setUserConfig', {
      gpuutil: setStorageOrCookie('gpuutil', gpuutil)
		});
  },
  setGpumemoryColor(context, memoryColor) {
    context.commit('setUserConfig', {
			memoryColor: setStorageOrCookie('memoryColor', memoryColor),
		});
  },
  setGpumemory(context, gpumemory) {
    context.commit('setUserConfig', {
			gpumemory: setStorageOrCookie('gpumemory', gpumemory),
		});
  },
  setGputemperatureColor(context, temperatureColor) {
    context.commit('setUserConfig', {
			temperatureColor: setStorageOrCookie('temperatureColor', temperatureColor),
		});
  },
  setGputemperature(context, gputemperature) {
    context.commit('setUserConfig', {
			gputemperature: setStorageOrCookie('gputemperature', gputemperature),
		});
  },
  setShow3D(context, show3D) {
    context.commit('setUserConfig', {
			show3D: setStorageOrCookie('show3D', show3D)
    });
  },
  setBreadcrumbBarName(context, breadcrumbBarName) {
    context.commit('setUserConfig', {
			breadcrumbBarName: setStorageOrCookie('breadcrumbBarName', breadcrumbBarName)
    });
  },
  setMobilePolicy(context, mobilePolicy) {
    context.commit('setUserConfig', {
      mobilePolicy: setStorageOrCookie('mobilePolicy', mobilePolicy)
    });
  },
  setLangCode(context,langCode){
    context.commit('setUserConfig',{
      langCode: setStorageOrCookie('langCode', langCode)
    });
  },
  setCurrency(context, currency) {
    context.commit('setUserConfig', {
			currency: setStorageOrCookie('currency', currency)
    });
  },
  clear(context) {
    context.commit('setUserConfig', {
			isSound: setStorageOrCookie('isSound', '')
		});
  }
}

const getters = {
  isSound: state => {
    if ( state.isSound == 'false' ||  state.isSound == false) {
      return false;
    } else {
      return true;
    }
  },
  getGpuutilColor: state => {
    if ( state.utilColor == 'false' ||  state.utilColor == false) {
      return false;
    } else {
      return true;
    }
  },
  getGpuutil: state => {
    if(state.gpuutil) {
      return state.gpuutil;
    } else {
      return getStorageOrCookie('gpuutil');
    }
  },
  getGpumemoryColor: state => {
    if ( state.memoryColor == 'false' ||  state.memoryColor == false) {
      return false;
    } else {
      return true;
    }
  },
  getGpumemory: state => {
    if(state.gpumemory) {
      return state.gpumemory;
    } else {
      return getStorageOrCookie('gpumemory');
    }
  },
  getGputemperatureColor: state => {
    if ( state.temperatureColor == 'false' ||  state.temperatureColor == false) {
      return false;
    } else {
      return true;
    }
  },
  getGputemperature: state => {
    if(state.gputemperature) {
      return state.gputemperature;
    } else {
      return getStorageOrCookie('gputemperature');
    }
  },
  getMobilePolicy: state => {
    if(state.mobilePolicy) {
      return state.mobilePolicy;
    } else {
      return getStorageOrCookie('mobilePolicy');
    }
  },
  getLangCode: state => {
    return state.langCode;
  },
  getCurrency: state => {
    if(state.currency) {
      return state.currency;
    } else {
      return getStorageOrCookie('currency');
    }
  }
}


const settingsModule = {
	namespaced: true,
  state: state,
  mutations: mutations,
  getters: getters,
  actions: actions
}

export default settingsModule
