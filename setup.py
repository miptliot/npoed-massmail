from setuptools import setup, find_packages

setup(
    name='npoed-massmail',
    version='0.1',
    packages=find_packages(),
    description='Mass e-mail utils for PLP and SSO',
    url='https://github.com/npoed/npoed-massmail',
    author='NPOED',
    install_requires=['django>=1.7',
                      'emails',
                      'django-post-office']
)
