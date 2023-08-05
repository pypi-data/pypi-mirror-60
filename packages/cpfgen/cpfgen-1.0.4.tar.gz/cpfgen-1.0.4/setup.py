import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="cpfgen",
	version="1.0.4",
	author="Rodrigo Richter",
	author_email="guigorichter@gmail.com",
	description="A simple CLI application that prints a valid CPF number.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/rodrigorichter/cpfgen",
	packages=setuptools.find_packages(),
	classifiers=[
        	"Programming Language :: Python :: 3",
        	"License :: OSI Approved :: MIT License",
        	"Operating System :: OS Independent",
    	],
    	python_requires='>=3.6',
)
