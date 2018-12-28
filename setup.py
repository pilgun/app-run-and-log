from distutils.core import setup

from setuptools import find_packages

setup(
    name='app-run-and-log',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'PyYAML==3.13',
        'pyaxmlparser==0.3.13',
        'click==7.0'],
    entry_points={
        'console_scripts': [
            'app-run-and-log=main:main',
        ]
    },
    setup_requires=['setuptools'],
)
