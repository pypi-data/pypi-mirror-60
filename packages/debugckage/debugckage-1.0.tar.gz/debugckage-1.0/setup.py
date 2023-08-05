#!/usr/bin/env python
# coding: utf-8

"""
    Module to install the "debugckage" package
"""

# =================================================================================================
# GLOBAL PARAMETERS
# =================================================================================================

__author__ = "JL31"
__version__ = "1.0"
__maintainer__ = "JL31"
__date__ = "January 2020"


# ==================================================================================================
# IMPORTS
# ==================================================================================================

from setuptools import setup, find_packages
import debugckage


# ==================================================================================================
# USE
# ==================================================================================================

if __name__ == "__main__":

    setup(
          name="debugckage",
          version=debugckage.__version__,
          packages=find_packages(),
          author="JL31",
          author_email="jeplul31@gmail.com",
          description="Functions to help debugging",
          long_description=open("README.rst").read(),
          include_package_data=True,
          url="https://github.com/JL31/debugckage",
          classifiers=["Programming Language :: Python",],
          license="WTFPL",
    )
