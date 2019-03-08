/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import AuthService from '../service/auth'
import Format from './format'

function restApiErrorHandler(res, reject) {
  if(res.status >= 400 && res.status < 500) {
    if(res.body.errid) {
      if(res.body.errid == '2013') {
        if(res.body.detail) {
          if(res.body.detail.remain_time) {
            var try_after_time = Format.formatDuration(res.body.detail.remain_time, 'login_after_time');
            if(try_after_time.split(',').length>=3 && parseInt(try_after_time.split(',')[0])>=12) {
              reject(window.gApp.$t('Error.2013.Ban.Long'));
            }
            reject(window.gApp.$t('Error.2013.Ban', {'try_after_hours': try_after_time}));
          } else if(res.body.detail.fail_chances >= 0) {
            reject(window.gApp.$t('Error.2013.LeftTimes', {'left_times': res.body.detail.remain_chances}));
          } else {
            reject(window.gApp.$t('Error.2013'));
          }
        } else {
          reject(window.gApp.$t('Error.2013'));
        }
      } else {
        reject(window.gApp.$t('Error.' + res.body.errid));
        if(['2017', '2018', '2019', '2020', '2024'].indexOf(res.body.errid) >= 0) {
          setTimeout(() => {
            AuthService.logout();
          }, 2000);
        }
      }
    } else {
      if(res.status == 401) {
        reject(window.gApp.$t('Error.401'));
        setTimeout(() => {
          AuthService.logout();
        }, 2000);
      } else {
        if(res.body.message) {
          reject(res.body.message);
        } else {
          reject(window.gApp.$t('Error.Unknown'));
        }
      }
    }
  } else if (res.status == 502) {
    reject(window.gApp.$t('Error.RestAPI.Connection'));
  } else {
    reject(window.gApp.$t('Error.RestAPI.Unknown', {'status': res.status}));
  }
}

export default {
  restApiErrorHandler
}
