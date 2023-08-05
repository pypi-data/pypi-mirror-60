from pathlib import Path
from setuptools import setup, find_packages

setup(
    name='ClustIPy',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/shuichiro-makigaki/ClustIPy',
    license='MIT',
    author='Shuichiro MAKIGAKI',
    author_email='shuichiro.makigaki@gmail.com',
    description='Clustering IPs',
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    entry_points='''
        [console_scripts]
        clustipy=clustipy.cmd.clustipy:main
    ''',
)
