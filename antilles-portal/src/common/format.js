/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

function baseFormatMoney(number, decimalPlaces, currencySymbol, thousandsSeparator, decimalSeparator) {
  decimalPlaces = !isNaN(decimalPlaces = Math.abs(decimalPlaces)) ? decimalPlaces : 2;
  currencySymbol = currencySymbol !== undefined ? currencySymbol : "$";
  thousandsSeparator = thousandsSeparator || ",";
  decimalSeparator = decimalSeparator || ".";
  var negative = number < 0 ? "-" : "",
    i = parseInt(number = Math.abs(+number || 0).toFixed(decimalPlaces), 10) + "",
    j = (j = i.length) > 3 ? j % 3 : 0;
  return currencySymbol + negative + (j ? i.substr(0, j) + thousandsSeparator : "") +
    i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + thousandsSeparator) +
    (decimalPlaces ? decimalSeparator + Math.abs(number - i).toFixed(decimalPlaces).slice(2) : "");
}

// (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423
// (new Date()).Format("yyyy-M-d h:m:s.S")      ==> 2006-7-2 8:9:4.18
function baseFormatDate(date, fmt) {
  var o = {
    "M+": date.getMonth() + 1,
    "d+": date.getDate(),
    "h+": date.getHours(),
    "m+": date.getMinutes(),
    "s+": date.getSeconds(),
    "q+": Math.floor((date.getMonth() + 3) / 3),
    "S": date.getMilliseconds()
  };
  if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (date.getFullYear() + "").substr(4 - RegExp.$1.length));
  for (var k in o)
    if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
  return fmt;
}

function formatCount(number) {
  if (number == 0) {
    return '-';
  }
  return number;
}

function formatMoney(number) {
  // return baseFormatMoney(number, 2, window.gApp.$t('Currency.Symbol'), ',', '.');
  return baseFormatMoney(number, 2, window.gApp.$store.getters['settings/getCurrency'], ',', '.');
}

function formatComputingTime(number) {
  return baseFormatMoney(number, 2, '', ',', '.');
}

function formatDateTime(date, format) {
  if(!format)
    format = 'yyyy-MM-dd hh:mm';
  if(date) {
    return baseFormatDate(date, format);
  }
  return '-';
}

function formatDuration(duration, LoginTime) {
  var seconds = duration % 60;
  var minutes = (duration % 3600 - duration % 60) / 60;
  var hours = (duration - duration % 3600) / 3600;
  var s = LoginTime == 'login_after_time'?','+seconds+'s':'';
  if(minutes <= 0 && hours <= 0) {
    return LoginTime == 'login_after_time'?seconds+'s':"<1m";
  }
  if(hours <= 0) {
    return minutes+'m'+s;
  }
  return hours+'h,'+minutes+'m'+s;
}

// unit: pb, tb, gb, mb, kb, b
function formatByteSize(bytes, unit) {
  var formatList = {
    b: Math.round(bytes),
    kb: bytes / Math.pow(2, 10),
    mb: bytes / Math.pow(2, 20),
    gb: bytes / Math.pow(2, 30),
    tb: bytes / Math.pow(2, 40),
    pb: bytes / Math.pow(2, 50)
  }
  var unitKeys = ['pb', 'tb', 'gb', 'mb', 'kb', 'b']
  if (unitKeys.includes(unit)) {
    var size = Math.round(formatList[unit] * 10) / 10
  } else {
    var i = 0
    while (i < unitKeys.length) {
      var unit = unitKeys[i]
      var size = Math.round(formatList[unit] * 10) / 10
      if (size >= 1) {
        break
      }
      i++
    }
  }
  return size + ' ' + unit.toUpperCase()
}

function formatNumber(number, digit) {
  var multi = Math.pow(10, digit)
  return Math.round(number * multi) / multi
}

function dos2unix(content) {
  var re = /(\r\n)/g;
  return content.replace(re,"\n");
}

function formatEnergy(number, unit) {
  return (number/unit).toFixed(1);
}

export default {
  formatCount,
  formatMoney,
  formatComputingTime,
  formatDateTime,
  formatByteSize,
  formatDuration,
  formatNumber,
  formatEnergy,
  dos2unix
}
