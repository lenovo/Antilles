/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

export default [
  {
    label: 'MonitorDashboard',
    icon: 'home',
    path: '/main/dashboard-monitor',
    home: true
  },
  {
    label: 'Monitor',
    icon: 'monitor',
    children: [
      {
        label: 'MonitorNodes',
        icon: 'listview',
        path: '/main/monitor-nodes'
      },
      {
        label: 'MonitorRacks',
        icon: 'physicalview',
        path: '/main/monitor-racks',
        details: [
          {
            type: 'rack',
            param: 'id',
            path: '/main/rack'
          }
        ]
      },
      {
        label: 'MonitorGroups',
        icon: 'groupview',
        path: '/main/monitor-groups'
      },
      {
        label: 'MonitorGpus',
        icon: 'GPU',
        path: '/main/monitor-gpus'
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
        label: 'AlarmManage',
        icon: 'alarm',
        path: '/main/alarm-manage'
      },
      {
        label: 'OperationManage',
        icon: 'operationlog',
        path: '/main/operation-manage'
      }
    ]
  },
  {
    label: 'Report',
    icon: 'report',
    children: [
      {
        label: 'JobReport',
        icon: 'jobreport',
        path: '/main/report-job'
      },
      {
        label: 'AlarmReport',
        icon: 'alarmreport',
        path: '/main/report-alarm'
      },
      {
        label: 'OperationReport',
        icon: 'operationreport',
        path: '/main/report-operation'
      }
    ]
  }
]
