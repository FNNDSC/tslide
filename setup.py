import sys
import os
# Make sure we are running python3.5+
if 10 * sys.version_info[0]  + sys.version_info[1] < 35:
    sys.exit("Sorry, only Python 3.5+ is supported.")

from setuptools import setup


def readme():
    print("Current dir = %s" % os.getcwd())
    print(os.listdir())
    with open('README.rst') as f:
        return f.read()

setup(
      name             =   'tsmake',
      version          =   '0.9.9',
      description      =   'Text-input web-based slide show manager',
      long_description =   readme(),
      author           =   'Rudolph Pienaar',
      author_email     =   'rudolph.pienaar@gmail.com',
      url              =   'https://github.com/FNNDSC/tslide',
      packages         =   ['tsmake'],
      install_requires =   ['pudb', 'psutil', 'pfurl', 'pfmisc'],
      test_suite       =   'nose.collector',
      tests_require    =   ['nose'],
      scripts          =   ['tsmake'],
      license          =   'MIT',
      zip_safe         =   False
     )
