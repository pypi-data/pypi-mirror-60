from setuptools import find_packages, setup

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="straal",
    version="0.1.0",
    author="Piotr Szpetkowski",
    url="https://github.com/piotr-szpetkowski/straal-python",
    license="Apache License, Version 2.0",
    description="Python client for Straal Payments API",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["requests>=2.22.0"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
