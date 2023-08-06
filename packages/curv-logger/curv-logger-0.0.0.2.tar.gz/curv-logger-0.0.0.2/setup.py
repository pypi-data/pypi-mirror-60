from setuptools import setup, find_packages
from pathlib import Path
from curv_logger import __version__

setup(
    name="curv-logger",
    long_description=Path(__file__).parent.joinpath("README.md").read_text(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="http://github.com/rep-ai/curv-logger",
    version=__version__,
    packages=find_packages(),
    install_requires=['dataclasses', 'dataclasses-json'],
)
