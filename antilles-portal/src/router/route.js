/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

import mainInnerRoutes from './main-inner-route'

export default [
  {
    path: '/',
    meta: {
      auth: false
    },
    component: resolve => require(['../view/login'], resolve)
  },
  {
    path: '/login',
    meta: {
      auth: false
    },
    component: resolve => require(['../view/login'], resolve)
  },
  {
    path: '/main',
    meta: {
      auth: true,
      access: ['admin', 'operator', 'staff']
    },
    component: resolve => require(['../view/main'], resolve),
    children: [].concat(mainInnerRoutes)
  }
]
