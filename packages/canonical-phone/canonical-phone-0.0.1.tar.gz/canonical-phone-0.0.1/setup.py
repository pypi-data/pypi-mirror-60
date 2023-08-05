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
