"""
    Important Points::
    => private repository needs entry in dependency_links
"""
from setuptools import setup

setup(
    name = 'py_sql',
    version = '1.0.0',
    url = '',
    author = 'Arslan Haider Sherazi',
    author_email = 'arslanhaider95@hotmail.com',
    description = 'Python Mysql Library',
    long_description=open('README.md').read(),
    packages = ['py_sql'],
    install_requires = [
        'mysql-connector==2.2.9'
    ],
    # dependency_links=[
    #     # Make sure to include the #egg portion so the install_requires recognizes the package
    #     'git+https://gitlab.com/arslansherazi/py_sql.git#egg=py_sql-1.0.0'
    # ]
)
