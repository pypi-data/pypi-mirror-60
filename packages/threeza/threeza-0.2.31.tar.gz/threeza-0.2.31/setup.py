import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="threeza",
    version="0.2.31",
    description="In support of www.3za.org ",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/microprediction/threeza",
    author="microprediction",
    author_email="info@3za.org",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["threeza","threeza.static","threeza.templates","threeza.collider"],
    test_suite='pytest',
    tests_require=['pytest'],
    include_package_data=True,
    install_requires=["threezaconventions","cachetools","pathlib","jsonpath_ng","requests","matplotlib","intechinvestments"],
    entry_points={
        "console_scripts": [
            "threeza=threeza.__main__:main",
        ]
     },
     )
