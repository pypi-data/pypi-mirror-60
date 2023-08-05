from setuptools import find_packages, setup

setup(
    author="TAOS DevopsNow",
    name="taosdevopsutils",
    description="Utility Functions for the Taos Devops team",
    # license=open("LICENSE").read(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    version="1.3.1",
    url="https://github.com/taosdevops/taos-devops-utils",
    install_requires=[
        "requests~=2.22",
        "slackclient~=2.2",
        "Click~=7.0",
    ],
    entry_points="""
        [console_scripts]
        devops=taosdevopsutils.cli.main:main
        """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)
