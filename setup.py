from setuptools import setup, find_packages

setup(
    name='app-run-and-log',
    version='0.1',
    py_modules=['main'],
    packages=find_packages(include=["modules", "modules.*"]),
    install_requires=[
        'loguru==0.7.3',
        'pyaxmlparser==0.3.31'],
    entry_points={
        'console_scripts': [
            'app_run_and_log=main:main',
            'app-run-and-log=main:main',
        ]
    },
    setup_requires=['setuptools'],
)
