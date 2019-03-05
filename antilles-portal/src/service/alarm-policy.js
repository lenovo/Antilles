/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import TableDataFetcherFactory from "../common/table-data-fetcher-factory"
import ErrorHandler from '../common/error-handler'
import utils from '../common/utils'
import Vue from 'vue'
import Collection from '../common/collection'

const AlarmPolicyLevelEnums = ['fatal', 'error', 'warn', 'info'];
const AlarmPolicyStatusEnums = ['on', 'off'];
const AlarmTriggerMonitorEnums = ['CPU', 'GPU','Temperature','GPU_Temperature', 'Network', 'Disk', 'Electric', 'Hardware'];
const AlarmTriggerTypeEnums = ['Greater', 'Lower', 'Equal', 'Off', 'Error'];

var AlarmLevelToParse = {
		'50': 'fatal',
		'40': 'error',
		'30': 'warn',
		'20': 'info'
	},
	AlarmTriggerMonitorToParse = {
		'CPUSAGE': 'CPU',
		'GPU_UTIL':'GPU',
		'TEMP': 'Temperature',
		'GPU_TEMP':'GPU_Temperature',
		// 'GPU_MEM':'GMEM',
		'NODE_ACTIVE': 'Network',
		'DISK': 'Disk',
		'ELECTRIC': 'Electric',
		'HARDWARE': 'Hardware'
	},
	AlarmTriggerTypeToParse = {
		'$gt': 'Greater',
		'$lt': 'Lower',
		'$eq': 'Equal',
		'off': 'Off',
		'error': 'Error'
	};

function getKeys(obj) {
	var keys = [];
	for (var key in obj) {
		keys.push(key);
	}
	return keys;
}

function findKey(obj, val) {
	for (var key in obj) {
		if (obj[key] == val) {
			return key;
		}
	}
}

class AlarmTrigger {
	constructor() {
		this.monitor = '';
		this.type = '';
		this.value = '';
		this.duration = 0;
	}
	static toRestApi(alarmTrigger , operation , id) {
		var portal = {};
		var node = alarmTrigger.node,
			email = alarmTrigger.email.trim().replace('，', ',').split(','),
			sms = alarmTrigger.sms.trim().replace('，', ',').split(',');
		if (node.length < 1 || (node.length == 1 && node[0] == "")) {
			node = ['all'];
		}
		portal[findKey(AlarmTriggerTypeToParse, alarmTrigger.condition)] = Number(alarmTrigger.value) * alarmTrigger.AlarmInputRole.seed;
		return {
			id: id,
			name: alarmTrigger.name,
			metric: findKey(AlarmTriggerMonitorToParse, alarmTrigger.monitor),
			duration: parseFloat(alarmTrigger.duration),
			level: Number(findKey(AlarmLevelToParse, alarmTrigger.level)),
			nodes: node,
			wechat: alarmTrigger.wechat,
			sound: alarmTrigger.sound,
			status: alarmTrigger.status ? 'ON' : 'OFF',
			operation: operation,
			script: alarmTrigger.script,
			targets: alarmTrigger.nogify,
			language: gApp.$i18n.locale,
			portal
		}
	}
	static parseFromRestApi(jsonObj) {
		var alarmTrigger = new AlarmTrigger();
		alarmTrigger.monitor = AlarmTriggerMonitorToParse[jsonObj.metric];
		var unit = getTriggerInputRole(alarmTrigger.monitor);
		alarmTrigger.type = AlarmTriggerTypeToParse[getKeys(jsonObj.portal)[0]];
		alarmTrigger.value = !utils.isUndefined(alarmTrigger.type) ? Math.round(Number(jsonObj.portal[getKeys(jsonObj.portal)[0]])/unit.seed) : '';
		alarmTrigger.duration = String(jsonObj.duration);
		return alarmTrigger;
	}
}

class AlarmPolicy {
	constructor() {
		this.id = 0;
		this.name = '';
		this.type = 'CPU';
		this.level = '';
		this.status = 'OFF';
		this.node = [];
		this.email = '';
		this.sms = '';
		this.wechat = false;
		this.sound = false;
		this.targets = [];
		this.trigger = new AlarmTrigger();
	}
	static parseFromRestApi(jsonObj) {
		var alarmPolicy = new AlarmPolicy();
		alarmPolicy.id = jsonObj.id;
		alarmPolicy.name = jsonObj.name;
		alarmPolicy.level = AlarmLevelToParse[String(jsonObj.level)];
		alarmPolicy.status = jsonObj.status == 'ON' ? true : false;
		alarmPolicy.node = jsonObj.nodes == 'all' ? [] : jsonObj.nodes;
		alarmPolicy.targets = jsonObj.targets;
		alarmPolicy.email = !utils.isUndefined(jsonObj.email) ? jsonObj.policy_email.toString() : '';
		alarmPolicy.sms = !utils.isUndefined(jsonObj.sms) ? jsonObj.policy_sms.toString() : '';
		alarmPolicy.wechat = jsonObj.wechat;
		alarmPolicy.sound = jsonObj.sound;
		alarmPolicy.script = jsonObj.script;
		alarmPolicy.trigger = AlarmTrigger.parseFromRestApi(jsonObj);
		return alarmPolicy;
	}
	get id() {
		return this._id;
	}
	set id(id) {
		this._id = id;
	}
	get name() {
		return this._name;
	}
	set name(name) {
		this._name = name;
	}
	get type() {
		return this._type;
	}
	set type(type) {
		this._type = type;
	}
	get level() {
		return this._level;
	}
	set level(level) {
		this._level = level;
	}
	get status() {
		return this._status;
	}
	set status(status) {
		this._status = status;
	}
	get node() {
		return this._node;
	}
	set node(node) {
		this._node = node;
	}
	get targets() {
		return this._targets;
	}
	set targets(targets) {
		this._targets = targets;
	}
	get email() {
		return this._email;
	}
	set email(email) {
		this._email = email;
	}
	get sms() {
		return this._sms;
	}
	set sms(sms) {
		this._sms = sms;
	}
	get wechat() {
		return this._wechat;
	}
	set wechat(wechat) {
		this._wechat = wechat;
	}
	get sound() {
		return this._sound;
	}
	set sound(sound) {
		this._sound = sound;
	}
	get trigger() {
		return this._trigger;
	}
	set trigger(trigger) {
		this._trigger = trigger;
	}
}

