from distutils.core import setup

setup(
    name='navigator-recorder',
    version='0.1.0',
    author='haphut',
    author_email='haphut@gmail.com',
    packages=['navirec'],
    url='https://github.com/HSLdevcom/navigator-recorder/',
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
