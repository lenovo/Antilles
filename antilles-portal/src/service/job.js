/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from "vue"
import TableDataFetcherFactory from "../common/table-data-fetcher-factory"
import ErrorHandler from '../common/error-handler'
import Parser from '../common/parser'
import Format from '../common/format'

const JobStatusEnums = ['completed', 'queueing', 'creating', 'running', 'suspending', 'waiting', 'holding', 'error', 'cancelled', 'createfailed'];
const JobWebStatusEnums = {
	running: [ 'running'],
	waiting: [ 'queueing', 'suspending', 'waiting', 'holding' ],
	finished: [ 'completed', 'error', 'cancelled', 'createfailed']
};
const JobActionEnums = ['browse', 'cancel', 'rerun', 'delete', 'hold', 'release', 'pause', 'resume'];

class Job {
	constructor() {
		this.id = 0;
		this.schedulerId = 0;
		this.submitUser = "";
		this.name = "";
		this.queue = "";
		this.submitTime = new Date(0);
		this.beginTime = new Date(0);
		this.finishTime = new Date(0);
		this.status = "";
		this.operateStatus = "";
		this.type = "";
		this.workingDirectory = "";
		this.workspace = "";
		this.jobFilename = "";
		this.modelId = 0;
		this.datasetId = 0;
		this.numberOfCpuCores = 0;
		this.numberOfNodes = 0;
		this.execHosts = '';
		this.req = null;
		this.numberOfGpus = 0;
		this.gpuExecHosts = '';
		this.outputFilename = null;
	}
	static parseFromRestApi(jsonObj) {
		var job = new Job();
		job.id = jsonObj.id;
		job.schedulerId = jsonObj.jobid;
		job.submitUser = jsonObj.submiter;
		job.name = jsonObj.jobname;
		job.queue = jsonObj.queue;
	  job.submitTime = Parser.parseTimeFromRestApi(jsonObj.qtime);
		job.beginTime = Parser.parseTimeFromRestApi(jsonObj.starttime);
		job.finishTime = Parser.parseTimeFromRestApi(jsonObj.endtime);
		job.status = jsonObj.status.toLowerCase();
		if(jsonObj.operatestatus) {
			job.operateStatus = jsonObj.operatestatus.toLowerCase();
		}
		job.type = jsonObj.type;
		job.workingDirectory = jsonObj.workingdir;
		job.workspace = jsonObj.workspace;
		job.jobFilename = jsonObj.jobfilename;
		if(jsonObj.model_id) {
			job.modelId = jsonObj.model_id;
		}
		if(jsonObj.datasource_id) {
			job.datasetId = jsonObj.datasource_id;
		}
		if(jsonObj.cpuscount) {
			job.numberOfCpuCores = jsonObj.cpuscount;
		}
		if(jsonObj.nodescount) {
			job.numberOfNodes = jsonObj.nodescount;
		}
		if(jsonObj.exechosts) {
			job.execHosts = jsonObj.exechosts;
		}
		if(jsonObj.gpuscount) {
			job.numberOfGpus = jsonObj.gpuscount;
		}
		if(jsonObj.gpusexechosts) {
			job.gpuExecHosts = jsonObj.gpusexechosts;
		}
		if(jsonObj.json_body && jsonObj.json_body != '') {
			var params = new Object();
			var requestParams = new Object();
			var notifyParams = new Object();
			parseJobReq(JSON.parse(jsonObj.json_body), params, requestParams, notifyParams);
			job.req = {
				params: params,
				requestParams: requestParams,
				notifyParams: notifyParams
			}
		}
		if(jsonObj.outfile) {
			job.outputFilename = jsonObj.outfile;
		}
		return job;
	}
	// Computed property
	get waitDuration() {
		if(JobWebStatusEnums.waiting.indexOf(this.status) >= 0) {
			return Math.round((new Date() - this.submitTime) / 1000);
		} else {
			return Math.round((this.beginTime - this.submitTime) / 1000);
		}
	}
	get runDuration() {
		if(JobWebStatusEnums.waiting.indexOf(this.status) >= 0) {
			return 0;
		} else if(JobWebStatusEnums.running.indexOf(this.status) >= 0) {
			return Math.round((new Date() - this.beginTime) / 1000);
		} else {
			return Math.round((this.finishTime - this.beginTime) / 1000);
		}
	}
	// Getter and Setter
	get id() {
	  return this._id;
	}
	set id(id) {
	 this._id = id;
	}
	get schedulerId() {
	  return this._schedulerId;
	}
	set schedulerId(schedulerId) {
	 this._schedulerId = schedulerId;
	}
	get submitUser() {
	  return this._submitUser;
	}
	set submitUser(submitUser) {
	 this._submitUser = submitUser;
	}
	get name() {
	  return this._name;
	}
	set name(name) {
	 this._name = name;
	}
	get queue() {
	  return this._queue;
	}
	set queue(queue) {
	 this._queue = queue;
	}
	get submitTime() {
	  return this._submitTime;
	}
	set submitTime(submitTime) {
	 this._submitTime = submitTime;
	}
	get beginTime() {
	  return this._beginTime;
	}
	set beginTime(beginTime) {
	 this._beginTime = beginTime;
	}
	get finishTime() {
	  return this._finishTime;
	}
	set finishTime(finishTime) {
	 this._finishTime = finishTime;
	}
	get status() {
	  return this._status;
	}
	set status(status) {
	 this._status = status;
	}
	get operateStatus() {
		return this._operateStatus;
	}
	set operateStatus(operateStatus) {
		this._operateStatus = operateStatus;
	}
	get type() {
	  return this._type;
	}
	set type(type) {
	 this._type = type;
	}
	get workingDirectory() {
	  return this._workingDirectory;
	}
	set workingDirectory(workingDirectory) {
	 this._workingDirectory = workingDirectory;
	}
	get workspace() {
	  return this._workspace;
	}
	set workspace(workspace) {
	 this._workspace = workspace;
	}
	get jobFilename() {
	  return this._jobFilename;
	}
	set jobFilename(jobFilename) {
	 this._jobFilename = jobFilename;
	}
	get modelId() {
		return this._modelId;
	}
	set modelId(modelId) {
		this._modelId = modelId;
	}
	get datasetId() {
		return this._datasetId;
	}
	set datasetId(datasetId) {
		this._datasetId = datasetId;
	}
	get numberOfCpuCores() {
		return this._numberOfCpuCores;
	}
	set numberOfCpuCores(numberOfCpuCores) {
		this._numberOfCpuCores = numberOfCpuCores;
	}
	get numberOfNodes() {
		return this._numberOfNodes;
	}
	set numberOfNodes(numberOfNodes) {
		this._numberOfNodes = numberOfNodes;
	}
	get execHosts() {
		return this._execHosts;
	}
	set execHosts(execHosts) {
		this._execHosts = execHosts;
	}
	get req() {
		return this._req;
	}
	set req(req) {
		this._req = req;
	}
	get numberOfGpus() {
	  return this._numberOfGpus;
	}
	set numberOfGpus(numberOfGpus) {
	 this._numberOfGpus = numberOfGpus;
	}
	get gpuExecHosts() {
	  return this._gpuExecHosts;
	}
	set gpuExecHosts(gpuExecHosts) {
	 this._gpuExecHosts = gpuExecHosts;
	}
	get outputFilename() {
		return this._outputFilename;
	}
	set outputFilename(outputFilename) {
		this._outputFilename = outputFilename;
	}
}

