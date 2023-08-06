from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='url_parser',
      version='0.9.6',
      description='Parse url and get all the different parts out of it',
      url='https://bitbucket.org/OddAdapted/url_parser/src/master/',
      author='Odd Jøren Røland',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author_email='odd@adapted.no',
      license='MIT',
      packages=['url_parser'],
      zip_safe=False)