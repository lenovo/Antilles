# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf.urls import url

from .views import agent, alarm, policy, target

urlpatterns = [
    url(r'^alarm/?$', alarm.AlarmView.as_view()),
    url(r'^status/?$', alarm.AlarmView.as_view()),
    url(r'^(?P<pk>[0-9]+)/comment/?$', alarm.CommentView.as_view()),
    url(r'^scripts/?$', alarm.ScriptView.as_view()),
    url(r'^sound/?$', alarm.SoundView.as_view()),

    url(r'^policy/?$', policy.PolicyView.as_view()),
    url(r'^policy/(?P<pk>[0-9]+)/?$', policy.PolicyDetailView.as_view()),

    url(r'^test/?$', agent.TestView.as_view()),
    url(r'^email/?$', agent.EmailView.as_view()),
    url(r'^sms/?$', agent.SMSView.as_view()),
    url(r'^wechat/?$', agent.WechatView.as_view()),
    url(r'^wechat/qrcode/?$', agent.WechatQrcodeView.as_view()),

    url(r'^targets/?$', target.TargetView.as_view()),
    url(r'^targets/(?P<pk>[0-9]+)/?$', target.TargetDetailView.as_view()),
]
