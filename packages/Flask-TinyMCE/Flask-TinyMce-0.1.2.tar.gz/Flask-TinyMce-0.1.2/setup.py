"""
    Flask-TinyMce
    @Time    : 2020/2/1 11:29
    @Author  : wumao
    @Email   : kanhebei@dingtalk.com
"""
from setuptools import setup

setup(
    name='Flask-TinyMce',
    version='0.1.2',
    url='https://github.com/kanhebei/flask-tinymce',
    license='MIT',
    author='WuMao',
    author_email='kanhebei@dingtalk.com',
    description='flask tinymce',
    long_description=__doc__,
    py_modules=['flask_tinymce'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
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