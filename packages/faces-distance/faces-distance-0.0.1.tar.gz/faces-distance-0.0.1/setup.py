import io
import re

from setuptools import find_packages, setup

with io.open('facedis/__init__.py', encoding='utf8') as v:
    version = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", v.read(), re.M)
    if version:
        version = version.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

with open("README.md", "r") as fh:
    long_description = fh.read()

dev_requirements = ['numpy']
integration_test_requirements = ['pytest', 'pytest-flask']
prod_requirements = ['numpy']

setup(
    name='faces-distance',
    version=version,
    author='Frank Ricardo R, Henrique Borba',
    author_email='frankjony17@gmail.com',
    packages=find_packages(exclude='tests'),
    python_requires='>=3.6',
    install_requires=prod_requirements,
    extras_require={
         'dev': dev_requirements,
         'integration': integration_test_requirements
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    description='Calculates faces distance accuracy as a percentage.',
    include_package_data=True,
    license='COPYRIGHT',
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Information Technology',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6'
    ],
    keywords=('distance', 'face')
)
