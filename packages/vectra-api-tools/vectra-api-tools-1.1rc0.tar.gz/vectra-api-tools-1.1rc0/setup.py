from setuptools import setup

with open('README.md', 'r') as fh:
    long_desc = fh.read()

setup(
    name='vectra-api-tools',
    description='Vectra API client library',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    version='1.1rc0',
    author='Vectra',
    author_email='tme@vectra.ai',
    url='https://github.com/vectranetworks/vectra_api_tools',
    license='Apache 2.0',
    package_dir={
        'vat': 'modules'
    },
    packages=['vat'],
    install_requires=['requests', 'pytz', 'cabby', 'stix'],
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Utilities'
    ]
)
