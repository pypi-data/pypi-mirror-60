# -*- coding: utf-8 -*-
from setuptools import setup

with open('requirements.txt') as f:
    requirements = [_.strip() for _ in f.readlines() if _]

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='chinesecalendar',
    version='1.4.0',
    description='check if some day is holiday in China',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Lirian Su',
    author_email='liriansu@gmail.com',
    url='https://github.com/LKI/chinese-calendar',
    license='MIT License',
    packages=['chinese_calendar'],
    install_requires=requirements,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
