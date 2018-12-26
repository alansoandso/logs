from setuptools import setup

install_requires = [
    'fabric==2.4.0',
    'PyYAML==3.13'
]

setup(name='logs',
      version='1.0',
      description='Tail remote logs for Plutus apps',
      author='Alan So',
      author_email='alansoandso@gmail.com',
      packages=['log_tools'],
      package_data={'log_tools': ['logs.yaml']},
      scripts=['logs'],
      install_requires=install_requires
      )
