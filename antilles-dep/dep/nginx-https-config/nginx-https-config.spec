# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

Name:           nginx-https-config
Version:        1.0.1
Release:        4%{?dist}
Summary:        Nginx config to support https

License:        BSD-3 and EPL-1.0

Source0:        https.rhel.conf
Source1:        https.suse.conf
Source2:        nginx-gencert

BuildArch:      noarch

BuildRequires:  antilles-rpm-macros

%if 0%{?rhel}
Requires:       nginx >= 1:1.12
Requires(post):	nginx-filesystem >= 1:1.12
%else
Requires:       nginx >= 1.12
Requires(post):	nginx >= 1.12
%endif

Requires(pre):  python2-setuptools >= 36.0
Requires:       python2-setuptools >= 36.0
Requires(post):  python2-setuptools >= 36.0

%description
install nginx https config to support https

%prep

%build

%install
%{__install} -d %{buildroot}%{_sysconfdir}/nginx/ssl

%{__install} -d %{buildroot}%{_sysconfdir}/nginx/conf.d/

%if 0%{?rhel}
%{__install} -m 644 %{SOURCE0} %{buildroot}%{_sysconfdir}/nginx/conf.d/https.conf
%endif

%if 0%{?suse_version}
%{__install} -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/nginx/conf.d/https.conf
%endif

%{__install} -d %{buildroot}%{_sysconfdir}/nginx/conf.d/sites-enabled
%{__install} -d %{buildroot}%{_sysconfdir}/nginx/conf.d/sites-available

%{__install} -d %{buildroot}%{_bindir}/
%{__install} -m 744 %{SOURCE2} %{buildroot}%{_bindir}/

%pre
%python_requires "cryptography>=2.0"

%post
%python_requires "cryptography>=2.0"
%{_bindir}/nginx-gencert

%files
%defattr(-,root,root,-)

%dir %{_sysconfdir}/nginx/
%dir %{_sysconfdir}/nginx/conf.d/
%{_sysconfdir}/nginx/ssl
%{_sysconfdir}/nginx/conf.d/sites-enabled
%{_sysconfdir}/nginx/conf.d/sites-available
%config(noreplace) %{_sysconfdir}/nginx/conf.d/https.conf
%{_bindir}/nginx-gencert

%changelog
* Fri Feb 1 2019 Yunfei Shi <shiyf2@lenovo.com> - 1.0.1-4
- Modify license.

* Thu Apr 17 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.1-3
- Support TLSv1.1 for older browsers.
- Modify license.

* Thu Apr 17 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.1-2
- Fix file permission.

* Fri Dec 22 2017 Yunfei Shi <shiyf2@lenovo.com> - 1.0.1-1
- Append ghost dir config.

* Thu Sep 15 2017 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial RPM release.
