import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "EventRecorder",
    version = "1.0.0",
    author = "Naman Thacker",
    author_email = "namanthacker98@gmail.com",
    description = ("CommandLine utility to keep track of important events and reminders"),
    license = "BSD",
    keywords = "commandline event recorder utility",
    url = "https://github.com/NDThacker/remind",
    packages = ['scripts',],
    long_description = read('README.md'),
	long_description_content_type = "text/markdown",
	scripts = ['remind'],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
		"Natural Language :: English",
		"Programming Language :: Python :: 3",
		"Topic :: Utilities"
    ],
	python_requires='>=3.6'
)
