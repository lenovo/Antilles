# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

%global  antilles_user antilles

%global src_name antilles-recipe

Name:           antilles-base-packages
Version:        1.0.0
Release:        1%{?dist}
Group:          antilles/base
Summary:        Antilles base

License:        BSD-3 and EPL-1.0

BuildRequires:      systemd

%if 0%{?sles_version} || 0%{?suse_version}
BuildRequires:      systemd-rpm-macros
%else
BuildRequires:      epel-rpm-macros
%endif

BuildArch:      noarch

Source0:        %{src_name}-%{version}.tar.gz
Source1:        NOTICE

%description
Collection of base packages

%package -n  antilles-prepare
Group:          antilles/base
Summary:        The basic directory layout for Antilles components
%if 0%{?sles_version} || 0%{?suse_version}
Requires(pre):     shadow
%else
Requires(pre):     shadow-utils
%endif

%description -n antilles-prepare
The antilles-prepare package contains the basic directory layout
for antilles-components including the correct permissions for the
directories.

%package -n  antilles-rpm-macros
Group:          antilles/base
Summary:        Include Files and Macros Mandatory for Building Antilles Modules

%if 0%{?sles_version} || 0%{?suse_version}
Requires:       python-rpm-macros
%else
Requires:       epel-rpm-macros
%endif

Requires:       antilles-prepare = %{version}-%{release}

%description -n antilles-rpm-macros
This package contains macros and source file for building Antilles modules.

%prep
%autosetup -n %{src_name}-%{version}
%{__install} -Dp -m 0644 %{SOURCE1} .

%install
%{__install} -Dp -m 0644 antilles.preset %{buildroot}%{_presetdir}/90-antilles.preset

%if 0%{?rhel}
%{__install} -Dp -m 0644 macros.antilles %{buildroot}%{rpmmacrodir}/macros.antilles
%else
%{__install} -Dp -m 0644 macros.antilles %{buildroot}%{_sysconfdir}/rpm/macros.antilles
%endif

%{__install} -Dp -m 0644 NOTICE %{buildroot}%{_datadir}/antilles/NOTICE

%{__install} -Dp -d -m 0755 %{buildroot}%{_sysconfdir}/antilles
%{__install} -Dp -d -m 0700 %{buildroot}%{_localstatedir}/lib/antilles

%{__install} -Dp -d %{buildroot}/opt/antilles/components

%pre -n antilles-prepare
getent group %{antilles_user} > /dev/null || groupadd -r %{antilles_user}
getent passwd %{antilles_user} > /dev/null || \
    useradd -r -d %{_localstatedir}/lib/antilles -g %{antilles_user} \
    -s /sbin/nologin -c "Antilles HPC Cluster" %{antilles_user}
exit 0

%files -n antilles-prepare
%defattr(-,root,root,-)
%license COPYING.BSD
%license COPYING.EPL
%doc NOTICE

%attr(700,%{antilles_user},%{antilles_user}) %dir %{_localstatedir}/lib/antilles
%dir %{_sysconfdir}/antilles
%dir /opt/antilles
%dir /opt/antilles/components
%dir %{_datadir}/antilles
%{_datadir}/antilles/NOTICE


%{_presetdir}/90-antilles.preset

%files -n antilles-rpm-macros
%defattr(-,root,root,-)
%if 0%{?rhel}
%{rpmmacrodir}/macros.antilles
%else
%{_sysconfdir}/rpm/macros.antilles
%endif

%changelog
* Tue Sep 25 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial package.

