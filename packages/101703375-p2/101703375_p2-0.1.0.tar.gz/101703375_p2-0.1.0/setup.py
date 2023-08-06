import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="101703375_p2",
    version="0.1.0",
    author="Nishant Dhanda",
    author_email="ndhanda_be17@thapar.edu",
    description="Removal of outliers using pandas",
	url='https://github.com/NishantDhanda/101703375_p2/',
	long_description=long_description,
	long_description_content_type="text/markdown",
	packages=setuptools.find_packages(),
	scripts=['bin/outcli'],
	keywords = ['CLI', 'OUTLIER', 'Data'], 
	python_requires='>=3.6', 
)
