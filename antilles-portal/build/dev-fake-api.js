/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

var path = require('path')
var fs = require('fs')

function fakeApi(baseDir, reqPath, reqMethod) {
  var fileDir = path.join(baseDir, reqPath);
  fileDir = path.join(fileDir, reqMethod.toLowerCase());
  // Change result every second.
  var seconds = Math.round(Date.now() / 1000);
  var policyItems = parsePolicy(path.join(fileDir, ".policy"));
  // Sleep 3 seconds.
  if(policyItems.length <= 0) {
    var filenames = findFilesBySuffix(fileDir, 'json');
    var index = seconds % filenames.length;
    return JSON.parse(fs.readFileSync(path.join(fileDir, filenames[index])));
  } else {
    var index = seconds % policyItems.length;
    var policyItem = policyItems[index];
    if(policyItem.status == 200) {
      return JSON.parse(fs.readFileSync(path.join(fileDir, policyItem.body)));
    } else {
      // Need implement
    }
  }
}

function parsePolicy(policyFilename) {
  var policyItems = [];
  if(!fs.existsSync(policyFilename)) {
    return filenames;
  }
  content = fs.readFileSync(policyFilename).toString();
  lines = content.split('\n');
  lines.forEach((line) => {
    line = trim(line);
    if(line.length > 0) {
      if(isNaN(line)) {
        policyItems.push({
          status: 200,
          body: line + '.json'
        });
      } else {
        policyItems.push({
          status: parseInt(line),
          body: ''
        });
      }
    }
  });
  return policyItems;
}

function trim(str)
{
     return str.replace(/(^\s*)|(\s*$)/g, '');
}

function getFileSuffix(filename) {
  return filename.substring(filename.lastIndexOf('.') + 1);
}

function findFilesBySuffix(dir, suffix) {
  var result = new Array();
  if(fs.existsSync(dir)) {
    var dirList = fs.readdirSync(dir);
    dirList.forEach((filename, index) => {
      if(getFileSuffix(filename) == suffix) {
        result.push(filename)
      }
    });
  }
  return result;
}

module.exports = fakeApi
