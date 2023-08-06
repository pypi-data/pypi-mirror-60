import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Krypton-GD", 
    version="1.0.1",
    author="Imran S M",
    author_email="imran.malik01@icloud.com",
    description="A small package to add up two gaussian distributions together",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/immu0001/Krypton",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',

)

