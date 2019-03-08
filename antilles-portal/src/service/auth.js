/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import JWTDecode from 'jwt-decode'
import AccessService from './access'
import ErrorHandler from '../common/error-handler'
import store from '../storage/store'

function login(username, password) {
  return new Promise((resolve, reject) => {
    var req = {
      user: username,
      pass: password
    };
    Vue.http.post('/api/auth', req).then((res) => {
      var token = res.body.token;
      var info = JWTDecode(token);
      var role = info.role;
      if(role=='user') {
        role = 'staff';
      }
      var availableAccess = AccessService.getAvailableAccessByRole(role);
      if(availableAccess.length > 0) {
        window.gApp.$store.dispatch('auth/login', {
          username: info.sub,
          userid: info.id,
          token: token,
          role: role,
          access: availableAccess[0],
          ldap: ''
        });
        window.gApp.$store.dispatch('settings/init');
        resolve();
      } else {
        reject("No available access.");
      }
    },
    (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    });
  });
}

function refreshToken() {
  return new Promise((resolve, reject) => {
    Vue.http.post('/api/auth').then((res) => {
      var token = res.body.token;
      var info = JWTDecode(token);
      var role = info.role;
      if(role=='user') {
        role = 'staff';
      }
      var availableAccess = AccessService.getAvailableAccessByRole(role);
      if(availableAccess.length > 0) {
        window.gApp.$store.dispatch('auth/setToken', {
          username: info.sub,
          userid: info.id,
          token: token,
          role: role
        });
        resolve();
      } else {
        reject("No available access.");
      }
    },
    (res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    });
  });
}

function logout() {
  window.CloseTerminals();
  window.stopAsync();
  window.gApp.$store.dispatch('auth/logout');
  window.gApp.$router.push({ path: '/login' });
}

function loginLDAP(username, password) {
  return new Promise((resolve, reject) => {
    var info = {"username": username,"password": password};
    var b64EncodeUnicode = function(str) {
        return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, function(match, p1) {
            return String.fromCharCode('0x' + p1);
        }));
    };
    var ldap = b64EncodeUnicode(JSON.stringify(info));
    window.gApp.$store.dispatch('auth/setLDAP', ldap);
    Vue.http.get('/api/user/backend-auth').then((res) => {
      resolve(username);
    },
    (res) => {
      window.gApp.$store.dispatch('auth/setLDAP', '');
      ErrorHandler.restApiErrorHandler(res, reject);
    });
  });
}

function isLogin() {
  var token = store.state.auth.token;
  var role = store.state.auth.role;
  var access = store.state.auth.access;
  if (token == '' || role == '' || access == '') {
    return false;
  } else {
    return true;
  }
}

function isLDAPLogin() {
  var ldap = store.state.auth.ldap;
  if (ldap == '') {
    return false;
  } else {
    return true;
  }
}

function changePassword(currentPassword, password) {
  return new Promise((resolve, reject) => {
    var req = {
      new_password: password,
      old_password: currentPassword
    };
    Vue.http.patch('/api/password/', req).then((res) => {
        resolve();
        //resolve(User.parseFromRestApi(res.body));
      },
      (res) => {
        if(res.status == 401) {
          reject(window.gApp.$t('Auth.ChangePassword.Error.CurrentPassword'));
        } else {
          ErrorHandler.restApiErrorHandler(res, reject);
        }
      }
    );
  });
}

function checkConfig() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/config/').then((res) => {
        window.gApp.$store.dispatch('auth/setLDAPManaged',
        {
          ldapManaged: res.body.user.managed,
          ldapDefaultUsername: res.body.user.ldap_root_dn
        });
        // Setup feature codes
        var featureCodes = ['antilles', 'hpc'];
        if(res.body.scheduler && res.body.scheduler.type === 'slurm') {
          featureCodes.push('scheduler.slurm');
        }
        // load local feature codes
        getLocalFeatureCodes().then((res) => {
          featureCodes = featureCodes.concat(res);
          window.gApp.$store.dispatch('auth/setFeatureCodes',
            {
              featureCodes: featureCodes
            });
          resolve();
        });
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getLocalFeatureCodes() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/static/feature-codes.json').then((res) => {
        resolve(res.body);
      },
      (res) => {
        console.log("Can't get local feature codes");
        resolve([]);
      }
    );
  });
}

function isLDAPManaged() {
  return store.state.auth.ldapManaged;
}

function getVersion() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/static/version.json').then((res) => {
        resolve(res.body.version);
      },
      (res) => {
        reject("Can't get version");
      }
    );
  });
}


export default {
  login,
  logout,
  loginLDAP,
  isLogin,
  isLDAPLogin,
  changePassword,
  checkConfig,
  isLDAPManaged,
  refreshToken,
  getVersion
}
