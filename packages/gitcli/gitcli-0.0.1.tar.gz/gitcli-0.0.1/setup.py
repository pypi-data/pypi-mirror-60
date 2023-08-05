from setuptools import setup, find_packages

DEPENDENCIES = [
    "click",
    "distro",
    "cookiecutter",
    "hiyapyco",
    "requests",
    "gitpython",
    "cryptography",
    "python-gitlab"
]


setup(
    version="0.0.1",
    name="gitcli",
    packages=find_packages(),
    # package_data={"": ["*.lsf", "*.json"]},
    include_package_data=True,
    scripts=["gcli/cli.py"],
    # use_scm_version=True,
    # setup_requires=['setuptools_scm'],
    description="Git Command Line Interface",
    author="joaquin",
    install_requires=DEPENDENCIES,
    tests_require=["pytest", "tox"],
    python_requires=">=3",
    entry_points='''
        [console_scripts]
        gcli=gcli.cli:cli
    ''',
)
