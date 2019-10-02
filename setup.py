# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
import watson.routing

name = 'watson-routing'
description = 'Process and route HTTP Request messages.'
version = watson.routing.__version__


def read(filename, as_list=False):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        contents = f.read()
        if as_list:
            return contents.splitlines()
        return contents


setup(
    name=name,
    version=version,
    url='http://github.com/watsonpy/' + name,
    description=description,
    long_description=read('README.rst'),

    author='Simon Coulton',
    author_email='simon@bespohk.com',

    license=read('LICENSE'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=read('requirements.txt', as_list=True),
    extras_require={
        'test': read('requirements-test.txt', as_list=True)
    },
)
