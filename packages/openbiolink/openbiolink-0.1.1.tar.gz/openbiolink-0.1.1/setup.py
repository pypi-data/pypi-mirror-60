import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="openbiolink", 
	version="0.1.01",
	author="Anna Breit, Matthias Samwald, Simon Ott, Laura Graf, Asan Agibetov",
	author_email="matthiassamwald@gmail.com",
	description=" A framework for evaluating link prediction models on heterogeneous biomedical graph data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OpenBioLink/OpenBioLink",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	install_requires=[
		'numpy',
		'pandas==0.23.4',
		'pykeen',
		'pytest==5.0.1',
		'scikit-learn==0.19.1; python_version == "3.6"',
		'scikit-learn; python_version == "3.7"',
		'tqdm==4.29.1',
		'sortedcontainers',
	],
    python_requires='>=3.6',
)