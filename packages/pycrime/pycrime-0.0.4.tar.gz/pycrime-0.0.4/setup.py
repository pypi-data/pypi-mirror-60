from setuptools import find_packages, setup

from pycrime.__version__ import __version__

setup(
    name='pycrime',
    version=__version__,
    author='Luke Hodkinson',
    author_email='furious.luke@gmail.com',
    maintainer='Luke Hodkinson',
    maintainer_email='furious.luke@gmail.com',
    description='Fetch crime statistics from the ExpenseCheck crime statistics API.',
    url='https://github.com/furious-luke/pycrime',
    long_description='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License'
    ],
    packages=find_packages(exclude=['tests', 'extern']),
    include_package_data=True,
    package_data={'': ['*.txt', '*.js', '*.html', '*.*']},
    install_requires=[
        'base-api==0.0.1'
    ],
    extras_require={},
    entry_points={},
    zip_safe=True
)
