/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import LibPhoneNumber from "google-libphonenumber";
const phoneUtil = LibPhoneNumber.PhoneNumberUtil.getInstance();


function getRequireRoleForText(itemLabel) {
  return {
    required: true,
    message: window.gApp.$t('Valid.Require', {'name': itemLabel})
  //  trigger: 'blur'
  };
}

function getLengthRoleForText(itemLabel, min, max) {
  return {
    min: min,
    max: max,
    message: window.gApp.$t('Valid.Text.Length', {'name': itemLabel, 'min': min, 'max': max})
    //trigger: 'blur'
  };
}

function getValidIdentityNameRoleForText(itemLabel) {
  var pattern = '^[a-zA-Z0-9_]+$';
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      var regExp = new RegExp(pattern);
      if(value.toString().length>0 && !regExp.test(value.toString())) {
        errors.push(
          new Error(window.gApp.$t('Valid.Text.Name', {'name': itemLabel}))
        )
      }
      callback(errors);
    }
  };
}

function getRequireRoleForNumber(itemLabel) {
  return {
    type: 'number',
    required: true,
    message: window.gApp.$t('Valid.Require', {'name': itemLabel})
    //trigger: 'blur'
  };
}

function getValidNumberRoleForText(itemLabel) {
  return {
    type: 'pattern',
    pattern: /^(\-|\+)?\d+(\.\d+)?$/,
    message: window.gApp.$t('Valid.Number', {'name': itemLabel})
    //trigger: 'blur'
  };
}

function getNodesExpressionRoleForText(itemLabel) {
  return {
    type: 'pattern',
    pattern: /(^(\w)+$)|(^[\w].*([\w|\]])$)/,
    message: window.gApp.$t('Valid.NodesExpression',{'name': itemLabel}),
    // trigger: 'blur'
  };
}

function getMaxTimeForText(itemLabel) {
  return {
    type: 'pattern',
    pattern: /(\d{1,3}-\d{1,2}:\d{1,2}$)|(\d{1,3}-\d{1,2}:\d{1,2}:\d{1,2}$)/,
    message: window.gApp.$t('Valid.MaxTime',{'name': itemLabel}),
    // trigger: 'blur'
  };
}

function getMaxTimeRangeRoleForText() {
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      var days = value.split('-')[0];
      var hours = value.split('-')[1].split(':')[0];
      var mins = value.split('-')[1].split(':')[1];
      if(days<0 || days>365){
        errors.push(new Error(window.gApp.$t('Valid.MaxTime.Days.Range')))
      }else if(hours<0 || hours>23){
        errors.push(new Error(window.gApp.$t('Valid.MaxTime.Hours.Range')))
      }else if(mins<0 || mins>59){
        errors.push(new Error(window.gApp.$t('Valid.MaxTime.Mins.Range')))
      }
      callback(errors);
    }
  };
}

function getNumberRangeRoleForText(itemLabel, min, max) {
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      if(value.length>0) {
        var num = parseFloat(value);
        if(num<min || num>max) {
          if(!max && max != 0) {
            errors.push(new Error(window.gApp.$t('Valid.Number.Range.Min', {'name': itemLabel, 'min': min})))
          } else if(!min && min != 0){
            errors.push(new Error(window.gApp.$t('Valid.Number.Range.Max', {'name': itemLabel, 'max': max})))
          } else {
            errors.push(
              new Error(window.gApp.$t('Valid.Number.Range', {'name': itemLabel, 'min': min, 'max': max}))
            )
          }
        }
      }
      callback(errors);
    }
  };
}

function getNumberDecimalRoleForText(itemLabel, decimal) {
  var numberPattern = '^(\\-|\\+)?\\d+(\\.\\d+)?$';
  var pattern = '^[-]?\\d+(\\.\\d{0,' + decimal + '})?$';
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      var numberRegExp = new RegExp(numberPattern);
      var regExp = new RegExp(pattern);
      if(value.length>0 && numberRegExp.test(value) && !regExp.test(value)) {
        errors.push(
          new Error(window.gApp.$t('Valid.Number.Decimal', {'name': itemLabel, 'decimal': decimal}))
        )
      }
      callback(errors);
    }
  };
}


function getRangeRoleForNumber(itemLabel, min, max) {
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      if(value.toString().length>0) {
        var num = parseFloat(value.toString());
        if(num<min || num>max) {
          errors.push(
            new Error(window.gApp.$t('Valid.Number.Range', {'name': itemLabel, 'min': min, 'max': max}))
          )
        }
      }
      callback(errors);
    }
  };
}

