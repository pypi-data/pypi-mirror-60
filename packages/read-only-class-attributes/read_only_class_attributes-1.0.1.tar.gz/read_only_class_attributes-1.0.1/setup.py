from setuptools import setup, find_packages
import versioneer

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='read_only_class_attributes',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='This package provides a decorator to make read only attributes on a given Python class',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pavanchhatpar/python-read-only-class-attributes',
    author='Pavan Chhatpar',
    author_email='pavanchhatpar@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[]
)