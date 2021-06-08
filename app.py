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

import botocore
import boto3
import logging
import os
import yaml
from thoth.common import init_logging
from thoth.python import Source

init_logging()

_LOGGER = logging.getLogger("thoth.gather_pypi_package_info")
_LOGGER.setLevel(logging.INFO)
_OUTPUT_FILE = os.getenv("OUTPUT_FILE", "gathered_pypi_package_info.yaml")
_OUTPUT_KEY = os.getenv("OUTPUT_KEY", f"data/{_OUTPUT_FILE}")
_BUCKET_NAME = os.environ["BUCKET_NAME"]
_ACCESS_KEY_ID = os.environ["ACCESS_KEY_ID"]
_S3_ENDPOINT = os.environ["S3_ENDPOINT"]
_SECRET_ACCESS_KEY = os.environ["SECRET_ACCESS_KEY"]


def cli() -> None:
    """Aggregate release information of packages."""
    pypi = Source("https://pypi.org/simple")

    session = boto3.Session(
        aws_access_key_id=_ACCESS_KEY_ID,
        aws_secret_access_key=_SECRET_ACCESS_KEY,
    )
    s3 = session.resource(
        "s3",
        config=botocore.client.Config(signature_version="s3v4"),
        endpoint_url=_S3_ENDPOINT,
    )

    _LOGGER.info("Obtaining package listing")
    packages = sorted(pypi.get_packages())

    packages_info = []
    failed = []
    try:
        for idx, package_name in enumerate(packages):
            _LOGGER.info(
                "%8s/%d Obtaining package info for %r", idx, len(packages), package_name
            )
            try:
                packages_info.append(
                    pypi._warehouse_get_api_package_info(package_name=package_name)
                )
            except Exception:
                failed.append(package_name)
                _LOGGER.exception(
                    "Failed to obtain package information for %r", package_name
                )
    finally:
        _LOGGER.info("Writing results to %r", _OUTPUT_FILE)
        with open(_OUTPUT_FILE, "w") as output:
            yaml.safe_dump({"packages_info": packages_info, "failed": failed}, output)

        s3.meta.client.upload_file(
            Filename=_OUTPUT_FILE,
            Bucket=_BUCKET_NAME,
            Key=_OUTPUT_KEY,
        )


__name__ == "__main__" and cli()
