import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hellobye",
    version="0.0.1",
    author="Tymoteusz Moryto",
    author_email="tymek24m@gmail.com",
    description='It says "Hello" and "Bye".',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://hellobye.c1.biz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)