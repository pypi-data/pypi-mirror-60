import setuptools
import pypyrus_logbook as logbook

with open('README.md', 'r') as fh:
    long_description = fh.read()

install_requires = ['sqlalchemy>=1.3.1']

author = logbook.__author__
email = logbook.__email__
version = logbook.__version__
description = logbook.__doc__
license = logbook.__license__

setuptools.setup(
    name='pypyrus-logbook',
    version=version,
    author=author,
    author_email=email,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    license=license,
    url='https://github.com/t3eHawk/logbook',
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
