# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual/non-commercial use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

Name:           slapd-ssl-config
Version:        1.0.0
Release:        4%{?dist}
Summary:        Easy tool to configure slapd

License:        BSD-3 and EPL-1.0

BuildArch:      noarch

Source0:        slapd.rhel.conf
Source1:        slapd.suse.conf
Source2:        slapd-gencert
Source3:        DB_CONFIG
Source4:        base.ldif

BuildRequires:  antilles-rpm-macros

%if 0%{?rhel}
Requires:       openldap-servers >= 2.4
Requires(post):	openldap-servers >= 2.4
%else
Requires:       openldap2 >= 2.4
Requires(post):	openldap2 >= 2.4
%endif

Requires(pre):  python2-setuptools >= 36.0
Requires:       python2-setuptools >= 36.0
Requires(post):  python2-setuptools >= 36.0

%if 0%{?sles_version} || 0%{?suse_version}
Recommends:       python-cryptography >= 2.0
%endif

Obsoletes:      %{name} < %{version}-%{release}

%description
Easy tool to configure slapd, include cert tool and mini configure file.

%prep

%build

%install
%if 0%{?suse_version}
%{__install} -Dp -m 600 %{SOURCE1} %{buildroot}%{_sysconfdir}/openldap/slapd.conf.antilles
%endif

%if 0%{?rhel}
%{__install} -Dp -m 600 %{SOURCE3} %{buildroot}%{_localstatedir}/lib/ldap/DB_CONFIG
%{__install} -Dp -m 600 %{SOURCE0} %{buildroot}%{_sysconfdir}/openldap/slapd.conf
%endif

%{__install} -d %{buildroot}%{_sysconfdir}/openldap/cacerts

%{__install} -Dp -m 500 %{SOURCE2} %{buildroot}%{_bindir}/slapd-gencert
%{__install} -Dp -m 600 %{SOURCE4} %{buildroot}%{_datadir}/openldap-servers/antilles.ldif

%pre
%python_requires "cryptography>=2.0"

%post
%python_requires "cryptography>=2.0"
%{_bindir}/slapd-gencert

%files
%defattr(-,root,root,-)

%dir %{_datadir}/openldap-servers
%{_datadir}/openldap-servers/antilles.ldif

%dir %{_sysconfdir}/openldap
%attr(-,ldap,ldap) %dir %{_sysconfdir}/openldap/cacerts

%attr(-,ldap,ldap) %{_bindir}/slapd-gencert

%if 0%{?suse_version}
%attr(-,ldap,ldap) %config(noreplace) %{_sysconfdir}/openldap/slapd.conf.antilles
%endif

%if 0%{?rhel}
%attr(-,ldap,ldap) %{_localstatedir}/lib/ldap/DB_CONFIG
%config(noreplace) %attr(-,ldap,ldap) %{_sysconfdir}/openldap/slapd.conf
%endif

%changelog
* Fri Feb 1 2019 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-4
- Modify license.

* Wed Dec 19 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-3
- Set min TLS version.
- Modify license.

* Thu Apr 17 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-2
- Fix file permission.

* Thu Dec 7 2017 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial RPM release.
