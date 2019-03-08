# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual/non-commercial use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

%{!?run_npm_install:%global run_npm_install 1}

Name:           antilles-portal

Version:        1.0.0
Release:        1%{?dist}

Summary:        Antilles web portal

License:        BSD-3 and EPL-1.0
URL:            https://github.com/lenovo/Antilles
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  nodejs >= 6
BuildRequires:  antilles-rpm-macros
%{?suse_version:BuildRequires:npm >= 6}

%if 0%{?sles_version} || 0%{?suse_version}
Requires:       nginx >= 1.12
%else
Requires:       nginx >= 1:1.12
%endif

Requires:       novnc >= 0.6
Requires:       antilles-prepare >= %{antilles_ver}
Requires:       antilles-prepare < %{antilles_next_ver}
Requires:       nginx-https-config

Obsoletes:      %{name} < %{version}-%{release}

%description
Antilles web portal for whole project.

%prep
%autosetup -n %{name}-%{version}

%build
%if 0%{?run_npm_install}
%{_bindir}/npm install
%endif
%{_bindir}/npm run build

%install
%{__install} -Dp etc/antilles-portal.conf %{buildroot}%{_antillesconfdir}/portal.conf
%{__install} -Dp etc/antilles-portal-sample.conf %{buildroot}%{_antillesconfdir}/portal.conf.example

%{__install} -D etc/antilles.conf %{buildroot}%{_sysconfdir}/nginx/conf.d/sites-available/antilles.conf
%{__install} -d %{buildroot}%{_sysconfdir}/nginx/conf.d/sites-enabled
ln -s -T ../sites-available/antilles.conf %{buildroot}%{_sysconfdir}/nginx/conf.d/sites-enabled/antilles.conf
%{__install} -d %{buildroot}%{_datadir}/%{name}
%{__cp} -rT dist %{buildroot}%{_datadir}/%{name}


%files
%defattr(-,root,root,-)
%license COPYING.BSD
%license COPYING.EPL

%config(noreplace) %{_antillesconfdir}/portal.conf
%{_antillesconfdir}/portal.conf.example

%dir %{_sysconfdir}/nginx
%dir %{_sysconfdir}/nginx/conf.d
%dir %{_sysconfdir}/nginx/conf.d/sites-available
%dir %{_sysconfdir}/nginx/conf.d/sites-enabled
%config %{_sysconfdir}/nginx/conf.d/sites-available/antilles.conf
%{_sysconfdir}/nginx/conf.d/sites-enabled/antilles.conf

%{_datadir}/%{name}

%changelog
* Tue Sep 25 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial package.
