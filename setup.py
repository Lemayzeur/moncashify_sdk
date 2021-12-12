import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
	name="moncashify",
	version="1.1.0",
	author="Lub Lorry Lamysère",
	author_email="lemayzeur@code9haiti.com",
	description="Python SDK to make API requests and handle API responses from the MonCash API",
	long_description=long_description,
	long_description_content_type='text/x-rst',
	url="https://lemayzeur.github.io/moncashify_sdk",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	install_requires=[],
	python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
)
