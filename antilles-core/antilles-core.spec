# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual/non-commercial use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

%{!?remove_source:%global remove_source 1}

%global service_name antilles
%global install_path %_antillesdir/core

Name:           antilles-core
Version:        1.0.0
Release:        1%{?dist}
Summary:        Restful server for antilles project

License:        BSD-3 and EPL-1.0
URL:            https://github.com/lenovo/Antilles
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  fdupes
BuildRequires:  gettext
BuildRequires:  systemd
BuildRequires:  python2-devel
BuildRequires:  python2-setuptools >= 36.0
BuildRequires:  python2-Cython
BuildRequires:  antilles-rpm-macros

%if 0%{?sles_version} || 0%{?suse_version}
BuildRequires:  systemd-rpm-macros
%endif

Requires(pre):  python2-setuptools >= 36.0
Requires:       python2-setuptools >= 36.0
Requires:       font(:lang=zh-cn)
Requires:       font(:lang=en)
Requires:       libuser-python >= 0.60

%if 0%{?sles_version} || 0%{?suse_version}
Recommends:       python-futures >= 3.1
Recommends:       python-gunicorn >= 19.7.1
Recommends:       python-psycopg2 >= 2.6
Recommends:       python-psutil >= 5.4
Recommends:       python-influxdb >= 5.0
Recommends:       python-django-pastedeploy-settings >= 1.0
Recommends:       python-pamela >= 0.3
Recommends:       python-cryptography >= 2.0
Recommends:       python-six >= 1.10
Recommends:       python-celery >= 4.1
Recommends:       python-requests >= 2.18
Recommends:       python-pika >= 0.11
Recommends:       python-pandas >= 0.19
Recommends:       python-xlwt >= 1.2
Recommends:       python-jsonschema >= 2.6
Recommends:       supervisor >= 3.3.4
Recommends:       python-PasteDeploy >= 1.5
Recommends:       python-Paste >= 2.0
Recommends:       python-Django < 2.0
Recommends:       python-Django >= 1.11
Recommends:       python-djangorestframework >= 3.7.0
Recommends:       python-django_celery_results >= 1.0.1
Recommends:       python-PyJWT >= 1.5.2
Recommends:       python-PyYAML >= 3.10
Recommends:       python-WeasyPrint >= 0.36
Recommends:       python-WeasyPrint < 0.43
%endif

%if 0%{?sles_version} || 0%{?suse_version}
Requires(pre):      systemd
%endif
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

Requires:       antilles-tools
Requires:       antilles-prepare >= %{antilles_ver}
Requires:       antilles-prepare < %{antilles_next_ver}

Obsoletes:      %{name} < %{version}-%{release}

%description
Restful server for antilles project.

%prep
%autosetup -n %{name}-%{version}
# Remove bundled egg-info
rm -rf %{name}.egg-info
pushd openHPC_web_project
rm -rf antilles.egg-info
popd

%build
pushd openHPC_web_project
CFLAGS="%{optflags}" %{__python} %{py_setup} %{?py_setup_args} bdist_egg
sleep 1
popd
%{_bindir}/cython src/*.pyx --embed

%{_bindir}/python2.7 -m compileall libs
%{_bindir}/python2.7 -OO -m compileall libs
%{_bindir}/python2.7 -m compileall job_daemon_project/job_daemon
%{_bindir}/python2.7 -OO -m compileall job_daemon_project/job_daemon

%install
# main project
%{__install} -d %{buildroot}%{install_path}
pushd openHPC_web_project
	easy_install -m --prefix %{buildroot}%{_prefix} -d %{buildroot}%{install_path} -N -Z dist/*-py%{python_version}*.egg
	pushd %{buildroot}%{install_path}
		egg_name=`ls -d *.egg`
	popd
	echo %{install_path}/${egg_name} >> ../conf/antilles.pth
	%{__install} -Dp -m 0400 ../conf/antilles.pth %{buildroot}%{python2_sitelib}/antilles.pth
	msgfmt -v antilles_web/locale/en/LC_MESSAGES/django.po -o %{buildroot}%{install_path}/${egg_name}/antilles_web/locale/en/LC_MESSAGES/django.mo
	msgfmt -v antilles_web/locale/sc/LC_MESSAGES/django.po -o %{buildroot}%{install_path}/${egg_name}/antilles_web/locale/sc/LC_MESSAGES/django.mo
popd

# compile antilles executable
%{__install} -d %{buildroot}%{_sbindir}
%{_bindir}/gcc src/*.c `python-config --ldflags --cflags` -o %{buildroot}%{_sbindir}/antilles-gunicorn

# old project
%{__install} -d %{buildroot}%{install_path}
%{__cp} -rT libs %{buildroot}%{install_path}/libs

%{__install} -Dp -m 0500 job_daemon_project/listener %{buildroot}%{install_path}/job_daemon_project/listener
%{__cp} -rT job_daemon_project/job_daemon %{buildroot}%{install_path}/job_daemon_project/job_daemon

# configure file
%{__install} -Dp -m 0644 etc/antilles.ini %{buildroot}%{_antillesconfdir}/antilles.ini
%{__install} -Dp -m 0644 etc/nodes.csv %{buildroot}%{_antillesconfdir}/nodes.csv.example
%{__install} -Dp -m 0644 etc/job_cmd_conf.yaml %{buildroot}%{_antillesconfdir}/job_cmd_conf.yaml
%{__install} -Dp -m 0644 etc/supervisord.conf %{buildroot}%{_antillesconfdir}/supervisord.conf
%{__install} -Dp -m 0644 etc/paste.d/django.ini %{buildroot}%{_antillesconfdir}/paste.d/django.ini
%{__install} -Dp -m 0644 etc/supervisor.d/antilles.ini %{buildroot}%{_antillesconfdir}/supervisor.d/antilles.ini
%{__install} -Dp -m 0644 etc/supervisor.d/jobdaemon.ini %{buildroot}%{_antillesconfdir}/supervisor.d/jobdaemon.ini

# runtime dir
%{__install} -d %{buildroot}%{_localstatedir}/log/antilles

# pam
%if 0%{?rhel}
%{__install} -Dp -m 0644 conf/%{service_name}.pam.rhel %{buildroot}%{_sysconfdir}/pam.d/%{service_name}
%endif

%if 0%{?suse_version}
%{__install} -Dp -m 0644 conf/%{service_name}.pam.suse %{buildroot}%{_sysconfdir}/pam.d/%{service_name}
%endif

# service
%{__install} -Dp -m 0644 conf/%{service_name}.conf %{buildroot}%{_sysconfdir}/sysconfig/%{service_name}
%{__install} -Dp -m 0644 conf/%{service_name}.service %{buildroot}%{_unitdir}/%{service_name}.service
%{__install} -Dp -m 0644 conf/%{service_name}.tmpfiles %{buildroot}%{_tmpfilesdir}/%{service_name}.conf

# remove all source files
%if 0%{?remove_source}
find %{buildroot}%{install_path} -regex .*\.py ! -regex .*/migrations/.*\.py -delete
%endif

