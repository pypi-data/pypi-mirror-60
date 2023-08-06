from setuptools import setup

from tinyapp import __version__


requirements = [
    'pymysql',
    'pandas'
]

setup(
    name='tinyapp',
    version=__version__,
    packages=['tinyapp'],
    url='',
    license='Apache License',
    author='lison',
    author_email='linzongxian@vip.qq.com',
    description='Tiny application framework',
    test_suite='tests',
    install_requires=requirements
)
