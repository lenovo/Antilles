/*
 * Copyright © 2019-present Lenovo
 *
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

const path = require('path')
const Proxy = require('./config/proxy')

const webpack = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin')
// const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const FilterWarningsPlugin = require('webpack-filter-warnings-plugin');


module.exports = {

  publicPath: './',

  outputDir: 'dist',
  assetsDir: 'static',
  indexPath: 'index.html',
  filenameHashing: true,

  // productionSourceMap: false,
  
  configureWebpack: {

    // cheap-module-eval-source-map is faster for development
    devtool: process.env.NODE_ENV !== 'production' ? '#cheap-module-eval-source-map': false,
    
    output: {
      filename: 'static/js/[name].[hash].js',
      chunkFilename: 'static/js/[id].[hash].js'
    },

    resolve: {
      alias: {
        'vue$': 'vue/dist/vue.common.js',
        jquery: "jquery/src/jquery",
        'src': path.join(__dirname, 'src'),
        'assets': path.join(__dirname, 'src/assets'),
        'components': path.join(__dirname, 'src/components')
      }
    },

    plugins: [

      new HtmlWebpackPlugin({
        template: 'index.html',
        inject: true,
        minify: {
          removeComments: true,
          collapseWhitespace: true,
          removeAttributeQuotes: true
          // more options:
          // https://github.com/kangax/html-minifier#options-quick-reference
        },
        // necessary to consistently work with multiple chunks via CommonsChunkPlugin
        chunksSortMode: 'dependency'
      }),
      
      new FilterWarningsPlugin({
        exclude: /mini-css-extract-plugin[^]*Conflicting order between:/,
      }),

      // new MiniCssExtractPlugin({
      //   // Options similar to the same options in webpackOptions.output
      //   // both options are optional
      //   filename: "static/css/[name].[hash].css",
      //   chunkFilename: "static/css/[id].[hash].css"
      // }),

      new webpack.optimize.MinChunkSizePlugin({
        minChunkSize: 1024000 // Minimum number of characters
      }),

      // copy custom static assets
      new CopyWebpackPlugin([
        {
          from: 'static',
          to: 'static',
          toType: 'dir',
          ignore: ['.*']
        }
      ])
    ],
    optimization: {
      splitChunks: {
        name: 'vendor',
        chunks: "all",
        cacheGroups: {
          vendors: {
            test: /[\\/]node_modules[\\/]/, // 匹配node_modules目录下的文件
            priority: -10 // 优先级配置项
          },
          default: {
            minChunks: 2,
            priority: -20, // 优先级配置项
            reuseExistingChunk: true
          }
        }
      }
    }
   
  },

  chainWebpack: config => {
    config
      .plugin('html')
      .tap(args => {
        args[0].template = 'index.html'
        return args
      })

  },
  // css: {
  //   sourceMap: process.env.NODE_ENV !== 'production'?true:false

  // },

  devServer: {

    host: 'localhost',
    port: 8080,
    proxy: Proxy,

    compress: false,
    open: true,

    contentBase: path.join(__dirname, "static")
  }
}