from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name="tjcsvreformatter",
    version="0.0.2",
    description="reformat old csvs into new format specified here:https://wiki.mgcorp.co/pages/viewpage.action?spaceKey=ENGADS&title=DSP+CSV",
    author='Maryia Hanina',
    author_email="maryia.ganina@gmail.com",
    url="https://stash.mgcorp.co/projects/ADS/repos/tj-reformat-csvs/browse",
    packages=find_packages(where='src'),
    python_requires='>=3.6.*',
    install_requires=['pandas', 'datetime', 'argparse'],
    entry_points={  # Optional
        'console_scripts': [
            'reformat=reformat:main',
        ],
    },

)
