# -*- coding: utf8 -*-
"""Used to build and install the reviews module."""

from setuptools import setup


with open("README.md", "r") as readme:
    LONG_DESCRIPTION = readme.read()


setup(
    name="reviews",
    version="0.0.1a1",
    description="Diff monitor.",
    long_description=LONG_DESCRIPTION,
    author="Joe Riopel",
    author_email="joe.riopel@gmail.com",
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Intended Audience :: Developers, Security Reviewers",
        "Topic :: Software Development :: Code Reviews",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.7"
    ],
    keywords="development security",
    py_modules=["reviews"],
    packages=["tests"]
)
