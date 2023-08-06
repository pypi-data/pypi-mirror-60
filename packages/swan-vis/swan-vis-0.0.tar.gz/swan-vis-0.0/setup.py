
from setuptools import setup
setup(
  name = 'swan-vis',
  packages = ['swan-vis'],
  version = '0.0',
  license='MIT',  description = 'swan is a tool for visualizing and analyzing transcript isoforms',
  author = 'Fairlie Reese',
  author_email = 'fairlie.reese@gmail.com',
  url = 'https://github.com/fairliereese/swan',
  download_url = 'https://github.com/fairliereese/swan/archive/v0.0-alpha.tar.gz',
  keywords = ['swan', 'transcription', 'isoform'],
  install_requires=[
          'networkx',
          'numpy',
          'pandas',
          'matplotlib',
          'fpdf',
          'sqlite3'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research ',    
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python :: 3.7',
  ],
)