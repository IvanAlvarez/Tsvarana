#! /usr/bin/env python

# Libraries
import setuptools

# Read version from __init__.py file
version = None
with open('tsvarana/__init__.py', 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('\'')
            break
if version is None:
    raise ValueError('Invalid version in __init__.py')

# Readme
with open('README.md', 'r') as fh:
    long_description = fh.read()

# Set-up
setuptools.setup(
    name='tsvarana',
    version=version,
    author='Ivan Alvarez',
    author_email='ivanalvarezferreira@gmail.com',
    maintainer_email='ivanalvarezferreira@gmail.com',
    description='Timeseries variance analysis for fMRI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/IvanAlvarez/Tsvarana',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
    ],
    install_requires=[
        'numpy>=1.19.1',
        'scipy>=1.4.1',
        'bokeh>=2.0.1',
        'nibabel>=3.0.2',
    ],
    python_requires='>=3.6',
)

# Done
#
