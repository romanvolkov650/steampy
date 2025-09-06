import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 12):
    sys.exit("Python < 3.12 is not supported")

version = "1.2.4"

setup(
    name="steampy",
    version=version,
    description="A Steam lib for trade automation",
    author="Michał Bukowski",
    author_email="gigibukson@gmail.com",
    license="MIT",
    url="https://github.com/bukson/steampy",
    packages=find_packages(
        include=["steampy", "steampy.*"],
        exclude=("tests", "tests.*", "test", "test.*", "examples", "examples.*"),
    ),
    install_requires=["requests", "beautifulsoup4", "rsa", "protobuf>=5"],
    include_package_data=True,
    package_data={"steampy": ["generated/**/*.pyi"]},
    python_requires=">=3.12",
    keywords=["steam", "trade"],
    classifiers=[],
)
