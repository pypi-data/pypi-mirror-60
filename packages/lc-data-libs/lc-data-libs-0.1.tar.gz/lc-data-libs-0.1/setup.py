import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='lc-data-libs',
    version='0.1',
    author="lc-data",
    author_email="data@gmail.com",
    description="Usefull library for lc operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/luckycart/lc-data",
    packages=['lcdata'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'google-cloud-logging',
        'google-cloud-dataproc'
    ],
 )