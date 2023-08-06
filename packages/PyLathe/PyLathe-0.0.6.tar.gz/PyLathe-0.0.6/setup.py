# !/usr/env/python3
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyLathe",
    version="0.0.6",
    author="Emmett Boudreau",
    author_email="emmettgb@gmail.com",
    description="A Python Wrapper for Lathe",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emmettgb/PyLathe",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
