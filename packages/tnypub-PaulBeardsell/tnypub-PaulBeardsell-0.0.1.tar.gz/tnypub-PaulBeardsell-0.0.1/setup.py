import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tnypub-PaulBeardsell",
    version="0.0.1",
    author="PaulBeardsell",
    author_email="pbeardsell@gmail.com",
    description="A static stite generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://tny.pub",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
