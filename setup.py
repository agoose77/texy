import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="texy",
    version="0.0.2",
    author="Angus Hollands",
    author_email="goosey15@gmail.com",
    description="A simple python Latex generator.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agoose77/texy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
