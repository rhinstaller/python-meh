%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define libreportver 2.0.18-1

Summary:  A python library for handling exceptions
Name: python-meh
Url: http://git.fedorahosted.org/git/?p=python-meh.git
Version: 0.25.3
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
BuildRequires: dbus-python, libreport-gtk >= %{libreportver}, libreport-cli >= %{libreportver}
Requires: python, dbus-python
Requires: openssh-clients, rpm-python, yum
Requires: libreport-cli >= %{libreportver}

%description
The python-meh package is a python library for handling, saving, and reporting
exceptions.

%package gui
Summary: Graphical user interface for the python-meh library
Requires: python-meh = %{version}-%{release}
Requires: pygobject3, gtk3
Requires: libreport-gtk >= %{libreportver}

%description gui
The python-meh-gui package provides a GUI for the python-meh library.

%prep
%setup -q

%build
make

%check
make test

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
%exclude %{python_sitelib}/meh/ui/gui.py*

%files gui
%{python_sitelib}/meh/ui/gui.py*
%{_datadir}/python-meh

%changelog
* Thu May 20 2019 Martin Kolman <mkolman@redhat.com> - 0.25.3-1
- Update translations
  Resolves: rhbz#1688260
- Switch from Transifex to Zanata for pulling translations (mkolman)
  Related: rhbz#1688260

* Thu Sep 11 2014 Martin Kolman <mkolman@redhat.com> - 0.25.2-1
- Exclude compiled versions of gui.py from the non-gui package (dshea)
  Resolves: rhbz#1140623

* Thu Sep 04 2014 Martin Kolman <mkolman@redhat.com> - 0.25.1-1
- Split GUI out into a separate package (#1136795) (vpodzime)
  Resolves: rhbz#1136795

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 0.25-2
- Mass rebuild 2013-12-27

* Tue Jun 18 2013 Vratislav Podzimek <vpodzime@redhat.com> - 0.25-1
- Add and use the safe_string module and the SafeStr class (vpodzime)
- Give translators hint about the cryptic strings (vpodzime)

* Thu May 02 2013 Vratislav Podzimek <vpodzime@redhat.com> - 0.24-1
- Epoch of the package from RPM db can be None (#957789) (vpodzime)

* Wed Apr 17 2013 Vratislav Podzimek <vpodzime@redhat.com> - 0.23-1
- Use Sphinx syntax for docstrings (vpodzime)
- Allow a change of the I/O functions (vpodzime)
- Reword the 'Debug' button warning (#948256) (vpodzime)

* Thu Apr 04 2013 Vratislav Podzimek <vpodzime@redhat.com> - 0.22-1
- Some more stuff for ABRT/libreport (#929181) (vpodzime)
- Tell ABRT we are reporting a Python excetion (vpodzime)
- Use named tuples instead of our magic tuples (vpodzime)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.21-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Jan 21 2013 Vratislav Podzimek <vpodzime@redhat.com> - 0.21-1
- New purely textual text interface (vpodzime)
- Add dumb enableNetwork implementation to GraphicalIntf (vpodzime)
- Destroy main window after running it (vpodzime)
- Get rid of the accountManager and use new libreport API (vpodzime)
- Add a way to override previously registered callback (vpodzime)
- Allow callbacks marked as attachment only (vpodzime)
- Add support for callbacks providing additional data (vpodzime)

* Tue Dec 11 2012 Vratislav Podzimek <vpodzime@redhat.com> - 0.20-1
- Handle non-ascii dict keys and values correctly (#883641) (vpodzime)

* Wed Nov 14 2012 Vratislav Podzimek <vpodzime@redhat.com> - 0.19-1
- Add test for handling unicode strings and files (vpodzime)
- Read files as UTF-8 and ignore errors (#874250) (vpodzime)
- Add %check section to the spec file (vpodzime)
- Fix tests (vpodzime)

* Thu Oct 25 2012 Vratislav Podzimek <vpodzime@redhat.com> - 0.18-1
- Handle tracebacks with no stack (#866441) (vpodzime)
- Parse component name correctly (#866526) (vpodzime)
- Spelling corrections (#865993) (vpodzime)

* Tue Oct 09 2012 Vratislav Podzimek <vpodzime@redhat.com> - 0.17-1
- Handle unicode strings correctly (#854959) (vpodzime)

* Tue Sep 11 2012 Vratislav Podzimek <vpodzime@redhat.com> - 0.16-1
- Do not overwrite process information with files having the same basename (vpodzime)
- Encode dump as utf-8 before writing to file (#854959) (vpodzime)

* Mon Aug 20 2012 Vratislav Podzimek <vpodzime@redhat.com> - 0.15-1
- Add main_window property to the MainExceptionWindow (vpodzime)
- Don't try to dump objects without __dict__ (vpodzime)
- Change require from rpm to rpm-python (vpodzime)

* Fri Aug 03 2012 Vratislav Podzimek <vpodzime@redhat.com> - 0.14-1
- Use just a basename of the attached file as the item name (vpodzime)
- Set the type hint for the mainExceptionWindow to Dialog (vpodzime)
- Store and then write out the string representation of the traceback and object dump (vpodzime)

* Wed Jul 27 2012 Vratislav Podzimek <vpodzime@redhat.com> - 0.13-1
- Add files specified in the Config object as attachments to bugreports (vpodzime)
- Display hint how to quit the debugger (vpodzime)
- Do not kill the process when 'continue' is used in pdb (vpodzime)
- Port to Gtk3 and the new design (vpodzime)
- Remove the rc attribute and getrc methods (vpodzime)
- Fix 'all' and 'install' Makefile targets (vpodzime)
- Migrate l10n to Transifex (vpodzime)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Dec 20 2011 Vratislav Podzimek <vpodzime@redhat.com> 0.12
- Use new libreport API to get more information to bugzilla (vpodzime).
- Adapt to the new API of libreport (vpodzime).
- Move "import rpm" to where it's needed to avoid nameserver problems (clumens).
  Resolves: rhbz#749330
- Change dependency to libreport-* (mtoman).
  Resolves: rhbz#730924
- Add abrt-like information to bug reports (vpodzime).
  Resolves: rhbz#728871
- Propagate the screen attr when using text mode (jmoskovc).

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

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
