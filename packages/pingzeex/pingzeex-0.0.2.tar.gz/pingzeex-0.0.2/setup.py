from setuptools import setup

import os

print(os.getcwd())
with open("README.md", "r") as fh:
	long_description = fh.read()


setup(
	name='pingzeex',
	version='0.0.2',
	description='Pingzeex Python Library',
	py_modules=["main"],
	package_dir={'':'src'},
	classifiers=[
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		],
		long_description=long_description,
		long_description_content_type="text/markdown",
		url= "https://github.com/nishgaba-ai/pingzeex",
		author="Nishchal Gaba",
		author_email="nishgaba.ai@gmail.com",
)
