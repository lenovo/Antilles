# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

Name:           antilles-vnc-mond
Version:        1.0.0
Release:        1%{?dist}
Summary:        Vnc monitor component

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
Recommends:     python-psutil >= 5.4.0
Recommends:     python-requests >= 2.18.4
Recommends:     python-docopt >= 0.6.2
%endif

Requires:       antilles-prepare >= %{antilles_ver}
Requires:       antilles-prepare < %{antilles_next_ver}

Obsoletes:      %{name} < %{version}-%{release}
Obsoletes:      antilles-vnc-slave

%if 0%{?sles_version} || 0%{?suse_version}
Requires(pre):      systemd
%endif
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
This antilles-vnc-mond daemon aggregates monitoring data from vnc.

%prep
%autosetup -n %{name}-%{version}
# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%antilles_py2_build

%install
%antilles_py2_install

%{__install} -Dp -m 0644 etc/%{name}.ini %{buildroot}%{_antillesconfdir}/vnc-mond.ini

%{__install} -Dp -m 0644 etc/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
%{__install} -Dp -m 0644 etc/%{name}@.timer %{buildroot}%{_unitdir}/%{name}@.timer
%{__install} -Dp -m 0644 etc/%{name}-xvnc.service %{buildroot}%{_unitdir}/%{name}-xvnc.service

%pre
%if 0%{?sles_version} || 0%{?suse_version}
%service_add_pre %{name}.service
%service_add_pre %{name}@xvnc.timer
%endif

%python_requires "psutil>=5.4.0"
%python_requires "requests>=2.18.4"
%python_requires "docopt>=0.6.2"

%post
%if 0%{?sles_version} || 0%{?suse_version}
%service_add_post %{name}.service
%service_add_post %{name}@xvnc.timer
%else
%systemd_post %{name}.service
%systemd_post %{name}@xvnc.timer
%endif

%preun
%if 0%{?sles_version} || 0%{?suse_version}
%service_del_preun %{name}.service
%service_del_preun %{name}@xvnc.timer
%else
%systemd_preun %{name}.service
%systemd_preun %{name}@xvnc.timer
%endif

%postun
%if 0%{?sles_version} || 0%{?suse_version}
%service_del_postun %{name}.service
%service_del_postun %{name}@xvnc.timer
%else
%systemd_postun_with_restart %{name}.service
%systemd_postun_with_restart %{name}@xvnc.timer
%endif

%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license COPYING.BSD
%license COPYING.EPL

# service
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}@.timer
%{_unitdir}/%{name}-xvnc.service

# configure
%config(noreplace) %{_antillesconfdir}/vnc-mond.ini

# program
%{_bindir}/%{name}
%{_antillessitedir}/antilles_vnc_mond-*-py?.?.egg
%{python2_sitelib}/%{name}-%{version}.pth

%changelog
* Fri Aug 3 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial package.
