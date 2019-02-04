
"""zconfigparser setup file."""

# from setuptools import setup, find_packages
from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

with open('VERSION') as f:
    version = f.read().strip()


setup(
    name='zconfigparser',
    version=version,
    url='https://github.com/openandclose/zconfigparser',
    license='MIT',
    author='Open Close',
    author_email='openandclose23@gmail.com',
    description='Extend ConfigParser to add some inheritance functionality',
    long_description=readme,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ],
    keywords='ini config configparser',
    # packages=find_packages(exclude=['docs', 'tests', 'nonpubfiles']),
    py_modules=['zconfigparser'],
    python_requires='~=3.5',
    extras_require={
        'test': ['pytest'],
        'dev': ['pytest', 'sphinx'],
    },
    zip_safe=False,
)
