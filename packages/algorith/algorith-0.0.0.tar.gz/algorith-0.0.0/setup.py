from setuptools import setup, find_packages

INSTALL_DEPS = ['numpy',
                'scipy',
                'matplotlib',
                'sympy'
               ]
TEST_DEPS = ['pytest']
DEV_DEPS = []

setup(name='algorith',
      version='0.0.0',
      url='https://github.com/ryu577/algorithms',
      license='MIT',
      author='Rohit Pandey',
      author_email='rohitpandey576@gmail.com',
      description='All kinds of algorithms.',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      zip_safe=False,
      install_requires=INSTALL_DEPS,
      python_requires='!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
      # List additional groups of dependencies here (e.g. development
      # dependencies). You can install these using the following syntax,
      # for example:
      # $ pip install -e .[dev,test]
      extras_require={
          'dev': DEV_DEPS,
          'test': TEST_DEPS,
      },
     )
