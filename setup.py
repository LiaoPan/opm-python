# -*- coding: utf-8 -*-
__author__ = 'LiaoPan'

import os
import os.path as op
from setuptools import setup, find_packages
from distutils.extension import Extension

# from Cython.Distutils import build_ext
# from Cython.Build import cythonize

# get the version
version = None
with open(op.join('opm', '_version.py'), 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('\'')
            break
if version is None:
    raise RuntimeError('Could not determine version')

VERSION = version
DISTNAME = "opm"
DESCRIPTION = "Processing tool for OPM-MEG."
MAINTAINER = "liaopan"
MAINTAINER_EMAIL = "liaopanblog@gmail.com"
URL = "https://github.com/liaopan/opm-python"
LICENSE = "MIT-License"
DOWNLOAD_URL = "http://github.com/liaopan/opm-python"
REQUIREMENTS_PATH = "requirements.txt"
TEST_REQUIREMENTS_PATH = "requirements_testing_tools.txt"

ext_modules = [Extension("opm", [
                               ])]


def parse_requirements_file(fname: str) -> list:
    """
    Parameters
    ----------
    fname:str
        the path of requirements.txt

    Returns
    -------
    requirements: list
        list of requirements.
    """
    requirements = []
    if not os.path.exists(fname):
        return requirements

    with open(fname, "r") as fileid:
        for line in fileid:
            package_name = line.strip()
            if not package_name.startswith('#'):
                requirements.append(package_name)
    return requirements


install_requires = parse_requirements_file(REQUIREMENTS_PATH)
tests_requires = parse_requirements_file(REQUIREMENTS_PATH) + parse_requirements_file(TEST_REQUIREMENTS_PATH)

with open("README.md", "r") as fid:
    long_description = fid.read()

setup(
    name=DISTNAME,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,
    packages=find_packages(),
    python_requires=">=3.6",
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
    ],
    version=VERSION,
    keywords="Neuroscience NeuroImaging OPM-MEG Brain.",
    # project_urls={
    #     "Homepage": "",
    #     "Download": "",
    #     "Bug Tracker": "",
    #     "Forum": "",
    #     "Source Code": "",
    # },
    package_data={
        'opm-python': []
    },
    entry_points={
        "console_scripts": [
        ]
    },
    # Indicates which packages the current module depends on.
    # If no packages are available in the environment,
    # they are automatically downloaded and installed from pypi.
    install_requires=install_requires,
    # Dependencies that are needed only at test time are not useful in normally distributed code.
    # tests_require=[
    #     'pytest>=3.3.1',
    #     'pytest-cov>=2.5.1',
    # ],
    # cmdclass={'build_ext': build_ext},
    # ext_modules=cythonize(ext_modules),
)
