from setuptools import setup, find_packages

name = 'focustools'
version = '0.2.3'

description = 'Python utilities supporting the FOCUS package and cryo-EM data processing in general.'
long_description = '''FOCUSTOOLS offers Python functions and scripts for performing common tasks in cryogenic electron microscopy (cryo-EM) data processing such as postprocessing 3D maps, filtering, masking, computing FSC curves, cropping/padding in real and Fourier space, CTF correction, among others. Some of the scripts and functions contained here were developed to support the FOCUS package. Others were written for the developer's own studies or mere convenience, and are made available here in the hope they can be useful to someone else.

The I/O of MRC files is based on the [MRCZ library](https://github.com/em-MRCZ/python-mrcz).

Where possible, tasks are accelerated by the [NumExpr](https://github.com/pydata/numexpr) engine.'''

keywords = 'cryoEM cryo-EM focus single-particle tomography subtomogram-averaging electron-microscopy'

url = 'https://github.com/C-CINA/focustools'

author = 'Ricardo Righetto'
author_email = 'ricardo.righetto@unibas.ch'

license = 'GPLv3'

setup(
    name = name,
    version=version,
    description=description,
    long_description=long_description,
    keywords=keywords,
    url=url,
    author=author,
    author_email=author_email,
    license=license,
    packages=find_packages(),
    scripts = ['bin/focus.postprocess','bin/focus.ctf','bin/focus.mrcz','bin/focus.resample','bin/focus.project'],
    include_package_data = True,
    install_requires=[
        'numpy>=1.11',
        'numexpr',
        'matplotlib',
        'mrcz>=0.5.3',
        'packaging',
        'blosc',
    ],
)