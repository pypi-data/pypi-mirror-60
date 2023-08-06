#!/usr/bin/env python3
from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name = 'django-shts3',
    version = '5.0',
    description = 'Start Django dev server faster',
    long_description = readme,
    long_description_content_type='text/markdown',
    author = "Wolphin",
    author_email = 'q@wolph.in',
    url = 'https://gitlab.com/qwolphin/django-shts3',
    py_modules = ['django_shts3'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'django = django_shts3:main',
            'd = django_shts3:main',
        ]
    },
)
