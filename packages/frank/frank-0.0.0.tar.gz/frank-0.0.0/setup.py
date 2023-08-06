#!/usr/bin/env python
# coding=utf-8
from setuptools import setup, find_packages

version = {}
exec(open("frank/__init__.py", "r").read(), version)
version = '0.0.0'

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="frank",
    version=version,
    packages=find_packages(),
    author="Richard Booth, Jeff Jennings, Marco Tazzari",
    author_email="jmj51@ast.cam.ac.uk",
    description="Frankenstein, the flux reconstructor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[line.rstrip() for line in open("requirements.txt", "r").readlines()],
    extras_require={
        'test' : ['pytest'],
        'docs-build' : ['sphinx', 'sphinxcontrib-fulltoc', 'sphinx_rtd_theme', 'nbsphinx'],
        },
    license="GPLv3",
    url="https://github.com/discsim/frank",
    classifiers=[
        # 'Development Status :: 1 - Production/Stable',
        # "Intended Audience :: Developers",
        # "Intended Audience :: Science/Research",
        # 'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3',
    ]
)
