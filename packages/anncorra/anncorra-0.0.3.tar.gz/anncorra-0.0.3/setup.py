"""Setup for the anncorra package."""

import setuptools


with open('README.md') as f:
    README = f.read()

setuptools.setup(
    author="Kuldeep Barot",
    name="anncorra",
    license="Apache License 2.0",
    description="Anncorra is a python package for giving meaning to POS (Part of Speech) tags.",
    version="v0.0.3",
    long_description=README,
    long_description_content_type='text/markdown',    
    url='https://github.com/kuldip-barot/anncorra',
    python_requires=">=3.5",
    install_requires=[],
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
)
