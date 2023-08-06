from setuptools import setup, find_packages
import versioneer

setup(
    name='read_only_class_attributes',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='This package provides a decorator to make read only attributes on a given Python class',
    url='https://github.com/pavanchhatpar/python-read-only-class-attributes',
    author='Pavan Chhatpar',
    author_email='pavanchhatpar@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[]
)