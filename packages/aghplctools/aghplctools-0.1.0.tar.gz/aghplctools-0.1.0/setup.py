from setuptools import setup, find_packages

NAME = 'aghplctools'
VERSION = '0.1.0'
AUTHOR = 'Lars Yunker / Hein Group'

PACKAGES = find_packages()
# KEYWORDS = ', '.join([
# ])

# with open('LICENSE') as f:
#     license = f.read()
#     license.replace('\n', ' ')

# with open('README.MD') as f:
#     long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description='Interaction package for Agilent ChemStation',
    # long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    url='https://gitlab.com/larsyunker/agcs',
    packages=PACKAGES,
    # license=license,
    python_requires='>=3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Operating System :: OS Independent',
        'Natural Language :: English'
    ],
    # keywords=KEYWORDS,
    install_requires=[
        'numpy',
        'matplotlib',
        'unithandler==1.2.2',
    ],
)
