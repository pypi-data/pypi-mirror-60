from setuptools import setup

setup(
    name            = 'pyupbit',
    version         = '0.2.6',
    description     = 'python wrapper for Upbit API',
    url             = 'https://github.com/sharebook-kr/pyupbit',
    author          = 'Lukas Yoo, Brayden Jo',
    author_email    = 'brayden.jo@outlook.com, jonghun.yoo@outlook.com, pystock@outlook.com',
    install_requires= ['requests', 'pandas', 'pyjwt'],
    license         = 'MIT',
    packages        = ['pyupbit'],
    zip_safe        = False
)