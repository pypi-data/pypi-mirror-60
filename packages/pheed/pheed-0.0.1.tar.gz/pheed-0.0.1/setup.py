"""Setup file
"""

import setuptools

import pheed

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='pheed',
                 version=pheed.__version__,
                 description='Python tools for aggregating physics literature',
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url=pheed.__github_url__,
                 author='James W. Kennington',
                 author_email='jameswkennington@gmail.com',
                 license='MIT',
                 packages=setuptools.find_packages(),
                 zip_safe=False)
