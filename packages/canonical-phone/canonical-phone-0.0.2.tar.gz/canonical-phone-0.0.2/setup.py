import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="canonical-phone",
    version="0.0.1",
    author="Nitin Suresh",
    author_email="nitin.kalal@pasarpolis.com",
    description="Library to get canonical phone number",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/nitinsureshp/canonical-phone.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="canonical-phone",
    version="0.0.2",
    author="Nitin Suresh",
    author_email="nitin.kalal@pasarpolis.com",
    description="Library to get canonical phone number",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/nitinsureshp/canonical-phone.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license="MIT",
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "realpython=canonical_phone.phone.canonical_number",
        ]
    },
)
