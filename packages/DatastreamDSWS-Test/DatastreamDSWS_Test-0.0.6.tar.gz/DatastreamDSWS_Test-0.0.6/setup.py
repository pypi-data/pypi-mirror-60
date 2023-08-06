import setuptools

setuptools.setup(
    name='DatastreamDSWS_Test',
    version='0.0.6',
    packages=['DatastreamDSWS_Test'],
    url='https://github.com/DatastreamDSWS/Datastream',
    license='MIT',
    author='Vidya Dinesh',
    author_email='datastream@refinitiv.com',
    description='Python API Package for Refinitiv Datastream Webservices (DSWS) - TEST Version',
    long_description='Python API package for Refinitiv Datastream Webservices (DSWS) - TEST -Version',
    install_requires=[
        'pandas',
        'urllib3',
        'datetime'
      ],
    python_requires='>=3'

)
