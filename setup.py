# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='JSGFTools',
    version='2.0.0',
    author='Pastèque Ho',
    author_email='timothyakho@gmail.com',
    description='Tools for parsing and generating strings from JSGF grammars',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/syntactic/JSGFTools',
    py_modules=['JSGFParser', 'JSGFGrammar', 'DeterministicGenerator', 'ProbabilisticGenerator'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyparsing>=3.0.0",
    ],
    entry_points={
        'console_scripts': [
            'jsgf-deterministic=DeterministicGenerator:main',
            'jsgf-probabilistic=ProbabilisticGenerator:main',
        ],
    },
)