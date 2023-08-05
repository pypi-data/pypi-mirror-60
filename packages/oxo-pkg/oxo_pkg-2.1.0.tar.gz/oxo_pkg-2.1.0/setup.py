import setuptools

with open("README.md") as fh:
    long_description = fh.read()

with open("oxo_pkg/resources/version.md") as fh:
    version = fh.read()

setuptools.setup(
    name="oxo_pkg",
    version=version,
    author="Adam Harrison",
    author_email="author@example.com",
    description="naughts and crosses game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/add-harris/oxo_pkg",
    scripts=["oxo"],
    packages=setuptools.find_packages(exclude=["test"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
