from setuptools import setup

setup(
    name='python-fmrest',
    version='0.2.0',
    author='David Hamann',
    author_email='dh@davidhamann.de',
    packages=['fmrest'],
    include_package_data=True,
    install_requires=['requests']
)
