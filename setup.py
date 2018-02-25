from setuptools import setup

setup(name='unit_parser',
      version='0.2',
      description='Unit Parser and Conversions',
      long_description=open('README.md').read(),
      keywords=['unit', 'conversion', 'parsing',
                'physics', 'engineering'],
      url='https://github.com/rwilson4/unit_parser',
      author='Bob Wilson',
      author_email='bob@convexanalytics.com',
      licence='Apache 2.0',
      packages=['unit_parser'],
      include_package_data=True,
      package_data={
          'unit_parser': ['units/*.txt']
      },
      entry_points={
          'console_scripts': [
              'convert=unit_parser.convert:main'
          ]
      },
      zip_safe=False)
