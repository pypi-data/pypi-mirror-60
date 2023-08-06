import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysteamcmd",
    version="0.2.1",
    author="f0rkz",
    author_email="f0rkz@f0rkznet.net",
    description="Python package to install and utilize steamcmd",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/f0rkz/pysteamcmd",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
