import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='wrds_tools',
                 version='0.0.6',
                 description='Various tools to create a connection to the WRDS service and download commonly used ' +
                             'data.',
                 long_description=long_description,
                 long_description_content_type='text/markdown',
                 author='Julian Barg',
                 author_email='barg.julian@gmail.com',
                 packages=['wrds_tools'],
                 install_requires=['pandas', 'wrds']
                 )
