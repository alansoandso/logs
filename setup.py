import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

install_requires = [
    'fabric==2.4.0',
    'PyYAML==3.13',
    'pytest==4.0.2'
]

setup(name='logs',
      version='1.0',
      description='Tail remote logs for Plutus apps',
      author='Alan So',
      author_email='alansoandso@gmail.com',
      packages=find_packages('src'),
      package_data={'log_tools': ['logs.yaml']},
      package_dir={'': 'src'},
      py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
      include_package_data=True,
      entry_points={'console_scripts': ['logs = log_tools.logs:command_line_runner', ]},
      install_requires=install_requires
      )
