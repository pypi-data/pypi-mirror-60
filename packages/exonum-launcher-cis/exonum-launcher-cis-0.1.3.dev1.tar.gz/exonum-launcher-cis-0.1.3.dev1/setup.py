#!/usr/bin/env python
"""Setup Script for the Exonum Launcher."""
import setuptools

INSTALL_REQUIRES = ["pyyaml", "exonum-client-cis==0.4.0.dev6"]

PYTHON_REQUIRES = ">=3.6"

with open("README.md", "r") as readme:
    LONG_DESCRIPTION = readme.read()

setuptools.setup(
    name="exonum-launcher-cis",
    version="0.1.3.dev1",
    author="The Exonum team",
    author_email="contact@exonum.com",
    description="Exonum CIS Dynamic Services Launcher",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=["exonum_launcher_cis", "exonum_launcher_cis.instances", "exonum_launcher_cis.runtimes"],
    install_requires=INSTALL_REQUIRES,
    python_requires=PYTHON_REQUIRES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
    ],
)
