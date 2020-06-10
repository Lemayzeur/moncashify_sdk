import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
	name="moncashify",
	version="0.0.1",
	author="Lub Lorry Lamysère",
	author_email="lemayzeur@code9haiti.com",
	description="Python SDK to make API requests and handle API responses from the MonCash API",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://lemayzeur.github.io/moncashify_sdk",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)