function getDecimalRoleForNumber(itemLabel, decimal) {
  var pattern = '^[-]?\\d+(\\.\\d{0,' + decimal + '})?$';
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      var regExp = new RegExp(pattern);
      if(value.toString().length>0 && !regExp.test(value.toString())) {
        errors.push(
          new Error(window.gApp.$t('Valid.Number.Decimal', {'name': itemLabel, 'decimal': decimal}))
        )
      }
      callback(errors);
    }
  };
}

function getRequireRoleForArray(itemLabel) {
  return {
    type: 'array',
    required: true,
    message: window.gApp.$t('Valid.Require', {'name': itemLabel}),
    trigger: 'blur'
  };
}

function getLengthRoleForArray(itemLabel, min, max) {
  return {
    type: 'array',
    min: min,
    max: max,
    message: window.gApp.$t('Valid.Array.Length', {'name': itemLabel, 'min': min, 'max': max}),
    trigger: 'blur'
  };
}

function getUniqueRoleForArray(itemLabel) {
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      if(value instanceof Array) {
        for(var i=0; i<value.length; i++) {
          for(var j=i+1; j<value.length; j++) {
            if(value[i] == value[j]) {
              errors.push(
                new Error(window.gApp.$t('Valid.Array.Unique', {'name': itemLabel}))
              )
              break;
            }
          }
          if(errors.length > 0) {
            break;
          }
        }
      }
      callback(errors);
    }
  };
}

function getEmailRole(itemLabel) {
  return {
    type: 'pattern',
    //pattern: /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+/,
    //pattern: /^([a-zA-Z0-9]+[\._-]*)+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/,
    //pattern: /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$/,
    pattern: /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/,
    message: window.gApp.$t('Valid.Email', {'name': itemLabel}),
    trigger: 'blur'
  };
}

function getPasswordRole(itemLabel) {
  var pattern = '^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z\\W_]+$)(?![a-z0-9]+$)(?![a-z\\W_]+$)(?![0-9\\W_]+$)[a-zA-Z0-9\\W_]{10,20}$';
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      var regExp = new RegExp(pattern);
      if(value.length>0 && !regExp.test(value)) {
        if(value.length < 10 || value.length > 32) {
          errors.push(new Error(window.gApp.$t('Valid.Password.Length', {'name': itemLabel})));
        } else {
          errors.push(new Error(window.gApp.$t('Valid.Password', {'name': itemLabel})));
        }
      }
      callback(errors);
    }
  };

  // return {
  //   type: 'pattern',
  //   // pattern: /^(?![a-zA-z]+$)(?!\d+$)(?![!@#$%^&*]+$)(?![a-zA-z\d]+$)(?![a-zA-z!@#$%^&*]+$)(?![\d!@#$%^&*]+$)[a-zA-Z\d!@#$%^&*]+$/,
  //   pattern: /^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z\W_]+$)(?![a-z0-9]+$)(?![a-z\W_]+$)(?![0-9\W_]+$)[a-zA-Z0-9\W_]{10,20}$/,
  //   message: window.gApp.$t('Valid.Password', {'name': itemLabel}),
  //   trigger: 'blur'
  // };
}

// function getMobileRole(itemLabel) {
//   return {
//     type: 'pattern',
//     //pattern: /^1(3[0-9]|4[57]|5[0-35-9]|8[0-9]|70)\d{8}$/,
//     pattern: /^((1[3,5,8][0-9])|(14[5,7])|(17[0,6,7,8])|(19[7]))\d{8}$/,
//     message: window.gApp.$t('Valid.Mobile', {'name': itemLabel}),
//     trigger: 'blur'
//   };
// }

function getMobileRole(itemLabel) {
  // Get country code
  const country = window.gApp.$store.getters['settings/getMobilePolicy']
  return {
    validator: (rule, value, callback) => {
      if(value.length > 0){
        try {
          var phonenumber = phoneUtil.parseAndKeepRawInput(value, country);
          var isaphone=phoneUtil.isValidNumber(phonenumber);
          if (!isaphone) {
            throw isaphone = false;
          } else {
            callback();
          }
        } catch (error) {
          callback(
            new Error(
              window.gApp.$t('Valid.Mobile', { 'name': itemLabel })
            )
          );
        }
      }
      else{
        callback();
      }
    },
    trigger: 'blur'
  };
}

function getArrayRequireForAI(itemLabel) {
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      if(value.trim() == '') {
        errors.push(
          new Error(window.gApp.$t('Valid.StepValues.Require'))
        )
      } else if (!value.trim().includes(' ')) {
        errors.push(
          new Error(window.gApp.$t('Valid.StepValues.Sequence'))
        )
      } else if (!isNaN(Number(value.trim()))) {
        errors.push(
          new Error(window.gApp.$t('Valid.StepValues.Sequence'))
        )
      }
      callback(errors);
    }
  };
}

