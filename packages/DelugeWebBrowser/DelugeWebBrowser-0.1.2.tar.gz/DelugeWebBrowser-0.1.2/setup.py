#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup
__plugin_name__ = 'DelugeWebBrowser'

with open("README.md") as readme_file:
    readme = readme_file.read()

test_requirements = [
    "codecov",
    "flake8",
    "black",
    "pytest",
    "pytest-cov",
    "pytest-raises",
]

setup_requirements = [
    "pytest-runner",
]

dev_requirements = [
    "bumpversion>=0.5.3",
    "coverage>=5.0a4",
    "flake8>=3.7.7",
    "ipython>=7.5.0",
    "m2r>=0.2.1",
    "pytest>=4.3.0",
    "pytest-cov==2.6.1",
    "pytest-raises>=0.10",
    "pytest-runner>=4.4",
    "Sphinx>=2.0.0b1",
    "sphinx_rtd_theme>=0.1.2",
    "tox>=3.5.2",
    "twine>=1.13.0",
    "wheel>=0.33.1",
]

interactive_requirements = [
    "altair",
    "jupyterlab",
    "matplotlib",
]

requirements = []

extra_requirements = {
    "test": test_requirements,
    "setup": setup_requirements,
    "dev": dev_requirements,
    "interactive": interactive_requirements,
    "all": requirements + test_requirements + setup_requirements + dev_requirements+ interactive_requirements
}

setup(
    author="Hicham Tahiri",
    author_email="aerospeace+dev@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="to complete later",
    entry_points="""
    [deluge.plugin.core]
    %s = %s:CorePlugin
    [deluge.plugin.gtkui]
    %s = %s:GtkUIPlugin
    [deluge.plugin.web]
    %s = %s:WebUIPlugin
    """ % ((__plugin_name__, __plugin_name__.lower()) * 3),
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="DelugeWebBrowser",
    name="DelugeWebBrowser",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    python_requires=">=2.7",
    setup_requires=setup_requirements,
    test_suite="DelugeWebBrowser/tests",
    tests_require=test_requirements,
    extras_require=extra_requirements,
    url="https://github.com/aerospeace/DelugeWebBrowser",
    # Do not edit this string manually, always use bumpversion
    # Details in CONTRIBUTING.rst
    version="0.1.2",
    zip_safe=False,
)
