from setuptools import setup, find_packages

setup(
    name='app-run-and-log',
    version='0.1',
    packages=["."],
    install_requires=[
        'PyYAML==3.13',
        'pyaxmlparser==0.3.13',
        'click==6.7'],
    entry_points={
        'console_scripts': [
            'app_run_and_log=main:main',
        ]
    },
    setup_requires=['setuptools'],
)
