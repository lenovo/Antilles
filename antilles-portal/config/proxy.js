/*
 * Copyright © 2019-present Lenovo
 *
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

var host = 'localhost'

try {
  var reg = /^-([0-9]{1,3}\.){3}[0-9]{1,3}$/
  const configArgv = JSON.parse(process.env.npm_config_argv)
  const original = configArgv.original.slice(1)
  host = reg.test(original[1]) ? original[1].replace(/-/g, '') : '';
 
} catch(err) {
  // console.log(err);
  
}

console.log(host);
console.log('\n');

module.exports = {
  '/api': {
    target: 'https://' + host,
    changeOrigin: true,
    secure: false,
    pathRewrite: {
      '^/api': '/api'
    }
  },
  '/tensorboard': {
    target: 'https://' + host,
    changeOrigin: true,
    secure: false,
    pathRewrite: {
      '^/tensorboard': '/tensorboard'
    }
  },
  '/download': {
    target: 'https://' + host,
    changeOrigin: true,
    secure: false,
    pathRewrite: {
      '^/download': '/download'
    }
  },
  '/node': {
    target: 'https://' + host,
    changeOrigin: true,
    secure: false,
    pathRewrite: {
      '^/node': '/node'
    }
  },
  '/gpu': {
    target: 'https://' + host,
    changeOrigin: true,
    secure: false,
    pathRewrite: {
      '^/gpu': '/gpu'
    }
  },
  '/sessions': {
    target: 'http://' + host + ':9257',
    changeOrigin: true,
    secure: false,
    pathRewrite: {
      '^/sessions': '/sessions'
    }
  },
  '/novnc': {
    target: 'http://' + host + ':6080',
    changeOrigin: true,
    secure: false,
    pathRewrite: {
      '^/novnc': '/'
    }
  },
  '/config': {
    target: 'https://' + host,
    changeOrigin: true,
    secure: false,
    pathRewrite: {
      '^/config': '/config'
    }
  },
  '/docs': {
    target: 'https://' + host,
    changeOrigin: true,
    secure: false,
    pathRewrite: {
      '^/docs': '/docs'
    }
  },
  '/dev': {
    target: 'https://' + host,
    changeOrigin: true,
    secure: false,
    pathRewrite: {
      '^/dev': '/dev'
    }
  }
}
