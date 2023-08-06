from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='gspread2',
    version='0.0.2',
    packages=find_packages(),
    url='https://github.com/futuereprojects/gspread2',
    license='MIT',
    author='FutuereProjects',
    author_email='nclark@riseup.net',
    description='Wrapper for gspread',
    long_description=long_description,
    python_requires='>=3.6',
    install_requires=['gspread', 'oauth2client'],
)
