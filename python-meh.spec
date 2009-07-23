%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary:  A python library for handling exceptions
Name: python-meh
Url: http://git.fedoraproject.org/git/?p=python-meh.git
Version: 0.1
Release: 1%{?dist}
# This is a Red Hat maintained package which is specific to
# our distribution.  Thus the source is only available from
# within this srpm.
# This tarball was created from upstream git:
#   git clone git://git.fedoraproject.org/git/python-meh.git
#   cd python-meh && make archive
Source0: %{name}-%{version}.tar.gz

License: GPLv2+
Group: System Environment/Libraries
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: python-devel, gettext, python-setuptools-devel, intltool
Requires: python, python-bugzilla, dbus-python, pygtk2, pygtk2-libglade
Requires: openssh-clients, rpm, yum, newt-python

%description
The python-meh package is a python library for handling, saving, and reporting
exceptions.

%prep
%setup -q

%build
make

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

%clean
rm -rf %{buildroot}

%files 
%defattr(-,root,root,-)
%doc ChangeLog COPYING
%{python_sitelib}/*
%{_datadir}/python-meh

%changelog
* Thu Jul 16 2009 Chris Lumens <clumens@redhat.com> 0.1-1
- Initial package.
