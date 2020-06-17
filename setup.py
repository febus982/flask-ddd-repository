"""
Flask-DDD-Repository
-------------

Domain-Driven-Design repository pattern implementation for Flask
"""
import re

from setuptools import setup

with open("src/flask_ddd_repository/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name='Flask-DDD-Repository',
    version=version,
    install_requires=["Flask>=1.1", "SQLAlchemy>=1.3"],
)



# setup(
#     name='Flask-DDD-Repository',
#     version='1.0',
#     # url='http://example.com/flask-sqlite3/',
#     # license='BSD',
#     author='Federico Busetti',
#     author_email='729029+febus982@users.noreply.github.com',
#     description='Domain-Driven-Design repository pattern implementation for Flask',
#     long_description=__doc__,
#     py_modules=['flask_ddd_repository'],
#     # if you would be using a package instead use packages instead
#     # of py_modules:
#     # packages=['flask_ddd_repository'],
#     zip_safe=False,
#     include_package_data=True,
#     platforms='any',
#     install_requires=[
#         'Flask'
#     ],
#     classifiers=[
#         'Environment :: Web Environment',
#         'Intended Audience :: Developers',
#         'License :: OSI Approved :: BSD License',
#         'Operating System :: OS Independent',
#         'Programming Language :: Python',
#         'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
#         'Topic :: Software Development :: Libraries :: Python Modules'
#     ]
# )