/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

export default [
  {
    label: 'JobDashboard',
    icon: 'home',
    path: '/main/dashboard-job',
    home: true
  },
  {
    label: 'JobTemplateStore',
    icon: 'jobtemplates',
    path: '/main/job-template-store',
    details: [
      {
        type: 'job-template-editor-copy',
        param: 'code',
        path: '/main/job-template-editor/copy'
      },
      {
        type: 'job-template-editor',
        param: 'code',
        path: '/main/job-template-editor'
      },
      {
        type: 'job-template',
        param: 'code',
        path: '/main/job-template'
      }
    ]
  },
  {
    label: 'JobManage',
    icon: 'job',
    path: '/main/job-manage',
    details: [
      {
        type: 'job',
        param: 'id',
        path: '/main/job'
      }
    ]
  },
  {
    label: 'ExpertMode',
    icon: 'expert',
    path: '/main/expert-mode'
  },
  {
    label: 'Tools',
    icon: 'tools',
    children: [
      {
        label: 'VNC',
        icon: 'vnc',
        path: '/main/vnc-manage'
      },
      {
        label: 'FileManage',
        icon: 'storage',
        path: '/main/file-manage'
      }
    ]
  }
]
