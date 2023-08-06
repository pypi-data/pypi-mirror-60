from setuptools import setup, find_packages
from os import path
from quqie import VERSION


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()


setup(
    name='quqie',
    version=VERSION,
    url='https://github.com/maguowei/quqie',
    license='MIT',
    author='maguowei',
    author_email='imaguowei@gmail.com',
    keywords='Quqie',
    description='Quqie',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.6',
    install_requires=[
        'fire==0.2.1',
    ],
    entry_points={
        'console_scripts': [
            'quqie-cli=quqie.cli:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
