from setuptools import setup

setup(
   name='oxdc-scidb',
   version='0.1b1',
   description='A simple scientific database.',
   author='oxdc',
   author_email='projaias@outlook.com',
   url='https://github.com/oxdc/sci.db',
   packages=['scidb'],
   install_requires=['PyYAML', 'minio', 'urllib3']
)
