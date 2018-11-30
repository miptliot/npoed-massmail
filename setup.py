from setuptools import setup, find_packages

setup(
    name='tp-massmail',
    version='0.1',
    packages=find_packages(),
    description='Mass e-mail utils for PLP and SSO',
    url='https://github.com/miptliot/tp-massmail',
    author='TP',
    install_requires=['django>=2',
                      'emails',
                      'django-post-office']
)
