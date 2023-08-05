from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='ddbimp',
    version='0.4',
    description='Easily load data from CSV to test out your DynamoDB table design',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/AlexJReid/dynamodb-dev-importer',
    author='AlexJReid',
    author_email='alexjreid@me.com',
    license='Apache',
    packages=['ddbimp'],
    install_requires=['boto3'],
    entry_points = {
        'console_scripts': ['ddbimp=ddbimp.cli:main']
    },
    zip_safe=False)
