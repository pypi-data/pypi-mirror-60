import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="tictoc-borisgorelik",
    version="0.0.3",
    author="Boris Gorelik",
    author_email="boris@gorelik.net",
    description="A simple way to measure execution time",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bgbg/tictoc",
    packages=setuptools.find_packages('./'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
