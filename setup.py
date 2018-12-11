import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='mafs',
    version='0.2',
    license='MIT',

    author='Justin Chadwell',
    author_email='jedevc@gmail.com',

    url='https://github.com/jedevc/mafs',
    description='Quickly conjure up virtual fileysystems',
    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=setuptools.find_packages(),
    install_requires=[
        'fusepy'
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Filesystems'
    ]
)
