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

import nox


@nox.session(python=False)
def install_dependencies(session):
    """Install dependencies."""
    session.run("pip", "install", "-r", "dev_requirements.txt")
    session.run("pip", "install", "-r", "requirements.txt")


@nox.session(python=False)
def clean(session):
    """Clean compiled files."""
    session.run("python", "setup.py", "clean", "--all")


@nox.session()
def black(session):
    """Format code correctly."""
    session.install("black")
    session.run("black", "stupify", "test", "setup.py", "noxfile.py")


@nox.session(python=False)
def build(session):
    """Compile extensions."""
    session.run("python", "setup.py", "build_ext", "--inplace")


@nox.session(python=False)
def sdist(session):
    """Build an sdist Python package."""
    session.run("python", "setup.py", "build", "sdist")


@nox.session(python=False)
def bdist_wheel(session):
    """Build a bdist_wheel Python package."""
    session.run("python", "setup.py", "build", "bdist_wheel")


@nox.session(python=False)
def test(session):
    """Run unit tests."""


@nox.session(python=False)
def deploy(session):
    """Deploy to PyPI."""
