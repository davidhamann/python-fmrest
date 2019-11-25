from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as ld:
    long_description = ld.read()

setup(
    name='python-fmrest',
    version='1.2.1',
    python_requires='>=3.6',
    author='David Hamann',
    author_email='dh@davidhamann.de',
    description='python-fmrest is a wrapper around the FileMaker Data API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/davidhamann/python-fmrest',
    packages=['fmrest'],
    include_package_data=True,
    install_requires=['requests>=2'],
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    )
)
