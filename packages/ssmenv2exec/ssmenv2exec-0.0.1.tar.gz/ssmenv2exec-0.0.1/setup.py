import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ssmenv2exec',
    version='0.0.1',
    description='Pass AWS SSM parameters as environment variables when executing a process',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jowage58/ssmenv2exec/',
    author='John Wagenleitner',
    author_email='johnwa@mail.fresnostate.edu',
    keywords='aws ssm paraemters environment',
    py_modules=['ssmenv2exec'],
    python_requires='>=3.6, <4',
    install_requires=['boto3>=1.5'],
    entry_points={
        'console_scripts': [
            'ssmenv2exec=ssmenv2exec:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/jowage58/ssmenv2exec/issues',
        'Source': 'https://github.com/jowage58/ssmenv2exec/',
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
