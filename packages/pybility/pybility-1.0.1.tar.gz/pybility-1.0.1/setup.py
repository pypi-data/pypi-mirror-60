from setuptools import setup

setup(name='pybility',
      version = '1.0.1',
      description = 'Python probability distribution sampling and plotting',
      long_description=open('README').read(),
      packages = ['pybility', 'pybility.tests'],
      install_requires = ['matplotlib', 'drawilleplot', 'Pillow', 'wheel'],
      include_package_data = True,
      package_dir = {'pybility':'pybility'},
      package_data = {'pybility': ['data/*.txt']},
      data_files = [('pybility', ['data/data.txt', 'data/data_poisson.txt', 'data/data_binomial'])],
      author = 'Marios Tsatsos',
      author_email = 'mariostsatsos@gmail.com',
      url = 'https://test.pypi.org/project/pybility/',
      zip_safe=False)