# fdupes
%fdupes %{buildroot}%{install_path}

%pre
%if 0%{?sles_version} || 0%{?suse_version}
%service_add_pre %{service_name}.service
%endif

%python_requires "futures>=3.1"
%python_requires "gunicorn>=19.7.1"
%python_requires "psycopg2>=2.6"
%python_requires "psutil>=5.4"
%python_requires "influxdb>=5.0"
%python_requires "django-pastedeploy-settings>=1.0"
%python_requires "pamela>=0.3"
%python_requires "cryptography>=2.0"
%python_requires "six>=1.10"
%python_requires "celery>=4.1"
%python_requires "requests>=2.18"
%python_requires "pika>=0.11"
%python_requires "pandas>=0.19"
%python_requires "xlwt>=1.2"
%python_requires "jsonschema>=2.6"
%python_requires "supervisor>=3.3.4"
%python_requires "PasteDeploy>=1.5"
%python_requires "Paste>=2.0"
%python_requires "Django~=1.11.8"
%python_requires "djangorestframework>=3.7.0"
%python_requires "django_celery_results>=1.0.1"
%python_requires "PyJWT>=1.5.2"
%python_requires "PyYAML>=3.10"
%python_requires "WeasyPrint~=0.42.3"

%post
%tmpfiles_create %{_tmpfilesdir}/%{service_name}.conf
%if 0%{?sles_version} || 0%{?suse_version}
%service_add_post %{service_name}.service
%else
%systemd_post %{service_name}.service
%endif

%preun
%if 0%{?sles_version} || 0%{?suse_version}
%service_del_preun %{service_name}.service
%else
%systemd_preun %{service_name}.service
%endif

%postun
%if 0%{?sles_version} || 0%{?suse_version}
%service_del_postun %{service_name}.service
%else
%systemd_postun_with_restart %{service_name}.service
%endif

%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license COPYING.BSD
%license COPYING.EPL

# code
%dir /opt/antilles
%{install_path}
%attr(0400,antilles,antilles) %{python2_sitelib}/antilles.pth

# config
%config(noreplace) %{_antillesconfdir}/antilles.ini
%{_antillesconfdir}/nodes.csv.example
%config(noreplace) %{_antillesconfdir}/job_cmd_conf.yaml
%config(noreplace) %{_antillesconfdir}/supervisord.conf
%config(noreplace) %{_antillesconfdir}/paste.d/
%config(noreplace) %{_antillesconfdir}/supervisor.d

# service
%dir %{_sysconfdir}/sysconfig
%config %{_sysconfdir}/sysconfig/%{service_name}
%{_unitdir}/%{service_name}.service
%{_tmpfilesdir}/%{service_name}.conf

# runtime dir
%{_localstatedir}/log/antilles

# pam
%dir %{_sysconfdir}/pam.d
%config(noreplace) %{_sysconfdir}/pam.d/%{service_name}

# bin
%attr(0700,antilles,antilles) %{_bindir}/antilles
%caps(cap_chown,cap_dac_override,cap_setgid,cap_setuid,cap_fowner=ep) %{_sbindir}/antilles-gunicorn

%changelog
* Tue Sep 25 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial package.
