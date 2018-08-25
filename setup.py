import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='mafs',
    version='0.0.1',
    license='MIT',

    url='https://github.com/jedevc/mafs',
    description='Quickly conjure up virtual fileysystems',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Justin Chadwell',
    author_email='jedevc@gmail.com',

    packages=setuptools.find_packages(),
    install_requires=[
        'fusepy'
    ]
)
