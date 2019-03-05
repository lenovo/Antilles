# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

Name:           antilles-mail-agent
Version:        1.0.0
Release:        1%{?dist}
Summary:        Mail alarm agent for antilles project

License:        BSD-3 and EPL-1.0
URL:            https://github.com/lenovo/Antilles
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python2-setuptools >= 36.0
BuildRequires:  fdupes
BuildRequires:  systemd
BuildRequires:  antilles-rpm-macros

%if 0%{?sles_version} || 0%{?suse_version}
BuildRequires:  systemd-rpm-macros
%endif

Requires(pre):  python2-setuptools >= 36.0
Requires:       python2-setuptools >= 36.0

%if 0%{?sles_version} || 0%{?suse_version}
Recommends:     python-PasteDeploy
Recommends:     python-PyYAML >= 3.10
Recommends:     python-gunicorn >= 19.7.1
Recommends:     python-gevent >= 1.1.2
Recommends:     python-falcon >= 1.3
Recommends:     python-ujson
Recommends:     python-jsonschema >= 2.5.1
%endif

Requires:       antilles-prepare >= %{antilles_ver}
Requires:       antilles-prepare < %{antilles_next_ver}

%if 0%{?sles_version} || 0%{?suse_version}
Requires(pre):      systemd
%endif
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

Obsoletes:      %{name} < %{version}-%{release}

%description
Email alarm agent for antilles project

%prep
%autosetup -n %{name}-%{version}
# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%antilles_py2_build

%install
%antilles_py2_install

%{__install} -Dp -m 0644 etc/%{name}.ini %{buildroot}%{_antillesconfdir}/mail-agent.ini

%{__install} -Dp -m 0644 etc/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
%{__install} -Dp -m 0644 etc/%{name}.service.conf %{buildroot}%{_sysconfdir}/sysconfig/%{name}

%pre
%if 0%{?sles_version} || 0%{?suse_version}
%service_add_pre %{name}.service
%endif

%python_requires "PasteDeploy"
%python_requires "PyYAML>=3.10"
%python_requires "gunicorn>=19.7.1"
%python_requires "gevent>=1.1.2"
%python_requires "falcon>=1.3"
%python_requires "ujson"
%python_requires "jsonschema>=2.5.1"

%post
%if 0%{?sles_version} || 0%{?suse_version}
%service_add_post %{name}.service
%else
%systemd_post %{name}.service
%endif

%preun
%if 0%{?sles_version} || 0%{?suse_version}
%service_del_preun %{name}.service
%else
%systemd_preun %{name}.service
%endif

%postun
%if 0%{?sles_version} || 0%{?suse_version}
%service_del_postun %{name}.service
%else
%systemd_postun_with_restart %{name}.service
%endif

%files
%defattr(-,root,root,-)
%license COPYING.BSD
%license COPYING.EPL

# service
%{_unitdir}/%{name}.service

# configure
%dir %{_sysconfdir}/sysconfig
%config %{_sysconfdir}/sysconfig/%{name}

%config(noreplace) %{_antillesconfdir}/mail-agent.ini

# program
%{_antillessitedir}/antilles_mail_agent-*-py?.?.egg
%{python2_sitelib}/%{name}-%{version}.pth

%changelog
* Tue Jul 17 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial package.
