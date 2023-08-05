#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requirements = [
    'click',
    'beautifulsoup4',
    'lxml',
    'mecab-python3',
    'neo4j',
    'neobolt',
    'reppy',
    'requests',
    'chardet',
]

setup(
    author="ganariya",
    author_email="ganariya2525@gmail.com",
    description="ACO Web Crawler implemented by python",
    entry_points={
        'console_scripts': [
            'ACOCrawler=ACOCrawler.cli:main'
        ]
    },
    license="MIT",
    install_requires=requirements,
    include_package_data=True,
    keywords="ACOCrawler",
    name="ACOCrawler",
    packages=find_packages(),
    url="https://github.com/ganariya/ACOCrawler",
    version='0.1.0'
)
