# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual/non-commercial use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

Name:           antilles-icinga-plugin
Version:        1.0.0
Release:        1%{?dist}
Summary:        Antilles monitor tool client

License:        BSD-3 and EPL-1.0
URL:            https://github.com/lenovo/Antilles
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python2-setuptools >= 36.0
BuildRequires:  fdupes
BuildRequires:  antilles-rpm-macros

%if 0%{?sles_version} || 0%{?suse_version}
BuildRequires:          nagios-rpm-macros
%else
%define nagios_libdir %{_libdir}/nagios
%define nagios_plugindir %{nagios_libdir}/plugins
%endif

Requires:       python2-setuptools >= 36.0
Requires:       antilles-prepare >= %{antilles_ver}
Requires:       antilles-prepare < %{antilles_next_ver}

Obsoletes:      %{name} < %{version}-%{release}

%description
The Antilles monitor tool Get the monitoring data on each node,
save it in icinga.

%prep
%autosetup -n %{name}-%{version}
# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%antilles_py2_build

%install
%antilles_py2_install

%{__install} -d %{buildroot}%{nagios_plugindir}
%{__mv} %{buildroot}%{_bindir}/antilles-icinga-plugin %{buildroot}%{nagios_plugindir}/antilles-icinga-plugin

%files
%defattr(-,root,root,-)
%license COPYING.BSD
%license COPYING.EPL

%dir %{nagios_libdir}
%dir %{nagios_plugindir}

# bin
%{nagios_plugindir}/antilles-icinga-plugin

# program
%{_antillessitedir}/antilles_icinga_plugin-*-py?.?.egg
%{python2_sitelib}/%{name}-%{version}.pth

%changelog
* Mon Jul 30 2018 Yuan Li <liyuan22@lenovo.com> - 1.0.0-1
- Initial package.
