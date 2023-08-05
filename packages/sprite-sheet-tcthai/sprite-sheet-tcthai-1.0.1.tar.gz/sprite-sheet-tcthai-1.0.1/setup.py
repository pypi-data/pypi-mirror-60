#/usr/bin/env python3
import setuptools

with open("Readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sprite-sheet-tcthai",
    version="1.0.1",
    author="tcthai",
    author_email="thai.tran@f4.intek.edu.vn",
    copyright="Copyright (C) 2019, Intek Institute",
    description="sprite sheet utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/intek-training-jsc/sprite-sheet-tcthai",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'setuptools',
        'wheel',
        'twine',
        'pipfile',
        'pillow',
        'numpy'
    ],
)