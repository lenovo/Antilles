# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual/non-commercial use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

Name:           antilles-env
Version:        1.0.0
Release:        1%{?dist}
Summary:        Antilles base environment

License:        BSD-3 and EPL-1.0

Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python2-devel
BuildRequires:  python2-setuptools
BuildRequires:  python2-Cython
BuildRequires:  antilles-rpm-macros

Requires(pre):  python2-setuptools >= 36.0

%if 0%{?sles_version} || 0%{?suse_version}
Recommends:     python-paramiko >= 2.4.0
%endif

Requires:       antilles-prepare >= %{antilles_ver}
Requires:       antilles-prepare < %{antilles_next_ver}

Obsoletes:      %{name} < %{version}-%{release}

%description
Antilles base workspace environment

%prep
%autosetup -n %{name}-%{version}

%build
%{_bindir}/cython src/*.pyx --embed

%install
%{__install} -d %{buildroot}%{_sysconfdir}/profile.d
%{__install} -m 444 antilles.sh %{buildroot}%{_sysconfdir}/profile.d/antilles.csh
%{__install} -m 444 antilles.sh %{buildroot}%{_sysconfdir}/profile.d/antilles.sh

%{__install} -m 700 -d %{buildroot}%{_sysconfdir}/skel/.ssh
%{__install} -m 600 ssh_config %{buildroot}%{_sysconfdir}/skel/.ssh/config
ln -s -T id_ecdsa.pub %{buildroot}%{_sysconfdir}/skel/.ssh/authorized_keys

%{__install} -Dp -m 755 antilles-data-collector.py %{buildroot}%{_bindir}/antilles-data-collector
%{_bindir}/gcc src/*.c `python-config --ldflags --cflags` -o %{buildroot}%{_bindir}/antilles-key-generator

%pre
%python_requires "paramiko>=2.4.0"

%files
%defattr(-,root,root,-)
%license COPYING.BSD
%license COPYING.EPL
%doc README.md

%dir %{_sysconfdir}/profile.d
%dir %{_sysconfdir}/skel
%dir %{_sysconfdir}/skel/.ssh

%{_sysconfdir}/profile.d/*
%{_sysconfdir}/skel/.ssh/*

%caps(cap_chown,cap_dac_override=ep) %{_bindir}/antilles-key-generator
%{_bindir}/antilles-data-collector

%changelog
* Wed Jul 18 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial RPM release.
