# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, 'tiledtmxloader')
import tiledtmxloader


from setuptools import setup, find_packages

setup(
    name='tiledtmxloader',
    version=tiledtmxloader.__version__,
    author='DR0ID',
    author_email='dr0iddr0id@gmail.com',
    maintainer='DR0ID',
    url='https://code.google.com/p/pytmxloader/',
    download_url='https://code.google.com/p/pytmxloader/downloads/list',
    description='',
    long_description=tiledtmxloader.tmxreader.__doc__,
    install_requires=["pyglet"],
    package_dir={'tiledtmxloader': 'tiledtmxloader'},
    packages=['tiledtmxloader'],
    keywords='pygame tiled mapeditor game map',
    license='New BSD License',
)