function alarmPolicyTableDataParser(res) {
  var alarmPolicies = [];
  res.forEach((item) => {
    alarmPolicies.push(AlarmPolicy.parseFromRestApi(item));
  });
  return {
    data: alarmPolicies
  };
}

function alarmPolicyTableDataSorter(dataItems, prop, order) {
	if(prop == 'level') {
		function compareLevel(objA, objB) {
	    var indexA = AlarmPolicyLevelEnums.indexOf(objA.level);
	    var indexB = AlarmPolicyLevelEnums.indexOf(objB.level);
	    if (indexA > indexB) {
	      return -1;
	    } else if (indexA < indexB) {
	      return 1;
	    } else {
	      return 0;
	    }
	  };
		Collection.sortObjectsByProp(dataItems, prop, order, compareLevel);
		return true;
	}
	return false;
}

function getAlarmPolicyTableDataFetcher() {
	return TableDataFetcherFactory.createLocalPagingFetcher('/api/alarm/policy', alarmPolicyTableDataParser, 'data', alarmPolicyTableDataSorter);
}

function createAlarmPolicy(alarmPolicy) {
	return new Promise((resolve, reject) => {
		var req = AlarmTrigger.toRestApi(alarmPolicy,'create',null);
		Vue.http.post('/api/alarm/policy', req).then((res) => {
				resolve(AlarmPolicy.parseFromRestApi(res.data));
			},
			(res) => {
				ErrorHandler.restApiErrorHandler(res, reject);
			}
		);
	});
}

function getAlarmPolicyById(id) {
	return new Promise((resolve, reject) => {
		Vue.http.get('/api/alarm/policy/' + id).then((res) => {
				var alarmPolicy = AlarmPolicy.parseFromRestApi(res.data);
				resolve(alarmPolicy);
			},
			(res) => {
				ErrorHandler.restApiErrorHandler(res, reject);
			}
		);
	});
}

function updateAlarmPolicy(id, alarmPolicy) {
	return new Promise((resolve, reject) => {
		var req = AlarmTrigger.toRestApi(alarmPolicy,'update',id);
		Vue.http.put('/api/alarm/policy/' + id , req).then((res) => {
				var alarmPolicy = AlarmPolicy.parseFromRestApi(res.data);
				resolve(alarmPolicy);
			},
			(res) => {
				ErrorHandler.restApiErrorHandler(res, reject);
			}
		);
	});
}

function deleteAlarmPolicy(id) {
	return new Promise((resolve, reject) => {
		Vue.http.delete('/api/alarm/policy/' + id).then((res) => {
				var alarmPolicy = AlarmPolicy.parseFromRestApi(res.data);
				resolve(alarmPolicy);
			},
			(res) => {
				ErrorHandler.restApiErrorHandler(res, reject);
			}
		);
	});
}

// const AlarmTriggerMonitorEnums = ['CPUSAGE', 'TEMP', 'NODE_ACTIVE', 'DISK', 'ELECTRIC', 'HARDWARE'];

function getTriggerInputRole(monitor) {
	switch (monitor) {
		case 'CPU':
		case 'GPU':
		case 'Disk':
			return {
				typeOptions: ['Greater', 'Lower'],
				value: true,
				duration: true,
				unit: '%',
				seed: 0.01
			}
		case 'Temperature':
		case 'GPU_Temperature':
			return {
				typeOptions: ['Greater', 'Lower'],
				value: true,
				duration: true,
				unit: '℃',
				seed: 1
			}
		case 'GMEM':
			return {
				typeOptions: ['Greater', 'Lower'],
				value: true,
				duration: true,
				unit: 'GB',
				seed: 1024
			}
		case 'Electric':
			return {
				typeOptions: ['Greater', 'Lower'],
				value: true,
				duration: true,
				unit: 'W',
				seed: 1
			}
		default:
			return {
				typeOptions: ['Off', 'Error'],
				value: false,
				duration: true,
				unit: '',
				seed: 1
			}
	}
}

export default {
	AlarmLevelToParse,
	AlarmPolicyLevelEnums,
	AlarmTriggerMonitorEnums,
	getAlarmPolicyTableDataFetcher,
	createAlarmPolicy,
	getAlarmPolicyById,
	updateAlarmPolicy,
	deleteAlarmPolicy,
	getTriggerInputRole
}
