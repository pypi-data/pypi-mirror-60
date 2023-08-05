from setuptools import setup

setup(name='pybility',
      version = '1.0',
      description = 'Python probability distribution sampling and plotting',
      packages = ['pybility'],
      install_requires = ['matplotlib', 'drawilleplot', 'Pillow', 'wheel'],
      include_package_data = True,
      package_dir = {'pybility':'pybility'},
      package_data = {'pybility':['data/*.txt']},
      author = 'Marios Tsatsos',
      author_email = 'mariostsatsos@gmail.com',
      zip_safe=False)
