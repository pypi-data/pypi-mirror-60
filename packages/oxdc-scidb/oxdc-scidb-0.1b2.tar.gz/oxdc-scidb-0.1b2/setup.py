from setuptools import setup

setup(
   name='oxdc-scidb',
   version='0.1b2',
   description='A simple scientific database.',
   author='oxdc',
   author_email='projaias@outlook.com',
   url='https://github.com/oxdc/sci.db',
   packages=['scidb', 'scidb.core', 'scidb.client', 'scidb.utils'],
   install_requires=['PyYAML', 'minio', 'urllib3']
)
