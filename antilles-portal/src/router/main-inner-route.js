/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

export default [{
    path: 'login-ldap',
    meta: {
      auth: true,
      access: ['admin']
    },
    component: resolve => require(['../view/login-ldap'], resolve)
  },
  {
    path: 'dashboard-monitor',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/dashboard-monitor'], resolve)
  },
  {
    path: 'dashboard-job',
    meta: {
      auth: true,
      access: ['staff']
    },
    component: resolve => require(['../view/dashboard-job'], resolve)
  },
  {
    path: 'user-group-manage',
    meta: {
      auth: true,
      access: ['admin'],
      ldap: 'optional'
    },
    component: resolve => require(['../view/user-group-manage'], resolve)
  },
  {
    path: 'user-manage',
    meta: {
      auth: true,
      access: ['admin'],
      ldap: 'optional'
    },
    component: resolve => require(['../view/user-manage'], resolve)
  },
  {
    path: 'bill-group-manage',
    meta: {
      auth: true,
      access: ['admin']
    },
    component: resolve => require(['../view/bill-group-manage'], resolve)
  },
  {
    path: 'job-template-store/:code?',
    meta: {
      auth: true,
      access: ['staff']
    },
    component: resolve => require(['../view/job-template-store'], resolve)
  },
  {
    path: 'monitor-nodes',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/monitor-nodes'], resolve)
  },
  {
    path: 'monitor-racks',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/monitor-racks'], resolve)
  },
  {
    path: 'monitor-groups',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/monitor-groups'], resolve)
  },
  {
    path: 'monitor-gpus',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/monitor-gpus'], resolve)
  },
  {
    path: 'job-manage/:status?',
    meta: {
      auth: true,
      access: ['admin', 'operator', 'staff']
    },
    component: resolve => require(['../view/job-manage'], resolve)
  },
  {
    path: 'alarm-manage',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/alarm-manage'], resolve)
  },
  {
    path: 'operation-manage',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/operation-manage'], resolve)
  },
  {
    path: 'scheduler-manage',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/scheduler-manage'], resolve)
  },
  {
    path: 'report-job',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/job-report'], resolve)
  },
  {
    path: 'report-alarm',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/report-alarm'], resolve)
  },
  {
    path: 'report-operation',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/operation-report'], resolve)
  },
  {
    path: 'vnc-manage',
    meta: {
      auth: true,
      access: ['admin', 'staff']
    },
    component: resolve => require(['../view/vnc-manage'], resolve)
  },
  {
    path: 'file-manage',
    meta: {
      auth: true,
      access: ['staff']
    },
    component: resolve => require(['../view/file-manage'], resolve)
  },
  {
    path: 'operation-log-manage',
    meta: {
      auth: true,
      access: ['admin']
    },
    component: resolve => require(['../view/operation-log-manage'], resolve)
  },
  {
    path: 'web-log-manage',
    meta: {
      auth: true,
      access: ['admin']
    },
    component: resolve => require(['../view/web-log-manage'], resolve)
  },
  {
    path: 'alarm-policy-manage',
    meta: {
      auth: true,
      access: ['admin']
    },
    component: resolve => require(['../view/alarm-policy-manage'], resolve)
  },
  {
    path: 'notify-group-manage',
    meta: {
      auth: true,
      access: ['admin']
    },
    component: resolve => require(['../view/notify-group-manage'], resolve)
  },
  {
    path: 'notify-adapter-manage',
    meta: {
      auth: true,
      access: ['admin']
    },
    component: resolve => require(['../view/notify-adapter-manage'], resolve)
  },
  {
    path: 'alarm-script-manage',
    meta: {
      auth: true,
      access: ['admin']
    },
    component: resolve => require(['../view/alarm-script-manage'], resolve)
  },
  {
     path: 'job/:id',
     meta: {
       auth: true,
       access: ['admin', 'operator', 'staff']
     },
     component: resolve => require(['../view/job'], resolve)
  },
  {
    path:'job-template/:code',
    meta: {
      auth: true,
      access: ['admin', 'staff']
    },
    component: resolve => require(['../view/job-template'], resolve)
  },
  {
    path:'job-template-ex/:code',
    meta: {
      auth: true,
      access: ['admin', 'staff']
    },
    component: resolve => require(['../view/job-template-ex'], resolve)
  },
  {
    path:'job-template/resume/:jobId',
    meta: {
      auth: true,
      access: ['admin', 'staff']
    },
    component: resolve => require(['../view/job-template'], resolve)
  },
  {
    path: 'job-template-editor',
    meta: {
      auth: true,
      access: ['admin', 'staff']
    },
    component: resolve => require(['../view/job-template-editor'], resolve)
  },
  {
    path: 'job-template-editor/copy/:code',
    meta: {
      auth: true,
      access: ['admin', 'staff']
    },
    component: resolve => require(['../view/job-template-editor'], resolve)
  },
  {
    path: 'job-template-editor/:code',
    meta: {
      auth: true,
      access: ['admin', 'staff']
    },
    component: resolve => require(['../view/job-template-editor'], resolve)
  },
  {
    path: 'rack/:id',
    meta: {
      auth: true,
      access: ['admin', 'operator']
    },
    component: resolve => require(['../view/rack'], resolve)
  },
  {
    path: 'user/:id',
    meta: {
      auth: true,
      access: ['admin']
    },
    component: resolve => require(['../view/user'], resolve)
  },
  {
    path: 'expert-mode',
    meta: {
      auth: true,
      access: ['staff']
    },
    component: resolve => require(['../view/expert-mode'], resolve)
  }
]
