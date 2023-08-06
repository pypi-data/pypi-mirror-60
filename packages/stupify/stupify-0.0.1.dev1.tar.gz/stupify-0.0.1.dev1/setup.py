# Copyright © Nekoka.tt 2020
#
# This file is part of stupify.
#
# stupify is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# stupify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with stupify. If not, see <https://www.gnu.org/licenses/>.
import os
import re
import types

from setuptools import find_packages, setup, Extension


name = "stupify"


def dump(path):
    with open(path) as fp:
        return fp.read()


def parse_requirements():
    with open("requirements.txt") as fp:
        dependencies = (d.strip() for d in fp.read().split("\n") if d.strip())
        return [d for d in dependencies if not d.startswith("#")]


def get_data():
    with open(os.path.join(name, "_about.py")) as fp:
        code = fp.read()

    token_pattern = re.compile(
        r"^__(?P<key>\w+)?__\s*=\s*(?P<quote>[(?:'{3})(?:\"{3})'\"])(?P<value>.*?)(?P=quote)", re.M
    )

    groups = {}

    for match in token_pattern.finditer(code):
        group = match.groupdict()
        groups[group["key"]] = group["value"]

    return types.SimpleNamespace(**groups)


extensions = []


data = get_data()


setup(
    author=data.author,
    author_email=data.email,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: 3 :: Only",
    ],
    description="Stupidly smart and speedy serialization",
    ext_modules=extensions,
    include_package_data=True,
    license=data.license,
    long_description=dump("README.rst"),
    long_description_content_type="text/x-rst",
    name=name,
    packages=find_packages(),
    python_requires=">=3.8",
    test_suite="test",
    version=data.version,
)
