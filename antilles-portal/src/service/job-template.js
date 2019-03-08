/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import ErrorHandler from '../common/error-handler'
import Collection from '../common/collection'
import Format from '../common/format'

const JobTemplateTypeEnums = ['system', 'private', 'public'];


class JobTemplate {
  constructor() {
    this.code = '';
    this.name = '';
    this.logo = '';
    this.description = '';
    this.category = '';
    this.featureCode = '';
    this.type = '';
    this.userId = 0;
  }
  static parseFromStatic(jsonObj) {
    var jobTemplate = new JobTemplate();
    jobTemplate.code = jsonObj.code;
    jobTemplate.name = jsonObj.name;
    jobTemplate.logo = jsonObj.logoUrl;
    jobTemplate.description = jsonObj.description;
    jobTemplate.category = jsonObj.category;
    jobTemplate.featureCode = jsonObj.featureCode;
    jobTemplate.type = 'system';
    jobTemplate.userId = 0;
    if(jsonObj.hypervisor) {
      jobTemplate.hypervisor = jsonObj.hypervisor;
    }
    if(jsonObj.framework) {
      jobTemplate.framework = jsonObj.framework;
    }
    if(jsonObj.params) {
      jobTemplate.params = jsonObj.params;
    }
    if(jsonObj.resourceOptions) {
      jobTemplate.resourceOptions = jsonObj.resourceOptions;
    }
    if(jsonObj.notifyOptions) {
      jobTemplate.notifyOptions = jsonObj.notifyOptions;
    }
    if(jsonObj.template_file) {
      jobTemplate.templateFileContent = jsonObj.template_file;
    }
    if(jsonObj.subTemplates) {
      jobTemplate.subTemplates = jsonObj.subTemplates;
    } else {
      jobTemplate.subTemplates = []
    }
    return jobTemplate;
  }
  static parseFromRestApi(jsonObj) {
    var jobTemplate = new JobTemplate();
    jobTemplate.code = String(jsonObj.id);
    jobTemplate.name = jsonObj.name;
    jobTemplate.logo = jsonObj.logo;
    jobTemplate.description = jsonObj.desc;
    jobTemplate.category = jsonObj.category;
    jobTemplate.featureCode = jsonObj.feature_code;
    jobTemplate.type = jsonObj.type.toLowerCase();
    jobTemplate.userId = jsonObj.user_id;
    if(jsonObj.parameters_json) {
      jobTemplate.params = JSON.parse(jsonObj.parameters_json);
    }
    if(jsonObj.template_file) {
      jobTemplate.templateFileContent = jsonObj.template_file;
    }
    if(jsonObj.workspace) {
      jobTemplate.workspace = jsonObj.workspace;
    }
    return jobTemplate;
  }
  get code() {
    return this._code;
  }
  set code(code) {
   this._code = code;
  }
  get name() {
    return this._name;
  }
  set name(name) {
   this._name = name;
  }
  get logo() {
    return this._logo;
  }
  set logo(logo) {
   this._logo = logo;
  }
  get description() {
    return this._description;
  }
  set description(description) {
   this._description = description;
  }
  get category() {
    return this._category;
  }
  set category(category) {
    this._category = category;
  }
  get featureCode() {
    return this._featureCode;
  }
  set featureCode(featureCode) {
    this._featureCode = featureCode;
  }
  get type() {
    return this._type;
  }
  set type(type) {
    this._type = type;
  }
  get userId() {
    return this._userId;
  }
  set userId(userId) {
    this._userId = userId;
  }
}

function getDefaultIcons(){
  return new Promise((resolve, reject) => {
    Vue.http.get('../../static/image/job-templates/icons/default-icons.json').then((res) => {
      resolve(eval('(' + res.bodyText + ')'))
    },(res) => {
      ErrorHandler.restApiErrorHandler(res, reject);
    });
  });
}

