from setuptools import find_packages, setup


# TODO: I would rather import this as opposed to parsing it, but when
# importing during installation it breaks due to the __init__.py file
# trying to load in other modules.
def parse_version():
    with open('./pycrime/__version__.py') as f:
        return f.read().split('=')[1].strip()[1:-1]


setup(
    name='pycrime',
    version=parse_version(),
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
