# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

Name:           novnc
Version:        1.0.0
Release:        1%{?dist}
Summary:        VNC client using HTML5 (Web Sockets, Canvas) with encryption support

License:        MPLv2.0
URL:            https://github.com/kanaka/noVNC
Source0:        https://github.com/kanaka/noVNC/archive/v%{version}.tar.gz

BuildArch:      noarch

%description
Websocket implementation of VNC client

%prep
%setup -q -n noVNC-%{version}

%build

%install
%{__install} -d %{buildroot}%{_datadir}/novnc/{core,app,vendor}
%{__install} -m 444 *.html %{buildroot}%{_datadir}/novnc/
#provide an index file to prevent default directory browsing
%{__install} -m 444 vnc.html %{buildroot}%{_datadir}/novnc/index.html
%{__install} -m 444 vnc_lite.html %{buildroot}%{_datadir}/novnc/vnc_auto.html

%{__cp} -rT core %{buildroot}%{_datadir}/novnc/core
%{__cp} -rT app %{buildroot}%{_datadir}/novnc/app
%{__cp} -rT vendor %{buildroot}%{_datadir}/novnc/vendor

%files
%defattr(-,root,root,-)
%doc README.md LICENSE.txt
%{_datadir}/novnc

%changelog
* Tue Mar 13 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Upgrade to 1.0.0.

* Fri Dec 22 2017 Yunfei Shi <shiyf2@lenovo.com> - 0.6.2-1
- Upgrade to 0.6.2.

* Thu Sep 15 2017 Yunfei Shi <shiyf2@lenovo.com> - 0.6.1-1
- Initial RPM release.

