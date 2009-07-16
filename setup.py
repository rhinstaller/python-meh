#!/usr/bin/python2

from distutils.core import setup

setup(name='python-meh', version='0.1',
      description='Python module for handling exceptions',
      author='Chris Lumens', author_email='clumens@redhat.com',
      url='http://fedoraproject.org/wiki/python-meh',
      package_dir = {'meh': 'src'},
      data_files = [('/usr/share/python-meh', ['ui/detailed-dialog.glade', 'ui/exnSave.glade'])],
      packages=['meh', 'meh.ui'])
