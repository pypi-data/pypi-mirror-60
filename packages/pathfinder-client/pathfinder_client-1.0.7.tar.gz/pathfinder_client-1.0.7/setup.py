import setuptools

import pathfinder_client


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pathfinder_client",
    version=pathfinder_client.__version__,
    author="",
    author_email="",
    description="Client for Pathfinder microservice",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[
        'aiohttp',
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 
