from setuptools import setup

setup(name='quantly',
      version='0.1',
      description='A multi-tool financial suite for equity traders.',
      url='https://github.com/BluechipData/quantly',
      author='Brandon Boisvert',
      license='MIT',
      packages=['quantly'],
      install_requires=['pandas', 'alphavantage', 'pystan', 'fbprophet'],
      zip_safe=False)
