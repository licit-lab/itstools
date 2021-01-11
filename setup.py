#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "numpy>=1.18",
    "bokeh>=2.1.1",
    "pandas>=1.0.0",
    "matplotlib>=3.2.2",
    "scipy>=1.5.4",
    "holoviews>=1.13.5",
    "hvplot>=0.6.0",
    "jupyter>=1.0.0",
    "networkx>=2.4.0",
]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]

dev_requirements = [
    "sphinx==3.2.1",
    "recommonmark==0.6.0",
    "pytest==6.1.1",
    "bump2version==1.0.0",
    "twine==3.2.0",
    "black==19.10b0",
    "pylint==2.6.0",
    "sphinx-rtd-theme==0.5.0",
    "tox==3.20.0",
    "coverage==5.3",
    "flake8==3.8.4",
]

setup(
    author="Andres Ladino",
    author_email="aladinoster@gmail.com",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="A package containing tools for simulating features for Intelligent Transportaiton Systems",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="itstools",
    name="itstools",
    packages=find_packages(include=["itstools", "itstools.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    extra_require={"dev": dev_requirements},
    url="https://github.com/reseach-licit/itstools",
    version="0.5.0",
    zip_safe=False,
)
