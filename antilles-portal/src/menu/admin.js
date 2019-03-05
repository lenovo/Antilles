/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual use and
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
    label: 'Admin',
    icon: 'admin',
    children: [
      {
        label: 'UserGroupManage',
        icon: 'userGroup',
        path: '/main/user-group-manage',
        ldap: 'optional'
      },
      {
        label: 'UserManage',
        icon: 'user',
        path: '/main/user-manage',
        ldap: 'optional',
        details: [
          {
            type: 'user',
            param: 'id',
            path: '/main/user'
          }
        ]
      },
      {
        label: 'BillGroupManage',
        icon: 'billinggroup',
        path: '/main/bill-group-manage'
      }
    ]
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
            param: 'jobId',
            path: '/main/job-template/resume'
          },
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
        label: 'OperationLogManage',
        icon: 'report',
        path: '/main/operation-log-manage'
      },
      {
        label: 'WebLogManage',
        icon: 'rizhi',
        path: '/main/web-log-manage'
      }
    ]
  },
  {
    label: 'Setting',
    icon: 'tools1',
    children: [
      {
        label: 'Scheduler',
        icon: 'scheduler',
        featureCode: 'scheduler.slurm',
        path: '/main/scheduler-manage'
      },
      {
        label: 'AlarmPolicyManage',
        icon: 'alarmpolicy',
        path: '/main/alarm-policy-manage'
      },
      {
        label: 'NotifyGroupManage',
        icon: 'notifygroup',
        path: '/main/notify-group-manage'
      },
      {
        label: 'NotifyAdapterManage',
        icon: 'notifyadapter',
        path: '/main/notify-adapter-manage'
      },
      {
        label: 'AlarmScriptManage',
        icon: 'script',
        path: '/main/alarm-script-manage'
      }
    ]
  }
]
