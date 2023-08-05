from setuptools import setup
f = open('readme.rst').read()
setup(name="HumanActivityRecognition",
version="0.1",
description="Package to recognize Human Activity Recognition",
long_description = f,
author="Salma",
author_email = "ssalma3157@outlook.com",
packages=['HumanActivityRecognition'],
install_requires=[],
classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
],
python_requires='>=3.6',
setup_requires=["wheel"],
)
