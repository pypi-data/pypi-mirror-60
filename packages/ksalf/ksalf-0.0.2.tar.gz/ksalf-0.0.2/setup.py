import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ksalf",
    version="0.0.2",
    author="Benjamin Haegenlaeuer",
    author_email="benni.haegenlaeuer@outlook.de",
    description="A lightweight webserver implementation [inspired by flask]",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Haegi/ksalf",
    packages=setuptools.find_packages(exclude=["test"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
