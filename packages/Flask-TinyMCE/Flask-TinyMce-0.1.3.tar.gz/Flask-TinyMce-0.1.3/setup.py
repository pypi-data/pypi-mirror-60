"""
    Flask-TinyMce
    @Time    : 2020/2/1 11:29
    @Author  : wumao
    @Email   : kanhebei@dingtalk.com
"""
from setuptools import setup
from os import path

basedir = path.abspath(path.dirname(__file__))

with open(path.join(basedir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Flask-TinyMce',
    version='0.1.3',
    url='https://github.com/kanhebei/flask-tinymce',
    license='MIT',
    author='WuMao',
    author_email='kanhebei@dingtalk.com',
    description='flask tinymce',
    long_description=long_description,
    packages=['flask_tinymce'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'WTForms'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)