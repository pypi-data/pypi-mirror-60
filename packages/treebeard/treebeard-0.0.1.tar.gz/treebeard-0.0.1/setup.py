import setuptools
from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip
from sys import version_info

pipfile = Project(chdir=False).parsed_pipfile
packages = pipfile["packages"].copy()
requirements = convert_deps_to_pip(packages, r=False)

print(requirements)
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="treebeard",
    version="0.0.1",
    author="Treebeard Technologies",
    author_email="alex@treebeard.io",
    description="Tools for notebook hosting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={"console_scripts": ["treebeard = treebeard.treebeard:cli"]},
    install_requires=requirements,
    download_url="https://github.com/treebeardtech/treebeard/archive/0.0.1.tar.gz"
)
