from setuptools import setup

setup(
    name='idmrc',
    version='0.0.2',
    packages=['idmrc'],
    author="Lukas Jurk",
    author_email="lukas.jurk@tu-dresden.de",
    description="a simple idmrc",
    license="GPLv3",
    keywords="requests rest",
    url="https://gitlab.hrz.tu-chemnitz.de/slm/rc",
    entry_points={
        'console_scripts': ['rc=idmrc.idmrc:cli']
    },
    install_requires=[
        'Click==7.0',
        'requests==2.22.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
