from setuptools import setup, find_packages

setup(
    name='bgparsers',
    version='0.10',
    packages=find_packages(),
    author='BBGLab (Barcelona Biomedical Genomics Lab)',
    author_email='bbglab@irbbarcelona.org',
    description="Library to read and parse mutation and region files.",
    license="Apache License 2",
    keywords="",
    url="https://bitbucket.org/bgframework/bgconfig",
    install_requires=[
        "tqdm",
        "bgconfig",
        "click",
        "numpy",
        "intervaltree"
    ],
    entry_points={
        'console_scripts': [
            'bgvariants = bgparsers.commands.bgvariants:cli',
        ]
    },
    setup_requires=[
        'pytest-runner'
    ],
    test_suite='tests',
    test_requires=[
        "pytest"
    ]
)
