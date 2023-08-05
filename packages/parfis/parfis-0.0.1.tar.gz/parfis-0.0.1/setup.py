from distutils.core import setup
setup(
  name = 'parfis',
  packages = ['parfis'],
  version = '0.0.1',
  license='MIT',
  description = 'Particles in field simulator',
  author = 'Ginko Balboa',
  author_email = 'ginkobalboa3@gmail.com',
  url = 'https://github.com/GinkoBalboa/parfis',
  download_url = 'https://github.com/GinkoBalboa/parfis/archive/pypi-0_0_1.tar.gz',
  keywords = ['physics', 'simulation', 'electromagnetic', 'particles', 'particle-in-cell', 'field'],
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7'
  ],
)