#!/usr/bin/python3

from distutils.core import setup

setup(name='python-meh',
      version='0.48',
      description='Python module for handling exceptions',
      license="GPL-2.0+",
      author='Chris Lumens',
      author_email='clumens@redhat.com',
      maintainer='Anaconda maintenance team',
      maintainer_email='anaconda-maint-list@redhat.com',
      url='https://github.com/rhinstaller/python-meh',
      data_files=[('/usr/share/python-meh', ['ui/exception-dialog.glade'])],
      packages=['meh', 'meh.ui'],
      install_requires=['dbus-python', 'PyGObject', 'report', 'rpm'])
