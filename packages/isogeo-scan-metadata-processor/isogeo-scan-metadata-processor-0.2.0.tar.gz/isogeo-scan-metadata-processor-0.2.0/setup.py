# -*- coding: UTF-8 -*-
#! python3  # noqa: E265

from setuptools import find_packages, setup

# package (to get version)
from scan_metadata_processor import __about__

setup(
    name="isogeo-scan-metadata-processor",
    version=__about__.__version__,
    author=__about__.__author__,
    author_email=__about__.__email__,
    description=__about__.__summary__,
    py_modules=["scan_metadata_processor"],
    # packaging
    packages=find_packages(
        exclude=["contrib", "docs", "*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    include_package_data=True,
    install_requires=[
        "click==7",
        "isogeo-pysdk>=3.3,<3.4",
        "python-dotenv",
        "peewee==3.13.*",
        "semver==2.9.*",
        "Send2Trash==1.5.*",
    ],
    entry_points="""
        [console_scripts]
        scan-metadata-processor=scan_metadata_processor.cli:scan_metadata_processor
    """,
)
