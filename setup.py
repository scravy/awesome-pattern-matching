import re

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

    start_result = re.search(r"<!-- START doctoc [^>]+-->", long_description)
    if start_result:
        pos = start_result.span(0)[0]
        before = long_description[:pos]
        remaining = long_description[pos:]
        end_result = re.search(r"<!-- END doctoc [^>]+-->", remaining)
        end_pos = end_result.span(0)[1]
        after = remaining[end_pos:]
        long_description = before + after

__pkginfo__ = {}
with open("apm/__pkginfo__.py") as fh:
    exec(fh.read(), __pkginfo__)

setuptools.setup(
    name="awesome-pattern-matching",
    version=__pkginfo__['__version__'],
    author="Julian Fleischer",
    author_email="tirednesscankill@warhog.net",
    description="Awesome Pattern Matching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scravy/awesome-pattern-matching",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
