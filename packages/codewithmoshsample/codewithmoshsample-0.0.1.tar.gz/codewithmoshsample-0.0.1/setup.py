import setuptools
from pathlib import Path

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="codewithmoshsample",
    version="0.0.1",
    author="Example Author",
    author_email="author@example.com",
    description="A small example package",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    # packages=setuptools.find_packages(),
    packages=setuptools.find_packages(exclude=["tests","data"])
    # python_requires='>=3.6',
)