#!/usr/bin/env python3
# Gather PyPI package information
# Copyright(C) 2021 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Obtain Python package information from PyPI."""

import logging
import os
import yaml
from thoth.common import init_logging
from thoth.python import Source

init_logging()

_LOGGER = logging.getLogger("thoth.gather_pypi_package_info")
_LOGGER.setLevel(logging.INFO)
_OUTPUT_FILE = os.getenv("OUTPUT_FILE", "gathered_pypi_package_info.yaml")


def cli() -> None:
    """Aggregate release information of packages."""
    pypi = Source("https://pypi.org/simple")

    _LOGGER.info("Obtaining package listing")
    packages = sorted(pypi.get_packages())

    packages_info = []
    failed = []
    try:
        for idx, package_name in enumerate(sorted(pypi.get_packages())):
            _LOGGER.info("%8s/%d Obtaining package info for %r", idx, len(packages), package_name)
            try:
                packages_info.append(pypi._warehouse_get_api_package_info(package_name=package_name))
            except Exception:
                failed.append(package_name)
                _LOGGER.exception("Failed to obtain package information for %r", package_name)
    finally:
        _LOGGER.info("Writing results to %r", _OUTPUT_FILE)
        with open(_OUTPUT_FILE, "w") as output:
            yaml.safe_dump({"packages_info": packages_info, "failed": failed}, output)


__name__ == "__main__" and cli()
