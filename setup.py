import os
from setuptools import setup, find_packages

version = '0.1dev'


setup(name='experimental.ploneperformance',
      version=version,
      description="Plone performance optimizations",
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['experimental'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'simplejson',
          'Zope2 >= 2.13.8',
          'five.pt >= 2.1.4',
          'Chameleon >= 2.2',
          'Products.CMFPlone >= 4.1',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
