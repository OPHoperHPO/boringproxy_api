"""Setup script"""
# -*- coding: utf-8 -*-

from setuptools import find_packages
from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='boringproxy_api',
    version='0.1.0',
    description='Python boringproxy api library',
    license='MIT',
    author='Nikita Selin (Anodev)',
    keywords=['boringproxy', 'api', 'client'],
    author_email='farvard34@gmail.com',
    url='https://github.com/OPHoperHPO/boringproxy_api',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=('docs', 'examples')),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
