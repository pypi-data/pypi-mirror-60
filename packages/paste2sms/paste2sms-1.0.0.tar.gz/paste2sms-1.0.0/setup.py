#!/usr/bin/env python3

# Copyright 2020 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Installer"""

from setuptools import setup, find_packages
import codecs
import os


def readme():
    directory = os.path.dirname(os.path.join(os.getcwd(), __file__))
    with codecs.open(
        os.path.join(directory, "README.rst"),
        encoding="utf8",
        mode="r",
        errors="replace",
    ) as file:
        return file.read()


setup(
    name="paste2sms",
    version="1.0.0",
    packages=find_packages(exclude=["test*"]),
    python_requires=">=3.7",
    setup_requires=["setuptools_scm"],
    install_requires=["notify2", "pyperclip", "pyxdg", "requests",],
    include_package_data=True,
    author="Louis Paternault",
    author_email="spalax+python@gresille.org",
    description="Sent clipboard content as a SMS.",
    url="http://git.framasoft.org/spalax/paste2sms",
    license="GPLv3 or any later version",
    test_suite="test.suite",
    entry_points={"console_scripts": ["paste2sms = paste2sms.__main__:main"]},
    keywords="clipboard sms",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Communications :: Telephony",
    ],
    data_files=[
        ("share/applications/", ["desktop/paste2sms.desktop"]),
        ("share/pixmaps/", ["desktop/paste2sms.svg"]),
    ],
    long_description=readme(),
    long_description_content_type="text/x-rst",
    zip_safe=True,
)