class RunningJob {
	constructor() {
		this.id = 0;
		this.schedulerId = 0;
		this.submitUser = "";
		this.name = "";
		this.queue = "";
		this.beginTime = new Date(0);
		this.usedCores = 0;
		this.usedGpus = 0;
	}
	static parseFromRestApi(jsonObj) {
		var job = new RunningJob();
		job.id = jsonObj.id;
		job.schedulerId = jsonObj.jobid;
		job.submitUser = jsonObj.submiter;
		job.name = jsonObj.jobname;
		job.queue = jsonObj.queue;
	  	job.beginTime = Parser.parseTimeFromRestApi(jsonObj.starttime);
		job.usedCores = jsonObj.core_num_on_node;
		if(jsonObj.gpu_num_on_node) {
			job.usedGpus = jsonObj.gpu_num_on_node;
		}
		return job;
	}
	get id() {
	  return this._id;
	}
	set id(id) {
	 this._id = id;
	}
	get schedulerId() {
	  return this._schedulerId;
	}
	set schedulerId(schedulerId) {
	 this._schedulerId = schedulerId;
	}
	get submitUser() {
	  return this._submitUser;
	}
	set submitUser(submitUser) {
	 this._submitUser = submitUser;
	}
	get name() {
	  return this._name;
	}
	set name(name) {
	 this._name = name;
	}
	get queue() {
	  return this._queue;
	}
	set queue(queue) {
	 this._queue = queue;
	}
	get beginTime() {
	  return this._beginTime;
	}
	set beginTime(beginTime) {
	 this._beginTime = beginTime;
	}
	get usedCores() {
	  return this._usedCores;
	}
	set usedCores(usedCores) {
	 this._usedCores = usedCores;
	}
	get usedGpus() {
	  return this._usedGpus;
	}
	set usedGpus(usedGpus) {
	 this._usedGpus = usedGpus;
	}
}

