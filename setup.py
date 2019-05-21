from setuptools import setup, find_packages

setup(
    name='app-run-and-log',
    version='0.1',
    packages=find_packages(include=["modules"]),
    install_requires=[
        'loguru==0.2.5',
        'pyaxmlparser==0.3.13'],
    entry_points={
        'console_scripts': [
            'app_run_and_log=main:main',
        ]
    },
    setup_requires=['setuptools'],
)
