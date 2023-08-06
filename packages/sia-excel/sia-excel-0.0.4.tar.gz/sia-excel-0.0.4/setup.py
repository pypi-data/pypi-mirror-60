from setuptools import setup, find_packages

setup(
    name='sia-excel',
    version='0.0.4',
    author='Maxim Kupfer',
    author_email='mkupfer@staffingindustry.com',
    packages=find_packages(),
    install_requires=['openpyxl>=3.0.3'],
    python_requires='>=3.6',
)
