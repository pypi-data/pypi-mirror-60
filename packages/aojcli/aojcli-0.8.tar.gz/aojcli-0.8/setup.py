from setuptools import setup, find_packages

requires = ["requests", "texttable"]

setup(
    name='aojcli',
    version='0.8',
    description='AOJ submit tool',
    url='https://github.com/kamaboko123/aojcli',
    author='kamaboko123',
    author_email='6112062+kamaboko123@users.noreply.github.com',
    license='LGPL',
    packages=['aojcli'],
    install_requires=requires,
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': ['aojcli=aojcli.aojcli:main']
    },
)

