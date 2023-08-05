from __future__ import unicode_literals
from __future__ import absolute_import
import setuptools
from distutils.core import setup

setup(name='ActivityStream',
      version='0.3.0',
      url='http://sf.net/p/activitystream',
      packages=['activitystream', 'activitystream.storage'],
      install_requires=['pymongo>=2.8'],
      license='Apache License, http://www.apache.org/licenses/LICENSE-2.0',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'License :: OSI Approved :: Apache Software License',
          ],
      )