function getAllJobTemplates() {
  return new Promise((resolve, reject) => {
    var restApiReq = Vue.http.get('/api/jobtemplates/');
    var staticReq = Vue.http.get('/static/job-template/job-templates.json');
    Promise.all([restApiReq, staticReq]).then((res) => {
        var jobTemplates = [];
        res[1].body.forEach((obj) => {
          if(!obj.hasOwnProperty('enable') || obj.enable == true) {
            jobTemplates.push(JobTemplate.parseFromStatic(obj));
          }
        });
        res[0].body.data.forEach((obj) => {
           jobTemplates.push(JobTemplate.parseFromRestApi(obj));
        });
        filterTemplatesByFeatureCodes(jobTemplates, window.gApp.$store.state.auth.featureCodes);
        resolve(jobTemplates);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function filterTemplatesByFeatureCodes(templates, featureCodes) {
  var removeArr = [];
  for(var i=0; i<templates.length; i++) {
    if(templates[i].type == 'system' && featureCodes.indexOf(templates[i].featureCode) < 0) {
      removeArr.push(templates[i]);
    }
  }
  for(var i=0; i<removeArr.length; i++) {
    Collection.removeByValue(templates, removeArr[i]);
  }
}

function getJobTemplate(code) {
  // If code is not a number, it must be the static template
  if(isNaN(parseInt(code))) {
    return new Promise((resolve, reject) => {
      Vue.http.get('/static/job-template/' + code + '.json').then((res) => {
          var jobTemplate = JobTemplate.parseFromStatic(res.body);
          resolve(jobTemplate);
        },
        (res) => {
          ErrorHandler.restApiErrorHandler(res, reject);
        }
      );
    });
  }
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/jobtemplates/' + code + '/').then((res) => {
        var jobTemplate = JobTemplate.parseFromRestApi(res.body);
        resolve(jobTemplate);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function createJobTemplate(name, logo, description, params, templateFileContent) {
  return new Promise((resolve, reject) => {
    var req = {
      name: name,
      logo: logo,
      desc: description,
      parameters_json: JSON.stringify(params),
      template_file: Format.dos2unix(templateFileContent)
    };
    Vue.http.post('/api/jobtemplates/', req).then((res) => {
        var jobTemplate = JobTemplate.parseFromRestApi(res.body);
        resolve(jobTemplate);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function updateJobTemplate(code, name, logo, description, params, templateFileContent) {
  return new Promise((resolve, reject) => {
    var req = {
      name: name,
      logo: logo,
      desc: description,
      parameters_json: JSON.stringify(params),
      template_file: Format.dos2unix(templateFileContent)
    };
    Vue.http.put('/api/jobtemplates/' + code + '/', req).then((res) => {
        var jobTemplate = JobTemplate.parseFromRestApi(res.body);
        resolve(jobTemplate);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function deleteJobTemplate(code) {
  return new Promise((resolve, reject) => {
    Vue.http.delete('/api/jobtemplates/' + code + '/').then((res) => {
        var jobTemplate = new JobTemplate();
        jobTemplate.code = code;
        resolve(jobTemplate);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function publishJobTemplate(code, category) {
  return new Promise((resolve, reject) => {
    var req = {
      category: category
    };
    Vue.http.post('/api/jobtemplates/' + code + '/publish/', req).then((res) => {
        var jobTemplate = JobTemplate.parseFromRestApi(res.body);
        resolve(jobTemplate);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function unpublishJobTemplate(code, category) {
  return new Promise((resolve, reject) => {
    Vue.http.post('/api/jobtemplates/' + code + '/unpublish/').then((res) => {
        var jobTemplate = JobTemplate.parseFromRestApi(res.body);
        resolve(jobTemplate);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

export default {
	getAllJobTemplates,
  getJobTemplate,
  createJobTemplate,
  updateJobTemplate,
  deleteJobTemplate,
  publishJobTemplate,
  unpublishJobTemplate,
  getDefaultIcons
}
