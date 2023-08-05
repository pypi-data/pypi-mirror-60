''' Setup for package '''
from setuptools import setup, find_packages

setup(
    name='nms-api-helpers',
    version='0.1',
    description="nms api helpers",
    long_description=""" NMS API Helpers and Wrappers """,
    classifiers=[],
    keywords='',
    author='Jandon Limited',
    author_email='automation@jandon.co.uk',
    url='https://github.com/Jandon-Ltd/nms-api-helpers',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "pyyaml",
        "requests",
        "urllib3"
    ],
)
