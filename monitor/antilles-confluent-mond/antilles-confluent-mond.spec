# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

Name:           antilles-confluent-mond
Version:        1.0.0
Release:        1%{?dist}
Summary:        Confluent monitor component

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
BuildRequires:      systemd-rpm-macros
%endif

Requires(pre):  python2-setuptools >= 36.0
Requires:       python2-setuptools >= 36.0

%if 0%{?sles_version} || 0%{?suse_version}
Recommends:     python-influxdb >= 5.0.0
Recommends:     python-six >= 1.11.0
Recommends:     python-docopt >= 0.6.2
%endif

Requires:       antilles-tools
Requires:       antilles-prepare >= %{antilles_ver}
Requires:       antilles-prepare < %{antilles_next_ver}
Requires:       confluent_client >= 1.7.2

Obsoletes:      %{name} < %{version}-%{release}

%if 0%{?sles_version} || 0%{?suse_version}
Requires(pre):      systemd
%endif

Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
This antilles-confluent-mond daemon aggregates monitoring data from confluent.
It also keeps metric history using influxdb.

%prep
%autosetup -n %{name}-%{version}
# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%antilles_py2_build

%install
%antilles_py2_install

%{__install} -Dp -m 0644 etc/confluent.pth %{buildroot}%{python2_sitelib}/confluent.pth
%{__install} -Dp -m 0644 etc/%{name}.ini %{buildroot}%{_antillesconfdir}/confluent-mond.ini

%{__install} -Dp -m 0644 etc/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
%{__install} -Dp -m 0644 etc/%{name}@.timer %{buildroot}%{_unitdir}/%{name}@.timer
%{__install} -Dp -m 0644 etc/%{name}@.service %{buildroot}%{_unitdir}/%{name}@.service
%{__install} -Dp -m 0644 etc/%{name}-health.service %{buildroot}%{_unitdir}/%{name}-health.service
%{__install} -Dp -m 0644 etc/%{name}-power.service %{buildroot}%{_unitdir}/%{name}-power.service
%{__install} -Dp -m 0644 etc/%{name}-temp.service %{buildroot}%{_unitdir}/%{name}-temp.service
%{__install} -Dp -m 0644 etc/%{name}-state.service %{buildroot}%{_unitdir}/%{name}-state.service

%pre
%if 0%{?sles_version} || 0%{?suse_version}
%service_add_pre %{name}.service
%service_add_pre %{name}@health.timer
%service_add_pre %{name}@power.timer
%service_add_pre %{name}@temp.timer
%service_add_pre %{name}@state.timer
%endif

%python_requires "influxdb>=5.0.0"
%python_requires "six>=1.11.0"
%python_requires "docopt>=0.6.2"

%post
%if 0%{?sles_version} || 0%{?suse_version}
%service_add_post %{name}.service
%service_add_post %{name}@health.timer
%service_add_post %{name}@power.timer
%service_add_post %{name}@temp.timer
%service_add_post %{name}@state.timer
%else
%systemd_post %{name}.service
%systemd_post %{name}@health.timer
%systemd_post %{name}@power.timer
%systemd_post %{name}@temp.timer
%systemd_post %{name}@state.timer
%endif

%preun
%if 0%{?sles_version} || 0%{?suse_version}
%service_del_preun %{name}@health.timer
%service_del_preun %{name}@power.timer
%service_del_preun %{name}@temp.timer
%service_del_preun %{name}@state.timer
%service_del_preun %{name}.service
%else
%systemd_preun %{name}@health.timer
%systemd_preun %{name}@power.timer
%systemd_preun %{name}@temp.timer
%systemd_preun %{name}@state.timer
%systemd_preun %{name}.service
%endif

%postun
%if 0%{?sles_version} || 0%{?suse_version}
%service_del_postun %{name}@health.timer
%service_del_postun %{name}@power.timer
%service_del_postun %{name}@temp.timer
%service_del_postun %{name}@state.timer
%service_del_postun %{name}.service
%else
%systemd_postun_with_restart %{name}@health.timer
%systemd_postun_with_restart %{name}@power.timer
%systemd_postun_with_restart %{name}@temp.timer
%systemd_postun_with_restart %{name}@state.timer
%systemd_postun_with_restart %{name}.service
%endif

%files
%defattr(-,root,root,-)
%license COPYING.BSD
%license COPYING.EPL

# service
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}@.timer
%{_unitdir}/%{name}@.service
%{_unitdir}/%{name}-health.service
%{_unitdir}/%{name}-power.service
%{_unitdir}/%{name}-temp.service
%{_unitdir}/%{name}-state.service

# configure
%dir %{_sysconfdir}/antilles
%config(noreplace) %{_antillesconfdir}/confluent-mond.ini

# program
%{_bindir}/%{name}
%{_antillessitedir}/antilles_confluent_mond-*-py?.?.egg
%{python2_sitelib}/%{name}-%{version}.pth
%{python2_sitelib}/confluent.pth

%changelog
* Tue Jul 17 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial package.
