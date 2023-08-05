import setuptools

with open('README.md') as f:
    long_description = f.read()

with open('VERSION') as f:
    version = f.read()

name = 'piqok'
setuptools.setup(
    name=name,
    version=version,
    author='Gilad Kutiel',
    author_email='gilad.kutiel@gmail.com',
    description='Get help with json',
    long_description=long_description,
    url='https://github.com/piqok/piqok',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'piqok=piqok.piqok:main'
        ],
    }
)
