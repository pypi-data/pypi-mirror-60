#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup."""

# Template from https://github.com/navdeep-G/setup.py

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = "board-game-recommender"
DESCRIPTION = "Board games recommender engine"
KEYWORDS = (
    "board games",
    "tabletop games",
    "recommendations",
    "recommender",
    "recommender engine",
    "recommendation engine",
    "boardgamegeek",
    "bgg",
    "ratings",
    "turicreate",
    "collaborative filtering",
    "ludoj",
    "ludoj-recommender",
)
URL_HOMEPAGE = "https://recommend.games/"
URL_DOCUMENTATION = (
    "https://gitlab.com/recommend.games/board-game-recommender/blob/master/README.md"
)
URL_FUNDING = None
URL_THANKS = None
URL_SOURCE = "https://gitlab.com/recommend.games/board-game-recommender"
URL_TRACKER = "https://gitlab.com/recommend.games/board-game-recommender/issues"
EMAIL = "markus@recommend.games"
AUTHOR = "Markus Shepherd"
REQUIRES_PYTHON = ">=3.6.0,<3.8.0"
VERSION = None  # will be read from __version__.py

# What packages are required for this module to be executed?
REQUIRED = ("pytility", "turicreate")

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

HERE = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
        LONG_DESCRIPTION = "\n" + f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
ABOUT = {}
if not VERSION:
    PROJECT_SLUG = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(HERE, PROJECT_SLUG, "__version__.py")) as f:
        # pylint: disable=exec-used
        exec(f.read(), ABOUT)
else:
    ABOUT["__version__"] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(string):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(string))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(HERE, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(ABOUT["__version__"]))
        os.system("git push --tags")

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=ABOUT["__version__"],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL_HOMEPAGE,
    project_urls={
        "Documentation": URL_DOCUMENTATION,
        # "Funding": URL_FUNDING,
        # "Say Thanks!": URL_THANKS,
        "Source": URL_SOURCE,
        "Tracker": URL_TRACKER,
    },
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=("tests", "*.tests", "*.tests.*", "tests.*")),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=(),
    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    # $ setup.py publish support.
    cmdclass={"upload": UploadCommand},
)
