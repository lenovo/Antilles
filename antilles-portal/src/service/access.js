/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Utils from '../common/utils'
import Collection from '../common/collection'
import routes from '../router/route'
import store from '../storage/store'
import menu from '../menu/menu'
import Vue from 'vue'
import ErrorHandler from '../common/error-handler'

function getAvailableAccessByRole(role) {
  if(role.toLowerCase() == 'admin') {
    return ['admin', 'operator', 'staff'];
  } else if (role.toLowerCase() == 'operator') {
    return ['operator'];
  } else if (role.toLowerCase() == 'staff') {
    return ['staff'];
  } else {
    return [];
  }
}

function shiftAccess(access) {
  if (window.gApp.$store.state.auth.access != access) {
    window.gApp.$store.dispatch('auth/setAccess', access);
    window.gApp.$router.push({ path: '/login' });
  }
}

function getMenuByAccess(access) {
  var result = [];
  if(menu[access]) {
    result = menu[access];
  }
  filterMenuForLDAP(result);
  filterMenuForFeatureCodes(result, window.gApp.$store.state.auth.featureCodes);
  return result;
}

function filterMenuForLDAP(menu) {
  var removeArr = [];
  for(var i=0; i<menu.length; i++) {
    if(checkForLDAP(menu[i].ldap)) {
      filterMenuForLDAP(menu[i].children);
    } else {
      removeArr.push(menu[i]);
    }
  }
  for(var i=0; i<removeArr.length; i++) {
    Collection.removeByValue(menu, removeArr[i]);
  }
}

function checkForLDAP(ldap) {
  if(ldap) {
    if(ldap=='force' && !store.state.auth.ldapManaged) {
      return false;
    }
  }
  return true;
}

function filterMenuForFeatureCodes(menu, featureCodes) {
  var removeArr = [];
  for(var i=0; i<menu.length; i++) {
    var menuFeatureCode = 'antilles';
    if(menu[i].featureCode) {
      menuFeatureCode = menu[i].featureCode;
    }
    if(featureCodes.indexOf(menuFeatureCode) < 0) {
      removeArr.push(menu[i]);
    } else {
      filterMenuForFeatureCodes(menu[i].children, featureCodes);
    }
  }
  for(var i=0; i<removeArr.length; i++) {
    Collection.removeByValue(menu, removeArr[i]);
  }
}

function getQuickLinkMenu(access) {
  return new Promise((resolve, reject) => {
    Vue.http.get('/config').then((res) => {
      var result = [];
      var local = JSON.parse(res.bodyText)['local'];
      if (local) {
        window.gApp.$store.dispatch('settings/setMobilePolicy', local.mobilePolicy);
        window.gApp.$store.dispatch('settings/setCurrency', local.currency);
      }
      var quickLinkMenu = JSON.parse(res.bodyText)['quick-link'];
      quickLinkMenu.forEach((menu) => {
        var newMenu = reformatQuickLinkMenu(access, menu);
        if(newMenu) {
          result.push(newMenu);
        }
      });
      resolve(result);
    }, (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    });
  });
}

function reformatQuickLinkMenu(access, menu) {
  if(menu.access) {
    var temp = access;
    if(access == 'staff') {
      temp = 'user';
    }
    if(menu.access.split(',').indexOf(temp) < 0) {
      return null;
    }
  }
  var newMenu = {
    label: menu.label,
    icon: 'Collection',
    path: menu.url,
    children: [],
    quickLink: true
  };
  if(menu.children) {
    menu.children.forEach((subMenu) => {
      var child = reformatQuickLinkMenu(access, subMenu);
      if(child) {
        newMenu.children.push(child);
      }
    });
  }
  if(newMenu.path || newMenu.children.length > 0) {
    return newMenu;
  } else {
    return null;
  }
}
function getScheduler() {
  if(window.gApp.$store.state.auth.featureCodes.includes('scheduler.slurm')){
    return 'slurm';
  }else{
    return ''
  }
}

export default {
  getAvailableAccessByRole,
  getMenuByAccess,
  shiftAccess,
  getQuickLinkMenu,
  getScheduler
}
