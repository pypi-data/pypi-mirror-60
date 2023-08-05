"""
Flask-PyMongol
-------------

TODO: Add docs
"""
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Flask-PyMongol',
    version='0.1.1',
    url='https://github.com/upeguiborja/flask-pymongol',
    license='BSD',
    author='Mateo Upegui Borja',
    author_email='upeguiborja@gmail.com',
    description='A less is more Pymongo wrapper for Flask',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    python_requires=">= 3.6",
    install_requires=[
        'Flask',
        'pymongo'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
