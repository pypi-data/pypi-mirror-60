import pathlib
import re
import sys

import setuptools

name = "apimoex"
python_minimal = "3.6"

if sys.version_info < tuple(int(i) for i in python_minimal.split(".")):
    raise RuntimeError(f"{name} requires Python {python_minimal}+")

with open(pathlib.Path(__file__).parent / "apimoex" / "__init__.py") as file:
    try:
        version = re.search(r"^__version__ = \"(.+)\"$", file.read(), re.M)[1]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

with open("README.rst") as file:
    long_description = file.read()

setuptools.setup(
    name=name,
    version=version,
    description="MOEX ISS API",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://wlm1ke.github.io/apimoex/",
    author="Mikhail Korotkov aka WLMike",
    author_email="wlmike@gmail.com",
    license="http://unlicense.org",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Natural Language :: Russian",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Utilities",
    ],
    keywords="moex iss api",
    project_urls={"Source": "https://github.com/WLM1ke/apimoex"},
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=["requests"],
    python_requires=f">={python_minimal}",
)
