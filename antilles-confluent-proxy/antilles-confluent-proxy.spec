# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

Name:           antilles-confluent-proxy
Version:        1.0.0
Release:        1%{?dist}
Summary:        Restful server to support multi confluent session

License:        BSD-3 and EPL-1.0
URL:            https://github.com/lenovo/Antilles
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python2-setuptools >= 36.0
BuildRequires:  fdupes
BuildRequires:  antilles-rpm-macros

Requires(pre):  python2-setuptools >= 36.0
Requires:       python2-setuptools >= 36.0

%if 0%{?sles_version} || 0%{?suse_version}
Recommends:     python-PasteDeploy
Recommends:     python-gunicorn >= 19.7.1
Recommends:     python-falcon >= 1.3
Recommends:     python-gevent >= 1.1.2
Recommends:     python-ujson
Recommends:     python-jsonschema >= 2.5.1
Recommends:     python-requests >= 2.18.4
Recommends:     python-six >= 1.10
%endif

Requires:       antilles-core
Requires:       antilles-tools
Requires:       antilles-prepare >= %{antilles_ver}
Requires:       antilles-prepare < %{antilles_next_ver}

Obsoletes:      %{name} < %{version}-%{release}

%description
Restful server to support multi confluent session

%prep
%autosetup -n %{name}-%{version}
# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%antilles_py2_build

%install
%antilles_py2_install

%{__install} -Dp -m 644 etc/%{name}.ini %{buildroot}%{_antillesconfdir}/confluent-proxy.ini
%{__install} -Dp -m 644 etc/%{name}.conf %{buildroot}%{_antillesconfdir}/supervisor.d/confluent-proxy.ini

%pre
%python_requires "PasteDeploy"
%python_requires "gunicorn>=19.7.1"
%python_requires "falcon>=1.3"
%python_requires "gevent>=1.1.2"
%python_requires "ujson"
%python_requires "jsonschema>=2.5.1"
%python_requires "requests>=2.18.4"
%python_requires "six>=1.10"

%files
%defattr(-,root,root,-)
%license COPYING.BSD
%license COPYING.EPL

%dir %{_antillesconfdir}/supervisor.d
%config(noreplace) %{_antillesconfdir}/confluent-proxy.ini
%config(noreplace) %{_antillesconfdir}/supervisor.d/confluent-proxy.ini

# program
%{_antillessitedir}/antilles_confluent_proxy-*-py?.?.egg
%{python2_sitelib}/%{name}-%{version}.pth

%changelog
* Fri Aug 3 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial package.
