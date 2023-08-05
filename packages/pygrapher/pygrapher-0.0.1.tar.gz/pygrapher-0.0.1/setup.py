from setuptools import setup, find_packages

setup(
    name = 'pygrapher',
    version = '0.0.1',
    description = 'A simple, excel-like plot fitting library',
    license = 'MIT License',
    url = 'https://github.com/610yilingliu/py-grapher',
    author = 'Yiling Liu',
    author_email = 'yilingliu1994@gmail.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    python_requires='>=3.6',
    install_requires = ['scipy', 'matplotlib','pandas','numpy'],
)