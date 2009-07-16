%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary:  A python library for handling exceptions
Name: python-meh
Url: http://fedoraproject.org/wiki/python-meh
Version: 0.1
Release: 1%{?dist}
# This is a Red Hat maintained package which is specific to
# our distribution.  Thus the source is only available from
# within this srpm.
Source0: %{name}-%{version}.tar.gz

License: GPLv2
Group: System Environment/Libraries
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: python-devel, gettext, python-setuptools-devel
Requires: python, python-bugzilla, dbus-python, pygtk2, pygtk2-libglade
Requires: openssh-clients, yum

%description
The python-meh package is a python library for handling, saving, and reporting
exceptions.

%prep
%setup -q
make

%build

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
%find_lang %{name}

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc ChangeLog
%{python_sitelib}/*
%{_datadir}/python-meh

%changelog
* Thu Jul 16 2009 Chris Lumens <clumens@redhat.com> 0.1-1
- Initial package.
