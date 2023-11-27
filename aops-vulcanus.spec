Name:		aops-vulcanus
Version:	v1.2.1
Release:	2
Summary:	A basic tool libraries of aops, including logging, configure and response, etc.
License:	MulanPSL2
URL:		https://gitee.com/openeuler/%{name}
Source0:	%{name}-%{version}.tar.gz
Patch0001:	0001-add-paging-parameter-schema.patch
Patch0002:	0002-updateuwsgi-conf-file-generation-function.patch


BuildRequires:  python3-setuptools
Requires:   python3-concurrent-log-handler python3-xmltodict python3-pyyaml python3-marshmallow >= 3.13.0
Requires:   python3-requests python3-xlrd python3-prettytable python3-pygments python3-sqlalchemy
Requires:   python3-elasticsearch >= 7 python3-elasticsearch < 8 python3-prometheus-api-client python3-urllib3 python3-werkzeug
Requires:   python3-flask python3-flask-restful python3-PyMySQL python3-kafka-python
Requires:   python-jwt python3-redis python3-Flask-APScheduler >= 1.11.0 python3-APScheduler
Provides:   aops-vulcanus
Conflicts:  aops-utils


%description
A basic tool libraries of aops, including logging, configure and response, etc.


%package -n aops-tools
Summary:  aops scripts
Provides: aops-tools = %{version}

%description -n aops-tools
tools for aops, it's about aops deploy


%prep
%autosetup -n %{name}-%{version} -p1


# build for aops-vulcanus
%py3_build


# install for aops-vulcanus
%py3_install


# install for aops-tools
mkdir -p %{buildroot}/opt/aops/
cp -r scripts %{buildroot}/opt/aops/


%files
%doc README.*
%attr(0644,root,root) %{_sysconfdir}/aops/system.ini
%attr(0640,root,root) %{_sysconfdir}/aops/.aops-private-config.ini
%{python3_sitelib}/aops_vulcanus*.egg-info
%{python3_sitelib}/vulcanus/*
%attr(0755,root,root) %{_bindir}/aops-vulcanus


%files -n aops-tools
%attr(0755, root, root) /opt/aops/scripts/*


%changelog
* Thu Jun 08 2023 wenxin<shusheng.wen@outlook.com> - v1.2.1-2
- fix issue: aops-zeus app failed to load when first start by uwsgi
- add paging parameter schema

* Tue May 23 2023 wenxin<shusheng.wen@outlook.com> - v1.2.1-1
- add cve rollback url for aops-zeus

* Tue May 9 2023 wenxin<shusheng.wen@outlook.com> - v1.2.0-4
- update length limit of username field

* Mon May 8 2023 gongzhengtang<gong_zhengtang@163.com> - v1.2.0-3
- add gevent config item for uwsgi; fix old token is invalid

* Thu Apr 27 2023 wenixn<shusheng.wen@outlook.com> - v1.2.0-2
- add custom validation rules;fix script docker install error

* Mon Apr 17 2023 wenixn<shusheng.wen@outlook.com> - v1.2.0-1
- update token authentication method; update the structure of response body
- update database connect method

* Tue Dec 27 2022 wenxin<shusheng.wen@outlook.com> - v1.1.1-2
- Modify uwsgi configuration file fields

* Fri Dec 02 2022 wenxin<shusheng.wen@outlook.com> - v1.1.1-1
- update get response

* Fri Nov 25 2022 wenxin<shusheng.wen@outlook.com> - v1.1.0-1
- Fix bug: fix file creation error

* Tue Nov 22 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.0.0-1
- Package init
