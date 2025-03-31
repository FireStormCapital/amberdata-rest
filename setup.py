from setuptools import find_packages, setup

setup(
    name='amberdata_rest',
    packages=find_packages(include=['amberdata_rest', 'amberdata_rest.*']),
    version='0.2.1',
    description='Amberdata.io REST API SDK',
    author='technology@firestorm.capital',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==8.2.2'],
    test_suite='tests',
)