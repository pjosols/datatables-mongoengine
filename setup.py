from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="datatables_mongoengine",
    version="0.1.7",
    description="MongoEngine QuerySet class for populating DataTables from MongoEngine.",
    long_description=readme(),
    url="https://github.com/pauljolsen/datatables-mongoengine",
    author="Paul Olsen",
    author_email="paul@wholeshoot.com",
    license="MIT",
    long_description_content_type="text/markdown",
    packages=["datatables_mongoengine"],
    install_requires=["mongoengine"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Topic :: Database :: Database Engines/Servers",
    ],
    keywords="flask django mongoengine mongodb",
    include_package_data=True,
    zip_safe=False,
)
