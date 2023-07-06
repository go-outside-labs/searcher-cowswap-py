from setuptools import setup, find_packages

setup(
    name="cowsol",
    version='0.1',
    packages=find_packages(include=['src', \
                    'src.apis', \
                    'src.strategies', \
                    'src.util']),
    author="bt3gl",
    install_requires=['python-dotenv'],
    entry_points={
        'console_scripts': ['cowsol=src.main:run']
    },
)
