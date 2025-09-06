import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 12):
    sys.exit("Python < 3.12 is not supported")

version = "1.2.2"

setup(
    name="steampy",
    packages=find_packages(
        include=["steampy", "steampy.*"],
        exclude=("tests", "tests.*", "test", "test.*", "examples", "examples.*"),
    ),
    version=version,
    description="A Steam lib for trade automation",
    author="Michał Bukowski",
    author_email="gigibukson@gmail.com",
    license="MIT",
    url="https://github.com/bukson/steampy",
    download_url="https://github.com/bukson/steampy/tarball/" + version,
    keywords=["steam", "trade"],
    classifiers=[],
    install_requires=["requests", "beautifulsoup4", "rsa", "protobuf>=5"],
    include_package_data=True,
    package_data={
        "steampy": [
            "generated/**/*.pyi",  # если генерируешь типовые заглушки
        ]
    },
)
