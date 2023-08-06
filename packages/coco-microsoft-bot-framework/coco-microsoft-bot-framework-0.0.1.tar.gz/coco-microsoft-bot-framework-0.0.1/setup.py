import os

from setuptools import setup
from setuptools import find_packages


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


long_description = read("README.md")

setup(name='coco-microsoft-bot-framework',
      version='0.0.1',
      description='CoCo(Conversational Components) SDK for using components with Microsoft Bot Framework.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Victor Vasiliev',
      author_email='victor@a-i.com',
      url='https://github.com/conversationalcomponents/coco-microsoft-bot-framework',
      license='MIT',
      install_requires=['coco-sdk', 'botbuilder-core'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=find_packages(),
      python_requires=">=3.6"
)
