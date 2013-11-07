from distutils.core import setup

setup(
    name='NavigatorRecorderServer',
    version='0.1.0',
    author='haphut',
    author_email='haphut@gmail.com',
    packages=['navirec'],
    #packages=['navirec', 'navirec.test'],
    #scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    #url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='Server component for recording Navigator activity.',
    long_description=open('README.md').read(),
    install_requires=[
        "Flask",
        "requests",
        "jsonschema",
        "strict-rfc3339",
        "pytz",
    ],
)
