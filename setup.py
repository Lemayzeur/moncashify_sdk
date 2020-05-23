import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
	name="moncashify",
	version="0.0.1",
	author="Lub Lorry Lamysère",
	author_email="lemayzeur@code9haiti.com",
	description="A small example package",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/lemayzeur/moncashify",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.7',
)