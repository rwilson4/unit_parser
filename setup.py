from setuptools import setup

setup(name='yaucl',
      version='0.1',
      description='Yet Another Unit Conversion Library',
      keywords=['unit', 'conversion', 'parsing',
                'physics', 'engineering'],
      url='https://github.com/rwilson4/yaucl',
      author='Bob Wilson',
      author_email='bob@causalityinc.com',
      licence='Apache 2.0',
      packages=['yaucl'],
      include_package_data=True,
      long_description=open('README.md').read(),
      zip_safe=False)
