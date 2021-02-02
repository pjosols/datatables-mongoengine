from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='mongoengine_datatables',
      version='0.1.2',
      description='Mixin for connecting DataTables to MongoDB with MongoEngine.',
      long_description=readme(),
      url='https://github.com/pauljolsen/mongoengine-datatables',
      author='Paul Olsen',
      author_email='paul@wholeshoot.com',
      license='MIT',
      packages=['mongoengine_datatables'],
      install_requires=['mongoengine'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.7',
          'Topic :: Database :: Database Engines/Servers',
      ],
      keywords='flask django mongoengine mongodb',
      include_package_data=True,
      zip_safe=False
      )
