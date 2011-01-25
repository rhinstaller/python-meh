%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary:  A python library for handling exceptions
Name: python-meh
Url: http://git.fedorahosted.org/git/?p=python-meh.git
Version: 0.11
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
Requires: python, dbus-python, pygtk2, pygtk2-libglade
Requires: openssh-clients, rpm, yum, newt-python, report-gtk report-newt

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
%find_lang %{name}

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc ChangeLog COPYING
%{python_sitelib}/*
%{_datadir}/python-meh

%changelog
* Tue Jan 25 2011 Chris Lumens <clumens@redhat.com> - 0.11-1
- Update the spec file URL to something valid (#670601). (clumens)
- Don't use _D for Debug, since that's already used by the expander (#640929). (clumens)
- Translation updates.

* Tue Jun 22 2010 Chris Lumens <clumens@redhat.com> 0.10-1
- Treat classes like simple types, too. (clumens)

* Thu Jun 10 2010 Chris Lumens <clumens@redhat.com> - 0.9-1
- Remove the requirement on python-bugzilla (#602794). (clumens)
- Rename ba.po -> bs.po (#583055). (clumens)
- Translation updates.

* Thu Mar 04 2010 Chris Lumens <clumens@redhat.com> - 0.8-1
- And add a requirement for report as well. (clumens)
- filer.py is now completely taken over by meh. (clumens)
- Everything from savers.py has moved into report. (clumens)
- Remove unused UI code now that report handles all this for me. (clumens)
- Switch ExceptionHandler to use report (#562656). (clumens)
- Don't allow an exception when writing out an attribute stop the whole dump. (clumens)
- Credit where credit is due. (clumens)

* Tue Nov 03 2009 Chris Lumens <clumens@redhat.com> - 0.7-1
- Add a test case framework.
- Move src -> meh for ease of test case writing.
- Another attempt at making the attrSkipList work (#532612, #532737).

* Thu Oct 08 2009 Chris Lumens <clumens@redhat.com> - 0.6-1
- Make idSkipList work again.
- Support dumping objects derived from Python's object.
- Use the right method to set text on a snack.Entry (#526884).

* Tue Sep 29 2009 Chris Lumens <clumens@redhat.com> - 0.5-1
- Always compare version numbers as strings (#526188).

* Fri Sep 25 2009 Chris Lumens <clumens@redhat.com> - 0.4-1
- Add a default description to bug reports.
- Handle the user pressing Escape by continuing to show the dialog.
- Lots more translation updates.

* Thu Sep 10 2009 Chris Lumens <clumens@redhat.com> - 0.3-1
- Pull in lots of new translations (#522410).

* Wed Aug 19 2009 Chris Lumens <clumens@redhat.com> - 0.2-1
- Add a title to the main exception dialog so it looks right in anaconda.
- Don't include an extra '/' in the displayed bug URL (#517515).
- Now that there's .po files, package them.
- Use the new exception icon (#517164).

* Tue Jul 28 2009 Chris Lumens <clumens@redhat.com> - 0.1-1
- Initial package.
