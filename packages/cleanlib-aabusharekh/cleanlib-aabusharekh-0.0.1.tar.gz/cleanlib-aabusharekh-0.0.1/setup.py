import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="cleanlib-aabusharekh",  # Replace with your own username
    version="0.0.1",
    author="aabusharekh",
    author_email="aabusharekh@gmail.com",
    description="A pipenv setuptools test package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
