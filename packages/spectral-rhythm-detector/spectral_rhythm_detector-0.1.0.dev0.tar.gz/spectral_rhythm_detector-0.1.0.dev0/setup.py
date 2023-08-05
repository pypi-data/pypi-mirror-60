#!/usr/bin/env python3

from setuptools import find_packages, setup

INSTALL_REQUIRES = ['numpy >= 1.14', 'matplotlib',
                    'pandas', 'scipy', 'scikit-learn',
                    'spectral_connectivity', 'hmmlearn==0.2.2']
TESTS_REQUIRE = ['pytest >= 2.7.1']

setup(
    name='spectral_rhythm_detector',
    version='0.1.0.dev0',
    license='MIT',
    description=('Identify spectral rhythm events'),
    author='',
    author_email='',
    url='https://github.com/Eden-Kramer-Lab/spectral_rhythm_detector',
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
)
