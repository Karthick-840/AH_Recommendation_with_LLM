from setuptools import setup, find_packages

import re
VERSIONFILE="web-scrapping-airline-dataset/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Web Scrapping for Airlines Dataset",
    version=verstr,
    author="Karthick Jayaraman",
    author_email="karthick840@yahoo.in",
    description="An example project on Web Scrapping and publishing data to Kaggle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Karthick-840/Web-Scrapping-Airline-Dataset.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)