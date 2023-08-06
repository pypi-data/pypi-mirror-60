from setuptools import setup, Command
import os
import sys


thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = [] # Examples: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

print("Req:")
print(install_requires)

setup(name='atspy',
      version='0.2.1',
      description='Automated Time Series in Python',
      url='https://github.com/firmai/atspy',
      author='snowde',
      author_email='d.snow@firmai.org',
      license='MIT',
      packages=['atspy'],
      install_requires=[
          install_requires

      ],
      zip_safe=False)
