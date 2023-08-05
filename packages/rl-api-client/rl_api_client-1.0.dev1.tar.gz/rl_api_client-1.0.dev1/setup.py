import os
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

# see https://github.com/pypa/sampleproject/blob/master/setup.py
#   for instructions.

_version = os.getenv('BUILD_VERSION', '100.0.0')

setup(
    name='rl_api_client',
    version=_version,
    author='Erez Atiya',
    author_email='erez.atiya@redislabs.com',
    description='Convenience API Client to use with Redis Enterprise API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License'
    ],
    packages=find_packages(),
    install_requires=[
        'requests==2.22.0',
        'urllib3==1.25.3',
        'wheel'

    ],
    dependency_links=[]
)
