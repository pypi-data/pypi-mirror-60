
from setuptools import setup, find_packages
from octopus.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='octopus-cli',
    version=VERSION,
    description='Octopus is a devOps toolset',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Zhao Wei',
    author_email='zhaowei@ascs.tech',
    url='https://bitbucket.ascs.tech/projects/TOOL/repos/octopus-cli',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'octopus': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        octopus = octopus.main:main
    """,
)
