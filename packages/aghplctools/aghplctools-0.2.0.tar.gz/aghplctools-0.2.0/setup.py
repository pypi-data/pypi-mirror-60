from setuptools import setup, find_packages

NAME = 'aghplctools'
VERSION = '0.2.0'
AUTHOR = 'Lars Yunker / Hein Group'

PACKAGES = find_packages()
# KEYWORDS = ', '.join([
# ])

with open('LICENSE') as f:
    lic = f.read()
    lic.replace('\n', ' ')

# with open('README.MD') as f:
#     long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description='Interaction package for Agilent ChemStation report files',
    # long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    url='https://gitlab.com/heingroup/aghplctools',
    packages=PACKAGES,
    license=lic,
    python_requires='>=3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Operating System :: Microsoft :: Windows',
        'Natural Language :: English'
    ],
    # keywords=KEYWORDS,
    install_requires=[
        'numpy',
        'matplotlib',
        'pythoms',  # todo get a lighter-weight XLSX solution
        'unithandler==1.2.2',
        'hein_utilities>=0.1.2',
    ],
    dependency_links=[
        'git+https://gitlab.com/heingroup/hein_utilities.git#egg=hein_utilities',
    ],
)
