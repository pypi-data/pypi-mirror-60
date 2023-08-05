import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='mango-jwt',
    version='1.3.2',
    packages=find_packages(),
    install_requires=[
        "Django>=2.0",
        "djangorestframework",
        "passlib",
        "PyJWT",
        "pymongo",
        "pytz",
        "dnspython"
    ],
    include_package_data=True,
    description='JWT Authentication for Django Rest Framework and MongoDB',
    long_description=README,
    url="https://github.com/srijannnd/mango-jwt",
    author='Srijan Anand',
    author_email='srijan.pydev@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
