from setuptools import setup, find_packages

setup(
  name = 'ReviewsLoader',
  packages=find_packages(),
  version = '0.1',
  license='MIT',
  description = 'Utility for downloading app reviews in the App Store.',
  author = 'Maksim Vorontsov',
  author_email = 'social.maksim.vrs@gmail.com',
  url = 'https://gitlab.com/maksimvrs/reviewsloader',
  download_url = 'https://gitlab.com/maksimvrs/reviewsloader/-/archive/master/reviewsloader-master.tar.gz',
  keywords = ['parser', 'AppStore', 'async'],
  install_requires=[
        'aioify',
        'aiohttp',
        'click',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)