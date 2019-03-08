/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

// see http://vuejs-templates.github.io/webpack for documentation.
var path = require('path')

var devProxyTable = {};
var argv = require('process').argv
if (argv && argv.length>=3) {
  var host = argv[2];
  devProxyTable = {
    '/api': {
      target: 'https://' + host,
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        '^/api':'/api'
      }
    },
    '/download': {
      target: 'https://' + host,
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        '^/download':'/download'
      }
    },
    '/node': {
      target: 'https://' + host,
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        '^/node':'/node'
      }
    },
    '/gpu': {
      target: 'https://' + host,
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        '^/gpu':'/gpu'
      }
    },
    '/sessions': {
      target: 'https://' + host + ':9257',
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        '^/sessions':'/sessions'
      }
    },
    '/novnc': {
      target: 'https://' + host + ':6080',
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        '^/novnc':'/'
      }
    },
    '/config': {
      target: 'https://' + host,
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        '^/config':'/config'
      }
    }
  }
}

module.exports = {
  build: {
    env: require('./prod.env'),
    index: path.resolve(__dirname, '../dist/index.html'),
    assetsRoot: path.resolve(__dirname, '../dist'),
    assetsSubDirectory: 'static',
    assetsPublicPath: '/',
    productionSourceMap: true,
    // Gzip off by default as many popular static hosts such as
    // Surge or Netlify already gzip all static assets for you.
    // Before setting to `true`, make sure to:
    // npm install --save-dev compression-webpack-plugin
    productionGzip: false,
    productionGzipExtensions: ['js', 'css'],
    // Run the build command with an extra argument to
    // View the bundle analyzer report after build finishes:
    // `npm run build --report`
    // Set to `true` or `false` to always turn it on or off
    bundleAnalyzerReport: process.env.npm_config_report
  },
  dev: {
    env: require('./dev.env'),
    port: 8088,
    autoOpenBrowser: true,
    assetsSubDirectory: 'static',
    assetsPublicPath: '/',
    proxyTable: devProxyTable,
    // CSS Sourcemaps off by default because relative paths are "buggy"
    // with this option, according to the CSS-Loader README
    // (https://github.com/webpack/css-loader#sourcemaps)
    // In our experience, they generally work as expected,
    // just be aware of this issue when enabling this option.
    cssSourceMap: false
  }
}
