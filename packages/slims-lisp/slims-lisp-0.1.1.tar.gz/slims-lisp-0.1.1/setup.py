from setuptools import find_packages, setup

setup(
    name = 'slims-lisp',
    version = '0.1.1',
    description = 'A high-level CLI for SlIMS REST API',
    long_description = open('README.rst').read(),
    long_description_content_type = 'text/x-rst',
    license = 'Apache License 2.0',
    author = 'Laboratory of Integrative System Physiology (LISP) at EPFL',
    author_email = 'alexis.rapin@epfl.ch',
    url = 'https://github.com/auwerxlab/slims-lisp-python-api',
    download_url = 'https://github.com/auwerxlab/slims-lisp-python-api/archive/v0.1.1.tar.gz',
    packages = find_packages(),
    install_requires = [
        'click',
        'requests',
        'datetime',
    ],
    entry_points = {
        'console_scripts': [
            'slims-lisp = slims_lisp.__main__:cli'
        ]
    },
)
