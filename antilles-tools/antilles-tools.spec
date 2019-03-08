# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual/non-commercial use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

%global debug_package %{nil}

Name:           antilles-tools
Version:        1.0.0
Release:        1%{?dist}
Summary:        Tools collection for antilles project

License:        BSD-3 and EPL-1.0
URL:            https://github.com/lenovo/Antilles
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python2-devel
BuildRequires:  python2-setuptools >= 36.0
BuildRequires:  python2-Cython >= 0.27
BuildRequires:  fdupes
BuildRequires:  antilles-rpm-macros

Requires(pre):  python2-setuptools >= 36.0
Requires:       python2-setuptools >= 36.0

%if 0%{?sles_version} || 0%{?suse_version}
Recommends:     python-cryptography >= 2.0
Recommends:     python-docopt >= 0.6.2
Recommends:     python-six >= 1.11.0
Recommends:     python-psycopg2 >= 2.7
%endif

Requires:       antilles-prepare >= %{antilles_ver}
Requires:       antilles-prepare < %{antilles_next_ver}

Obsoletes:      %{name} < %{version}-%{release}

%description
Tools collection for antilles project

%prep
%autosetup -n %{name}-%{version}
# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%antilles_py2_build

%install
%antilles_py2_install
%{__install} -Dp -m 0700 -d %{buildroot}%{_antillesstatedir}/tools

%pre
%python_requires "cryptography>=2.0"
%python_requires "docopt>=0.6.2"
%python_requires "six>=1.11.0"
%python_requires "psycopg2>=2.7"

%files
%defattr(-,root,root,-)
%license COPYING.BSD
%license COPYING.EPL

%attr(0700,antilles,antilles) %{_antillesstatedir}/tools
%attr(0500,root,root) %{_bindir}/antilles-passwd-tool

%attr(0700,antilles,antilles) %{_antillessitedir}/antilles_tools-*-py?.?-*.egg
%{python2_sitelib}/%{name}-%{version}.pth

%changelog
* Tue Nov 29 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial package.
