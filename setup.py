#!/usr/bin/python2

from distutils.core import setup

setup(name='python-meh', version='0.2',
      description='Python module for handling exceptions',
      author='Chris Lumens', author_email='clumens@redhat.com',
      url='http://git.fedoraproject.org/git/?p=python-meh.git',
      package_dir = {'meh': 'src'},
      data_files = [('/usr/share/python-meh', ['ui/detailed-dialog.glade', 'ui/exnSave.glade',
                                               'pixmaps/exception.png'])],
      packages=['meh', 'meh.ui'])
