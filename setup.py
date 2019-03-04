from setuptools import setup

setup(name='wrds_tools',
      version='0.0.1',
      description='Various tools to create a connection to the WRDS service and download commonly used data.',
      author='Julian Barg',
      author_email='barg.julian@gmail.com',
      packages=['wrds_tools'],
      install_requires=['pandas', 'wrds']
      )
