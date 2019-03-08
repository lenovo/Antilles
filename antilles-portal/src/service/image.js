/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import Vue from 'vue'
import Parser from '../common/parser'
import TableDataFetcherFactory from '../common/table-data-fetcher-factory'
import ErrorHandler from '../common/error-handler'

class Image {
  constructor() {
    this.id = 0;
    this.name = '';
    this.status = '';
    this.fileSize = 0;
    this.type = '';
    this.description = '';
    this.filePath = '';
    this.deployName = '';
    this.username = '';
    this.userId = 0;
    this.downloadStatus = '';
    this.imagePath = '';
  }
  static parseFromRestApi(jsonObj) {
    var image = new Image();
    image.id = jsonObj.id;
    image.name = jsonObj.name;
    image.status = jsonObj.status;
    image.fileSize = jsonObj.size_mb * Math.pow(2, 20);
    image.type = jsonObj.type;
    image.description = jsonObj.description;
    image.filePath = jsonObj.file_path;
    image.deployName = jsonObj.deploy_name;
    image.username = jsonObj.user_name;
    image.userId = jsonObj.user_id;
    image.hypervisorType = jsonObj.hypervisor_type;
    image.framework = jsonObj.framework_type;
    image.reason = jsonObj.reason
    image.imagePath = jsonObj.image_path
    return image;
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
  get status() {
    return this._status;
  }
  set status(status) {
    this._status = status;
  }
  get downloadStatus() {
    return this._downloadStatus;
  }
  set downloadStatus(downloadStatus) {
    this._downloadStatus = downloadStatus;
  }
  get fileSize() {
    return this._fileSize;
  }
  set fileSize(fileSize) {
    this._fileSize = fileSize;
  }
  get description() {
    return this._description;
  }
  set description(description) {
    this._description = description;
  }
  get type() {
    return this._type;
  }
  set type(type) {
    this._type = type;
  }
  get username() {
    return this._username;
  }
  set username(username) {
    this._username = username;
  }
  get filePath() {
    return this._filePath;
  }
  set filePath(filePath) {
    this._filePath = filePath;
  }
  get imagePath() {
    return this._imagePath;
  }
  set imagePath(imagePath) {
    this._imagePath = imagePath;
  }
  get deployName() {
    return this._deployName;
  }
  set deployName(deployName) {
    this._deployName = deployName;
  }
  get userId() {
    return this._userId;
  }
  set userId(userId) {
    this._userId = userId;
  }
  get framework() {
    return this._framework;
  }
  set framework(framework) {
    this._framework = framework;
  }
  get hypervisorType() {
    return this._hypervisorType;
  }
  set hypervisorType(hypervisorType) {
    this._hypervisorType = hypervisorType;
  }
  get reason() {
    return this._reason;
  }
  set reason(reason) {
    this._reason = reason;
  }
}

function imagesTableDataParser(res) {
  var images = [];
  res.data.forEach((item) => {
    images.push(Image.parseFromRestApi(item));
  });
  return {
    data: images
  };
}

function getImagesTableDataFetcher() {
  // return TableDataFetcherFactory.createRemotePagingFetcher('/api/ai/images/', imagesRestApiPropMap, imagesTableDataParser, 'data', 'offset', 'total');
  return TableDataFetcherFactory.createLocalPagingFetcher('/api/ai/images/', imagesTableDataParser, 'data');
}

function getAllImages() {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/ai/images/').then((res) => {
        var images = [];
        res.body.data.forEach((obj) => {
          images.push(Image.parseFromRestApi(obj));
        });
        resolve(images);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      });
  });
}

function getImageById(id) {
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/ai/image/' + id + '/').then((res) => {
        resolve(Image.parseFromRestApi(res.body.data));
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function createImage(name, filePath, description, hypervisorType, framework) {
  return new Promise((resolve, reject) => {
    var req = {
      name: name,
      file_path: filePath,
      description: description,
      hypervisor_type: hypervisorType,
      framework_type: framework
    };
    Vue.http.post('/api/ai/images/', JSON.stringify(req)).then((res) => {
        resolve(res.body.data);
        // dockerImage res ?
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function deleteImage(id) {
  return new Promise((resolve, reject) => {
    var req = {
      id: id
    };
    Vue.http.patch('/api/ai/image/' + id + '/', req).then((res) => {
        // var image = Image.parseFromRestApi(res.body.data)
        resolve(res.body);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function deployImage(id) {
  return new Promise((resolve, reject) => {
    Vue.http.put('/api/ai/image/' + id + '/').then((res) => {
        resolve(res.body.data);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function downloadImage(id, path) {
  var req = {
    target_path: path.replace('MyFolder/', '')
  };
  return new Promise((resolve, reject) => {
      Vue.http.get('/api/ai/image/' + id + '/download/', {params: req}).then((res) => {
        var data = res.body.data
        resolve(data);
      },
      (res) => {
        var message = res.body.detail
        ErrorHandler.restApiErrorHandler(data, reject);
      }
    );
  });
}

function copyImage(id, name) {
  var req = {
    name: name
  };
  return new Promise((resolve, reject) => {
    Vue.http.put('/api/ai/image/' + id + '/copy/', JSON.stringify(req)).then((res) => {
        resolve(res.body.data);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}

function getImageExist(id, path) {
  var req = {
    target_path: path
  }
  return new Promise((resolve, reject) => {
    Vue.http.get('/api/ai/image/' + id + '/exist/', {params: req}).then((res) => {
          resolve(res.body.data);
      },
      (res) => {
        ErrorHandler.restApiErrorHandler(res, reject);
      }
    );
  });
}



export default {
  getImagesTableDataFetcher,
  getAllImages,
  getImageById,
  createImage,
  deleteImage,
  deployImage,
  downloadImage,
  getImageExist,
  copyImage
}
