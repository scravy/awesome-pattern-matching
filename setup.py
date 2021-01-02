import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

__pkginfo__ = {}
with open("jinsi/__pkginfo__.py") as fh:
    exec(fh.read(), __pkginfo__)


class Info:
    version = __pkginfo__.get("version", None)


setuptools.setup(
    name="ornament",
    version=Info.version,
    author="Julian Fleischer",
    author_email="tirednesscankill@warhog.net",
    description="JSON/YAML homoiconic templating language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scravy/ornament",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
