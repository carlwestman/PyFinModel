# setup.py

from setuptools import setup, find_packages

setup(
    name="PyFinModeler",
    version="0.1.0",
    description="Professional Financial Modeling and Valuation Framework in Python",
    author="Carl Westman",
    author_email="carl@wsvc.se",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.5",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Financial Analysts",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
