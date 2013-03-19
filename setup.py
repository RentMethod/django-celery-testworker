# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

import codecs

setup(
    name='django-celery-testworker',
    version='0.1.0',
    author=u'Willem Bult',
    author_email='willem.bult@gmail.com',
    packages=find_packages(),
    url='http://github.com/RentMethod/django-celery-testworker',
    license='BSD license, see LICENSE',
    description='Test functions to use with Django for tests that depend on the execution of Celery tasks',
    long_description=codecs.open('README.md', 'r', 'utf-8').read(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'lettuce>=0.2.15',
        'splinter>=0.5.0',
        'django_celery>=3.0.11',
    ],
)
