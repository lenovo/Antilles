# Copyright © 2019-present Lenovo
# 
# This file is licensed under both the BSD-3 license for individual use and
# EPL-1.0 license for commercial use. Full text of both licenses can be found in
# COPYING.BSD and COPYING.EPL files.

%global flavor ohpc

%if "%flavor" == "ohpc"
%bcond_without ohpc
%else
%bcond_with ohpc
%endif

%if %{with ohpc}
Name:           gmond-ohpc-gpu-module
%else
Name:           gmond-gpu-module
%endif
Version:        1.0.0
Release:        4%{?dist}
Summary:        NVIDIA GPU metric gmond module using the Python bindings for NVML

License:        MIT
URL:            https://github.com/ganglia/gmond_python_modules/tree/master/gpu/nvidia
Source0:        nvidia.py
Source1:        nvidia.pyconf

BuildArch:      noarch

%if %{with ohpc}
Requires:       ganglia-gmond-python-ohpc >= 3.7.2
%else
Requires:       ganglia-gmond-python >= 3.7.2
%endif

Requires:       python2-nvidia-ml-py >= 7.352.0

Obsoletes:      %{name} < %{version}-%{release}

%if %{with ohpc}
Obsoletes:gmond-gpu-module-ohpc
%endif

%description
NVIDIA GPU metric gmond module using the Python bindings for NVML

%prep

%build

%install
%{__install} -d %{buildroot}%{_sysconfdir}/ganglia/conf.d
%{__install} -m 444 %{SOURCE1} %{buildroot}%{_sysconfdir}/ganglia/conf.d

%{__install} -d %{buildroot}%{_libdir}/ganglia/python_modules
%{__install} -m 444 %{SOURCE0} %{buildroot}%{_libdir}/ganglia/python_modules

%files
%defattr(-,root,root,-)

%dir %{_libdir}/ganglia
%dir %{_libdir}/ganglia/python_modules
%dir %{_sysconfdir}/ganglia
%dir %{_sysconfdir}/ganglia/conf.d
%config(noreplace) %{_sysconfdir}/ganglia/conf.d/nvidia.pyconf
%{_libdir}/ganglia/python_modules/nvidia.py*

%changelog
* Thu Dec 27 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-4
- Modify License.

* Tue Mar 06 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-3
- Fix spec file syntax.

* Tue Mar 06 2018 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-2
- Modify ohpc package name.

* Thu Nov 28 2017 Yunfei Shi <shiyf2@lenovo.com> - 1.0.0-1
- Initial RPM release.
