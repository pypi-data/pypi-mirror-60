import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="s2v-extractor",
    version="0.0.0",
    author="Shubham Dhanda",
    author_email="sdhandahr08@gmail.com",
    description="Python package extractoin value from string",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iammoni/s2v-extractor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
