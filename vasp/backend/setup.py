# Copyright (c) The Diem Core Contributors
# SPDX-License-Identifier: Apache-2.0

from setuptools import setup, find_packages

setup(
    name="diem-sample-merchant-vasp",
    version="0.1.0",
    description="Sample merchant VASP implementation",
    python_requires=">=3.5",
    packages=find_packages(),
    tests_require=["pytest", "pytest-runner"],
    package_dir={"": "."},
)
