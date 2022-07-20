from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()

VERSION = '0.2.5'
DESCRIPTION = 'Symmetric cryptography module'

# Setting up
setup(
    name="listcrypt",
    version=VERSION,
    license="MIT",
    author="JustScott",
    author_email="<justscottmail@protonmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    url = "https://github.com/JustScott/ListCrypt",
    project_urls={
        "Bug Reports":"https://github.com/JustScott/ListCrypt/issues",
    },
    package_dir={"":"src"},
    packages=["listcrypt"],
    install_requires=[],
    keywords=['python','encryption','decryption','cryptography'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.0',
        'Topic :: Security :: Cryptography',
    ]
)
