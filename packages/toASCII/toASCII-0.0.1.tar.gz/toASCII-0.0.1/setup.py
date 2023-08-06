import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="toASCII", # Replace with your own username
    version="0.0.1",
    author="Matthew McCann",
    author_email="matthewmccann41@gmail.com",
    description="A simple package for easily converting strings to ASCII",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MattCodes03/Simple-ASCII-Converter-with-Python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)