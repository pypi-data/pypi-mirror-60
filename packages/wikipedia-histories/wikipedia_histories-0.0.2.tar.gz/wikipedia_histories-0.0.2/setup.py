import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wikipedia_histories",
    version="0.0.2",
    author="Nathan Drezner",
    author_email="nathan@drezner.com",
    description="A simple package designed to collect the edit histories of Wikipedia pages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ndrezn/wikipedia-histories",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)