import setuptools

with open('README.rst') as file:

    readme = file.read()

name = 'md4c'

version = '0.0.0'

author = 'Exahilosys'

url = f'https://github.com/{author}/{name}'

setuptools.setup(
    name = name,
    version = version,
    author = author,
    url = url,
    packages = setuptools.find_packages(),
    license = 'MIT',
    description = 'Markdown parsing.',
    long_description = readme
)
