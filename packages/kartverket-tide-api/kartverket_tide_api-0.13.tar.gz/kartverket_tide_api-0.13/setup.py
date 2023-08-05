from distutils.core import setup
setup(
  name = 'kartverket_tide_api',
  packages = ['kartverket_tide_api', 'kartverket_tide_api/tideobjects', 'kartverket_tide_api/tests',
              'kartverket_tide_api/parsers', 'kartverket_tide_api/exceptions'],
  version = '0.13',
  license='MIT',
  description = 'This is a unofficial library for the kartverket tide api',
  author = 'Mats Johan Pedersen',
  author_email = 'matspedersen@protonmail.com',
  url = 'https://github.com/matsjp/kartverket_tide_api',
  download_url = 'https://github.com/matsjp/kartverket_tide_api/archive/v0.13-alpha.tar.gz',
  keywords = ['kartverket'],
  install_requires=[
          'requests',
          'vcrpy',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
  ],
)