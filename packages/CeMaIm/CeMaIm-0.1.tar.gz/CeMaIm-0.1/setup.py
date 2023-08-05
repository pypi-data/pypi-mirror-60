from pathlib import Path
from setuptools import setup, find_packages

setup(
    name='CeMaIm',
    version='0.1',
    description='Program for import certificates to email client',
    long_description=Path('long_text.html').read_text(),
    author='Lukas Vacek',
    author_email='vaceklu6@fit.cvut.cz',
    license='GPLv3',
    url='https://github.com/vaceklu6/certs-mail-import',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
    package_data={
        'cemaim': ['*.ui'],
    },
    install_requires=[
        'pyqt5', 'unicode', 'pycryptodome', 'pyOpenSSL', 'click', 'requests', 'bs4', 'unidecode', 'importlib.resources'
    ],
    entry_points={
        'console_scripts': [
            'cemaim = cemaim:cli',
        ],
    },
)