function getArrayValidForAI(itemLabel) {
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      var n = '0123456789'
      value = value.trim()
      var numList = value.split(' ')
      var i = 0
      while (i < numList.length) {
        var num = numList[i]
        if (isNaN(Number(num))) {
          errors.push(
            new Error(window.gApp.$t('Valid.StepValues.Sequence'))
          )
          break
        }
        if (num == '') {
          errors.push(
            new Error(window.gApp.$t('Valid.StepValues.Sequence'))
          )
          break
        } else {
          i += 1
        }
      }
      if (errors.length == 0) {
        var tmp = numList[0]
        if (tmp == '0') {
          errors.push(
            new Error(window.gApp.$t('Valid.StepValues.Number'))
          )
        } else {
          for (var i = 1; i < numList.length; i++) {
            if (tmp < numList[i]) {
              tmp = numList[i]
            } else {
              errors.push(
                new Error(window.gApp.$t('Valid.StepValues.Ascend'))
              )
              break
            }
          }
        }
      }
      callback(errors);
    }
  };
}

function getSuffixValid(itemLabel, rules) {
  var str =  rules.join(', ');
  var pattern = `(${rules.join('|')})$`;
  return {
    trigger: 'blur',
    validator(rule, value, callback, source, options) {
      if(value.length > 0) {
        var errors = [new Error(window.gApp.$t('Valid.Filename.Suffix', {'name': itemLabel, 'value': str}))];
        var regExp = new RegExp(pattern, 'i');
        for (var i = 0; i < rules.length; i++) {
          if(regExp.test(value.substr(0-rules[i].length))) {
            errors = [];
            break
          }
        }
      }
      callback(errors);
    }
  };
}

function getValidSystemNameRoleForText(itemLabel, caseInsensitive) {
  var pattern = '^[a-zA-Z][a-zA-Z0-9_-]+$';
  if(!caseInsensitive) {
    pattern = '^[a-z][a-z0-9_-]+$'
  }
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      var regExp = new RegExp(pattern);
      if(value.toString().length>1 && !regExp.test(value.toString())) {
          if(caseInsensitive) {
            errors.push(new Error(window.gApp.$t('Valid.Text.SystemName', {'name': itemLabel})))
          } else {
            errors.push(new Error(window.gApp.$t('Valid.Text.SystemName.NoCaseInsensitive', {'name': itemLabel})))
          }
      }
      callback(errors);
    }
  };
}

function getValidFileName(itemLabel) {
  return {
    validator(rule, value, callback, source, options) {
      var errors = [];
      // var regExp = new RegExp(pattern);
      value = value.trim();
      var errorChars = '\\\/:*?"<>| '
      for (var i = 0; i < value.length; i++) {
        if (errorChars.includes(value[i])) {
          errors.push(new Error(window.gApp.$t('Valid.FileName')));
          break;
        }
      }
      callback(errors);
    }
  };
}

function getValidUsersName(allable, maxValue){
  return {
    validator(rule, value, callback){
      var Reg = /^[a-zA-Z0-9_,-]*$/
      if(value==''){
        if (allable){
          callback()
        } else {
          callback(new Error(window.gApp.$t('Multi.User.Required')))
        }
      }else if(!value.match(Reg)){
        callback(new Error(window.gApp.$t('Multi.User.FormatError')));
      }else if(value.split(',').length>maxValue){
        callback(new Error(window.gApp.$t('Multi.User.tooLong', {value:maxValue})));
      }else{
        callback()
      }
    },
    trigger: 'change'
  }
}

function getValidMultiSelect(allable){
  return {
    validator(rule, value, callback){
      if(value.length==0 && !allable){
        callback(new Error(window.gApp.$t('Multi.User.Required')));
      }else{
          callback()
      }
    },
    trigger: 'change'
  }
}

export default {
  getRequireRoleForText,
  getLengthRoleForText,
  getValidIdentityNameRoleForText,
  getValidNumberRoleForText,
  getNumberRangeRoleForText,
  getNumberDecimalRoleForText,
  getRequireRoleForNumber,
  getRangeRoleForNumber,
  getDecimalRoleForNumber,
  getRequireRoleForArray,
  getLengthRoleForArray,
  getUniqueRoleForArray,
  getEmailRole,
  getPasswordRole,
  getMobileRole,
  getArrayRequireForAI,
  getArrayValidForAI,
  getSuffixValid,
  getValidSystemNameRoleForText,
  getValidFileName,
  getNodesExpressionRoleForText,
  getValidUsersName,
  getValidMultiSelect,
  getMaxTimeForText,
  getMaxTimeRangeRoleForText
}
