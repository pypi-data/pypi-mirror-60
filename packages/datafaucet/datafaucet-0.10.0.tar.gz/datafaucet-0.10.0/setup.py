import os
from glob import glob
from setuptools import setup

# the name of the package
name = 'datafaucet'
submodules = ['cli', 'web', 'pandas', 'spark', 'dask']
packages = [name] + ['{}.{}'.format(name, sm) for sm in submodules]

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))
pkg_root = pjoin(here, name)

version_ns = {}
with open(pjoin(here, name, '_version.py')) as f:
    exec(f.read(), {}, version_ns)

setup_args = dict(
    name=name,
    version=version_ns['__version__'],
    description='Productivity Utilities for Data Science with Python Notebooks',
    url='http://github.com/natbusa/datafaucet',
    author='Natalino Busa',
    author_email='natalino.busa@gmail.com',
    license='MIT',
    packages=packages,
    scripts=glob(pjoin('scripts', '*')),
    zip_safe=False,
    platforms="Linux, Mac OS X, Windows",
    keywords=['Interactive', 'Interpreter', 'Shell', 'Web'],
    classifiers=['Intended Audience :: Developers'],
)

install_requires = [
    # cli
    'traitlets',
    'cookiecutter',

    #datafaucet
    'numpy>=1.14',
    'pandas',
    'dask[complete]>=2.9.0',

    #datafaucet io
    'pyarrow',
    'fastparquet',
    'sqlalchemy',
    's3fs',

    # datafaucet visualization
    'bokeh',
    'seaborn',

    # dataframe methods
    'HLL',
    'unidecode',
    'faker',
    'requests',

    # datafaucet project
    'ruamel.yaml',
    'jinja2',
    'jsonschema',
    'ipykernel',
    'nbconvert',
    'python-dotenv',

    # datafaucet logging
    'gitpython',
    'kafka-python',

    # utils
    'python-dateutil',
    'cryptography'
]

try:
    #if pyspark is already installed skip pyspark
    import pyspark
except ImportError:
    install_requires.append('pyspark')


setup_args['include_package_data'] = True

if __name__ == '__main__':
    setup(**setup_args, install_requires = install_requires )