function jobTableDataParser(res) {
	var jobs = [];
	res.data.forEach((item) => {
		jobs.push(Job.parseFromRestApi(item));
	});
	return {
		offset: res.offset,
		total: res.total,
		data: jobs
	}
}

function jobsRestApiPropMap(prop) {
	if(prop=='schedulerId') {
		return 'jobid';
	}
	if(prop=='submitUser') {
		return 'submiter';
	}
	if(prop=='name') {
		return 'jobname';
	}
	if(prop=='submitTime') {
		return 'qtime';
	}
	if(prop=='beginTime') {
		return 'starttime';
	}
	if(prop=='finishTime') {
		return 'endtime';
	}
	if(prop=='workingDirectory') {
		return 'workingdir';
	}
	if(prop=='jobFilename') {
		return 'jobfilename';
	}
	return prop;
}

function getJobTableDataFetcher(access) {
	var api = '/api/jobs/';
	if(access == 'admin' || access == 'operator') {
		api = '/api/jobs/?role=admin';
	}
	return TableDataFetcherFactory.createRemotePagingFetcher(api, jobsRestApiPropMap, jobTableDataParser, 'data', 'offset', 'total');
}

function getJobById(id) {
	return new Promise((resolve, reject) => {
		Vue.http.get('/api/jobs/' + id).then((res) => {
			var job = Job.parseFromRestApi(res.body);
			if(!job.id) {
				job.id = id;
			}
			resolve(job);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function runningJobsTableDataParser(res) {
  var jobs = [];
  res.jobs.forEach((item) => {
    jobs.push(RunningJob.parseFromRestApi(item));
  });
  return {
    data: jobs
  };
}

function getRunningJobsTableDataFetcher(nodeId) {
	var api = '/api/nodes/' + nodeId + '/runningjobs/';
  return TableDataFetcherFactory.createLocalPagingFetcher(api, runningJobsTableDataParser, 'data');
}

function getJobLog(file, offset, lines) {
	var url = '/api/jobs/log/';
	var req = {
		file_path: file,
		line_num: offset
	};
	if(lines!=undefined){
		req.lines = lines
	}
	return new Promise((resolve, reject) => {
		Vue.http.get(url, {params: req}).then((res) => {
			var lines = [];
			if(res.body.data.log.length > 0)
				lines = res.body.data.log.split('\n')
			var result = {
				lines: lines,
				offset: res.body.data.line_num
			}
			resolve(result);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function cancelJob(id) {
	return new Promise((resolve, reject) => {
		var req = {
			'action': 'cancel'
		};
		Vue.http.put('/api/jobs/' + id +'/', req).then((res) => {
			resolve(res.body);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function deleteJob(id) {
	return new Promise((resolve, reject) => {
		var req = {
			'action': 'delete'
		};
		Vue.http.delete('/api/jobs/' + id + '/', req).then((res) => {
			resolve(res.body);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function rerunJob(id) {
	return new Promise((resolve, reject) => {
		var req = {
			'action': 'rerun',
			'id': id
		};
		Vue.http.post('/api/jobs/', req).then((res) => {
			setTimeout(function() {
				waitForJobCreated(res.body.id, resolve, reject, 10);
			}, 2000);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function holdJob(id) {
	return new Promise((resolve, reject) => {
		var req = {
			'action': 'hold'
		};
		Vue.http.put('/api/jobs/' + id +'/', req).then((res) => {
			resolve(res.body);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function releaseJob(id) {
	return new Promise((resolve, reject) => {
		var req = {
			'action': 'release'
		};
		Vue.http.put('/api/jobs/' + id +'/', req).then((res) => {
			resolve(res.body);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function pauseJob(id) {
	return new Promise((resolve, reject) => {
		var req = {
			'action': 'pause'
		};
		Vue.http.put('/api/jobs/' + id +'/', req).then((res) => {
			resolve(res.body);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function resumeJob(id, params, resourceParams) {
	return new Promise((resolve, reject) => {
		var req = {
			'action': 'resume'
		};
		Vue.http.put('/api/jobs/' + id +'/', req).then((res) => {
			// getJobById(id).then((res) => {
			// 	if(res.req == null) {
			// 		reject(window.gApp.$t('Job.Resume.NoParams'));
			// 	} else {
			// 		if(params || resourceParams) {
			// 			buildJobReq(params, resourceParams, null, res.req);
			// 		}
			// 		Vue.http.post('/api/jobs/', res.req).then((res) => {
			// 			setTimeout(function() {
			// 				waitForJobCreated(res.body.id, resolve, reject, 10);
			// 			}, 2000);
			// 		},(res) => {
			// 			ErrorHandler.restApiErrorHandler(res, reject);
			// 		});
			// 	};
			// }, (res) => {
			// 	reject(res);
			// });
			resolve(res.body);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function parseJobReq(req, params, resourceParams, notifyParams) {
	for(var key in req) {
		if(key == 'queue') {
			resourceParams['queue'] = req.queue;
		}
		if(key == 'pnodescount') {
			resourceParams['nodes'] = req.pnodescount;
		}
		if(key == 'ppn') {
			resourceParams['coresPerNode'] = req.ppn;
		}
		if(key == 'pmem') {
			resourceParams['ramSize'] = req.pmem;
		}
		if(key == 'walltime') {
			resourceParams['runTime'] = parseTimeToHours(req.walltime);
		}
		if(key == 'mailtrigger') {
			notifyParams['triggers'] = parseTriggers(req.mailtrigger);
		}
		if(key == 'mail') {
			notifyParams['email'] = req.mail;
		}
		if(['action', 'type', 'jobname'].indexOf(key) < 0) {
			params[key] = req[key];
		}
	}
}

function buildJobReq(params, resourceParams, notifyParams, req) {
	for(var key in params) {
		req[key] = params[key];
	}
	if(resourceParams.hasOwnProperty('queue') && resourceParams.queue != '') {
		req['queue'] = resourceParams.queue;
	} else {
		req['queue'] = 'compute';
	}
	if(resourceParams.hasOwnProperty('nodes')) {
		req['pnodescount'] = resourceParams.nodes;
	} else {
		req['pnodescount'] = 0;
	}
	if(resourceParams.hasOwnProperty('coresPerNode')) {
		req['ppn'] = resourceParams.coresPerNode;
	} else {
		req['ppn'] = 0;
	}
	if(resourceParams.hasOwnProperty('gpusPerNode')) {
		req['pgn'] = resourceParams.gpusPerNode;
	} else {
		req['pgn'] = 0;
	}
	if((req['ppn'] > 0 || req['pgn'] > 0) && req['pnodescount'] <= 0) {
		req['pnodescount'] = 1
	}
	if(resourceParams.hasOwnProperty('ramSize')) {
		req['pmem'] = resourceParams.ramSize;
	} else {
		req['pmem'] = 0;
	}
	if(resourceParams.hasOwnProperty('runTime')) {
		req['walltime'] = formatHoursToTime(resourceParams.runTime);
	} else {
		req['walltime'] = '';
	}
	if(notifyParams) {
		req['mailtrigger'] = notifyParams.hasOwnProperty('triggers') ? formatTriggers(notifyParams.triggers) : '';
		req['mail'] = notifyParams.hasOwnProperty('email') ? notifyParams.email : '';
	}
}

function createJob(type, name, params, resourceParams, notifyParams, resumeJobId) {
	return new Promise((resolve, reject) => {
		var req = new Object();
		req['action'] = 'create';
		if(type=='general') {
			req['type'] = 'file';
		} else {
			req['type'] = type;
		}
		req['jobname'] = name;
		if(resumeJobId) {
			req['resumejobid'] = resumeJobId;
		}
		buildJobReq(params, resourceParams, notifyParams, req);
		// console.log(req);
		Vue.http.post('/api/jobs/', req).then((res) => {
			setTimeout(function() {
				waitForJobCreated(res.body.id, resolve, reject, 10);
			}, 2000);
		},(res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function createJobEx(jobTemplate, params) {
	return new Promise((resolve, reject) => {
		var req = new Object();
		req['jobname'] = params['job_name'];
		req['template_id'] = parseInt(jobTemplate.code);
		if(isNaN(req['template_id'])) {
			req['template_id'] = jobTemplate.code;
		}
		req['parameters'] = params;
		req['template_file'] = Format.dos2unix(jobTemplate.templateFileContent);
		req['workingdir'] = params['job_workspace'];
		req['type'] = 'file';
		Vue.http.post('/api/jobs_ex/', req).then((res) => {
			setTimeout(function() {
				waitForJobCreated(res.body.id, resolve, reject, 10);
			}, 2000);
		},(res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		});
	});
}

function waitForJobCreated(jobId, resolve, reject, tryTimes) {
	 getJobById(jobId).then((res) => {
		 var job = res;
		 // console.log('waitForJob', job);
		 if(job.status != 'creating') {
			 resolve(job);
		 } else {
			 if(tryTimes > 0) {
				 setTimeout(function() {
  				 waitForJobCreated(jobId, resolve, reject, tryTimes - 1);
  			 }, 2000);
			 } else {
				 reject(window.gApp.$t('Job.Create.Error.NoSchedulerId'));
			 }
		 }
	 },(res) => {
		 reject(res);
	 });
}

function formatHoursToTime(hours) {
	var hourStr = Math.floor(hours).toString();
	var minuteStr = Math.floor(60 * (hours - Math.floor(hours))).toString();
	var secondStr = '00';
	if(hourStr.length < 1) {
		hourStr = '0' + hourStr;
	}
	if(minuteStr.length < 1) {
		minuteStr = '0' + minuteStr;
	}
	return hourStr + ':' + minuteStr + ':' + secondStr;
}

function parseTimeToHours(time) {
	var hours = 0;
	var times = time.split(':');
	hours += parseInt(times[0]);
	hours += parseInt(times[1]) / 60;
	return times;
}

function formatTriggers(triggers) {
	var result = '';
	triggers.forEach((trigger) => {
		if(trigger == 'suspend') {
			result += 'b';
		} else if(trigger == 'finish') {
			result += 'e';
		}
	});
	return result;
}

function parseTriggers(trigger) {
	var result = [];
	for(var c=0; c<trigger.length; c++) {
		if(trigger[c] == 'b') {
			result.push('suspend');
		}
		if(trigger[c] == 'e') {
			result.push('finish');
		}
	}
	return result;
}

function getJoblatest(length, status, role) {
	return new Promise((resolve, reject) => {
		var api = (role=='admin'|| role == 'operator')?'':'user/';
		status = status?status:'finished';
		var params = {
			counts: length,
			status: JobWebStatusEnums[status].toString()
		};
		Vue.http.get('/api/jobs/latest/' + api, {params: params}).then((res) => {
			var jobs = [];
			res.body.forEach((item) => {
				jobs.push(Job.parseFromRestApi(item));
			})
			resolve(jobs);
		}, (res) => {
			ErrorHandler.restApiErrorHandler(res, reject);
		})
	});
}

function getJobActionsByAccess(access) {
	if(access == 'staff') {
		return ['browse', 'cancel', 'rerun', 'delete'];
	}
	return [];
}

function getJobActions(operateStatus, status, type) {
	var actions = [];
	if(JobWebStatusEnums.running.indexOf(status) >= 0 ||
		 JobWebStatusEnums.finished.indexOf(status) >= 0) {
		actions.push('browse');
	}
	if(operateStatus != 'cancelling' &&
		 JobWebStatusEnums.finished.indexOf(status) < 0) {
	  actions.push('cancel');
	}
	if(JobWebStatusEnums.finished.indexOf(status) >= 0) {
		actions.push('rerun');
		actions.push('delete');
	}
	return actions;
}

export default {
	JobStatusEnums,
	JobWebStatusEnums,
	JobActionEnums,
	getJobTableDataFetcher,
	cancelJob,
	deleteJob,
	rerunJob,
	getJobById,
	getJobLog,
	createJob,
	getRunningJobsTableDataFetcher,
	getJoblatest,
	getJobActions,
	holdJob,
	releaseJob,
	pauseJob,
	resumeJob,
	getJobActionsByAccess,
	createJobEx
}
