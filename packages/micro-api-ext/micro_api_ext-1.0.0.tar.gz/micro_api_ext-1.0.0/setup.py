"""micro_api_ext """

import os.path

from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

setup(
    name="micro_api_ext",
    version="1.0.0",
    description="micro_api_ext",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/alhazmy13/api_ext",
    author="Alhazmy13",
    author_email="me@alhazmy13.net",
    license="MIT",
    classifiers=[],
    packages=["micro_api_ext"],
    include_package_data=True,
    install_requires=[
        "micro_restplus_ext",
        "flask", 'sqlalchemy', 'six'
    ]
)
