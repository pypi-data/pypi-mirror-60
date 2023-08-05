import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ds_pkg',
    version='0.0.3',
    scripts=['ds_pkg'],
    author="Hasan Badran",
    author_email="badranh88@gmail.com",
    description="A Data Science project structure pip package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/badran047/ds-pkg",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

