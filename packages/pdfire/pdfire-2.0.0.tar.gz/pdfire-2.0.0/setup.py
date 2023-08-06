import setuptools
from distutils.core import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='pdfire',
    version='2.0.0',
    license='MIT',
    description='Python client for the PDFire.io API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='modernice Ltd.',
    author_email='info@modernice.ltd',
    url='https://github.com/modernice/pdfire-python',
    keywords=['PDFire', 'client', 'API', 'library', 'PDF', 'converter'],
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
    install_requires=[
        'python-dateutil'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
)
