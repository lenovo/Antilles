# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

Name:           antilles-icinga-mond
Version:        1.0.0
Release:        1%{?dist}
Summary:        Icinga monitor daemon for Antilles

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
Recommends:     python-influxdb >= 5.0.0
Recommends:     python-APScheduler >= 3.5.1
Recommends:     python-requests >= 2.19.1
Recommends:     python-simplejson >= 3.16.0
%endif

Requires:       antilles-tools
Requires:       antilles-prepare >= %{antilles_ver}
Requires:       antilles-prepare < %{antilles_next_ver}

Obsoletes:      %{name} < %{version}-%{release}

%if 0%{?sles_version} || 0%{?suse_version}
Requires(pre):      systemd
%endif
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
The icinga monitor daemon get monitoring data from icinga to form
a common format. It also keeps metric history using influxdb.

%prep
%autosetup -n %{name}-%{version}
# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%antilles_py2_build

%install
%antilles_py2_install

%{__install} -Dp -m 0644 etc/%{name}.ini %{buildroot}%{_antillesconfdir}/icinga-mond.ini
%{__install} -Dp -m 0644 etc/%{name}.service %{buildroot}%{_unitdir}/%{name}.service

%pre
%if 0%{?sles_version} || 0%{?suse_version}
%service_add_pre %{name}.service
%endif

%python_requires "influxdb>=5.0.0"
%python_requires "APScheduler>=3.5.1"
%python_requires "requests>=2.19.1"
%python_requires "simplejson>=3.16.0"

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
%config(noreplace) %{_antillesconfdir}/icinga-mond.ini

# bin
%{_bindir}/antilles-icinga-mond

# program
%{_antillessitedir}/antilles_icinga_mond-*-py?.?.egg
%{python2_sitelib}/%{name}-%{version}.pth

%changelog
* Mon Jul 23 2018 Huijun Ni <nihj1@lenovo.com> - 1.0.0-1
- Initial package.

