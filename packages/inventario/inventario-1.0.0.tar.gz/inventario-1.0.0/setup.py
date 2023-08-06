import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name = 'inventario',
    version = '1.0.0',
    py_modules = ['inventario'],
    author = 'Felipe Augusto',
    author_email = 'fasnik@gmail.com',
    description = 'Inventario para equipamentos',
    url = 'http://professorfelipe.000webhostapp.com/',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"],
    python_requires='>=3.6',
    )
