/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from "vue"
import ErrorHandler from '../common/error-handler'
import utils from '../common/utils'

function toUTC(time){
	var now = new Date(time);
	return Date.UTC(now.getFullYear() , now.getMonth() , now.getDate() , now.getHours() , now.getMinutes());
}

let reportType = {
	'alarm':"alarm",
	'job':"jobs",
	'log':"operation",
	'node':"node",
	'user':"user",
	'billgroup':"bill",
	"node_running":"node_running",
	"node_user":"node_user",
	"user_login":"user_login",
	"user_storage":"user_storage"};
let levelToRest = {
	"all":"0",
	"fatal":"1",
	"error":"2",
	"warn":"3",
	"info":"4"
};

function toReportUrl(type , content , name , format){
	switch(type){
		case 'job':
			return reportType[name]+'_'+content+'.'+format;
		case 'alarm':
			return 'alarm'+'_'+content+'.'+format;
		case 'operation':
			var log_content = name == 'log' ? 'details' : content;
			return reportType[name]+'_'+log_content+'.'+format;
		default:
			break;
	}
}


class report {
	constructor() {
		this.type = 'job';
		this.report = 'job';
		this.content = 'statistics';
		this.format = 'xls';
		this.level = "all";
		this.user = [];
		this.node = [];
		this.billGroup = [];
		this.startTime = new Date(0);
		this.endTime = new Date(0);
	}
	//定义属性，定义属性方法
	static toRestApi(form){
		var reportForm = {};
		var now = new Date();
		var reportName = form.reportType == 'job' ? 'job_type' : 'operation_type';
		reportForm.url = toReportUrl(form.reportType, form.filterData.content, form.filterData[reportName] , form.format);
		reportForm.event_level = levelToRest[form.filterData.level];
		reportForm.job_user = form.filterData.user;
		reportForm.node = form.filterData.node;
		reportForm.bill = form.filterData.billGroup;
		reportForm.monitor_type = form.filterData.monitor_type;
		var now = new Date();
		reportForm.start_time = isNaN(form.start_time) ? 0 : form.start_time/1000;
		reportForm.end_time = isNaN(form.end_time) ? 0 : form.end_time/1000;
		reportForm.creator = gApp.$store.state.auth.username;
		reportForm.language = gApp.$i18n.locale;
		if(reportForm.language=='zh') {
			reportForm.language = 'sc';
		}
		reportForm.page_direction = form.direction;
		// Backend not need create time
		// reportForm.create_time = toUTC(now.valueOf());
		reportForm.timezone_offset = now.getTimezoneOffset();
		return reportForm;
	}
	get type() {
	  return this._type;
	}
	set type(type) {
	 this._type = type;
	}
	get report() {
	  return this._report;
	}
	set report(report) {
	 this._report = report;
	}
	get content() {
	  return this._content;
	}
	set content(content) {
	 this._content = content;
	}
	get format() {
	  return this._format;
	}
	set format(format) {
	 this._format = format;
	}
	get level() {
	  return this._level;
	}
	set level(level) {
	 this._level = level;
	}
	get user() {
	  return this._user;
	}
	set user(user) {
	 this._user = user;
	}
	get node() {
	  return this._node;
	}
	set node(node) {
	 this._node = node;
	}
	get billGroup() {
	  return this._billGroup;
	}
	set billGroup(billGroup) {
	 this._billGroup = billGroup;
	}
	get startTime() {
	  return this._startTime;
	}
	set startTime(startTime) {
	 this._startTime = startTime;
	}
	get endTime() {
	  return this._endTime;
	}
	set endTime(endTime) {
	 this._endTime = endTime;
	}
}
// 发送请求，接收后台数据
function createReport(form){
	var req = report.toRestApi(form);
	return new Promise((resolve, reject) => {
		Vue.http.post('/api/report/'+ req.url, req).then((res) => {
			var reportUrl = '/download/'+res.data.data;
			resolve(reportUrl);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function previewJobReport(form){
	var name= form.job_type == "billgroup"?form.billgroup:form.user;
	var now = new Date();
	var para = {
				filters: JSON.stringify(name),
				start_time: form.start_time/1000,
				end_time  : form.end_time/1000,
				timezone_offset : now.getTimezoneOffset()
			};
	var type = form.job_type == "billgroup"?"bill_group":form.job_type;
	return new Promise((resolve, reject) => {
		Vue.http.get('/api/report/job/'+type, {params:para}
		).then((res) => {
			resolve(res.data.data);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}
class ReportAlarm {
	constructor(){
		this.alarmTime=new Date(0);
		this.numTotal=0;
		this.critical=0;
		this.error=0;
		this.warning=0;
		this.info=0;
	}

	static parseReportAlarm(obj){
		var reportAlarm = new ReportAlarm();
		 	reportAlarm.alarm_time = obj.alarm_time,
			reportAlarm.numTotal = obj.num_total,
			reportAlarm.critical = obj.critical,
			reportAlarm.error = obj.error,
			reportAlarm.warning = obj.warning,
			reportAlarm.info = obj.info
		return ReportAlarm
	}
	get alarmTime() {
	  return this._alarmTime;
	}
	set alarmTime(alarmTime) {
	 this._alarmTime = alarmTime;
	}
	get numTotal() {
	  return this._numTotal;
	}
	set numTotal(numTotal) {
	 this._numTotal = numTotal;
	}
	get critical() {
	  return this._critical;
	}
	set critical(critical) {
	 this._critical = critical;
	}
	get error() {
	  return this._error;
	}
	set error(error) {
	 this._error = error;
	}
	get warning() {
	  return this._warning;
	}
	set warning(warning) {
	 this._warning = warning;
	}
	get info() {
	  return this._info;
	}
	set info(info) {
	 this._info = info;
	}

}

// 调后台的数据接口，处理后台数据
function alarmReport(form){
	var para = {
		start_time: form.start_time,
		end_time  : form.end_time,
		timezone_offset:form.timezone_offset
	};
	return new Promise((resolve, reject) => {
		Vue.http.get('/api/report/alarm/', {params:para}).then((res) => {
		var reportAlarmUrl=[];
		res.data.data.forEach((item) => {
			reportAlarmUrl.push(item);
		})
		resolve(reportAlarmUrl);
		// console.log(res);
		}, (res) => {
		ErrorHandler.restApiErrorHandler(res, reject);
		resolve(res);
		});
	});
}

let log_type = {
	"cpu":"cpu",
	"mem":"memory",
	"net":"network"
};

function previewLogReport(form){
	var type= log_type[form.monitor_type];
	var now = new Date();
	var para = {
					filters: JSON.stringify(form.node),
					timezone_offset : now.getTimezoneOffset()
				};
	return new Promise((resolve, reject) => {
		Vue.http.get('/api/report/operation/'+type, {params:para}
		).then((res) => {
			resolve(res.data.data);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

export default {
	createReport,
	previewJobReport,
	alarmReport,
	previewLogReport
}
