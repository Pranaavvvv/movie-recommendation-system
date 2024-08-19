# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

def read_long_description(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()

setup(
    name='movie-recommendation-system',  # Use a more descriptive name if needed
    version='0.0.1',
    author='Pranav Dharwadkar',
    author_email='pranav.djsce24@gmail.com',
    description='Movie Recommendation System',
    long_description=read_long_description("README.md"),
    long_description_content_type='text/markdown',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.6',
    install_requires=[
        'streamlit',
        # Add other requirements here if needed
    ],
)
