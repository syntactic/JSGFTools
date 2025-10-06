# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='jsgf-tools',
    version='2.1.1',
    author='Pastèque Ho',
    author_email='timothyakho@gmail.com',
    description='Complete JSGF toolkit: parse, generate, and test speech grammars with Unicode support',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/syntactic/JSGFTools',
    project_urls={
        'Bug Tracker': 'https://github.com/syntactic/JSGFTools/issues',
        'Documentation': 'https://github.com/syntactic/JSGFTools#readme',
        'Source Code': 'https://github.com/syntactic/JSGFTools',
    },
    packages=find_packages(exclude=['tests*', 'docs*']),
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
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Text Processing :: Linguistic",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: Japanese",
        "Natural Language :: Korean",
        "Natural Language :: Arabic",
        "Natural Language :: Russian",
        "Natural Language :: Hebrew",
        "Natural Language :: Greek",
        "Natural Language :: Hindi",
    ],
    keywords='jsgf grammar speech recognition nlp parsing generation unicode testing',
    python_requires=">=3.7",
    install_requires=[
        "pyparsing>=3.0.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'jsgf-deterministic=DeterministicGenerator:main',
            'jsgf-probabilistic=ProbabilisticGenerator:main',
        ],
    },
)