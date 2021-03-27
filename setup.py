# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'easy_mock', '__about__.py'), encoding='utf-8') as f:
    exec(f.read(), about)

with io.open("README.md", encoding='utf-8') as f:
    long_description = f.read()

install_requires = ["PyYAML", "jsonschema", "loguru", "flask"]

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3',
    packages=find_packages(exclude=['test.*', 'test']),
    package_data={},
    keywords='har converter HttpRunner yaml json',
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': [
            'easy_mock=easy_mock.cli:cli'
        ]
    }
)
