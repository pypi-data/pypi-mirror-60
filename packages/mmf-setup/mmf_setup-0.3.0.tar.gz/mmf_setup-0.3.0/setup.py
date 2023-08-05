"""Python Tools.

This is a meta-package providing an easy way to initialize a python
distribution to have the tools I commonly use.

**Source:**
  https://bitbucket.org/mforbes/mmf_setup
**Issues:**
  https://bitbucket.org/mforbes/mmf_setup/issues
"""
import os.path
import sys

from setuptools import setup, find_packages

NAME = "mmf_setup"

install_requires = [
    'nbstripout>=0.2.0',
    'python-hglib',
    'twine',
    'readme_renderer',
]

test_requires = [
    'notebook',
    'pytest>=2.8.1',
    'pytest-cov>=2.2.0',
    'pytest-flake8',
    'coverage',
    'mercurial',
    'twine',
]

extras_require = {
    # Hack so that pip install -e .[test] works for testing.
    # https://inneka.com/programming/python/pip-install-test-dependencies-for-tox-from-setup-py/
    'test': test_requires,
    'nbextensions': [
        'jupyter_contrib_nbextensions'
    ]

}


# Remove NAME from sys.modules so that it gets covered in tests. See
# http://stackoverflow.com/questions/11279096
for mod in sys.modules.keys():
    if mod.startswith(NAME):
        del sys.modules[mod]
del mod

# Get the long description from the README.rst file
_HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(_HERE, 'README.rst')) as _f:
    LONG_DESCRIPTION = _f.read()


setup(name=NAME,
      version='0.3.0',
      packages=find_packages(exclude=['tests']),

      install_requires=install_requires,
      tests_require=test_requires,
      extras_require=extras_require,

      scripts=['bin/mmf_setup', 'bin/mmf_initial_setup', 'bin/mmf_setup_bash.py'],

      # Include data from MANIFEST.in
      include_package_data=True,

      # Metadata
      author='Michael McNeil Forbes',
      author_email='michael.forbes+bitbucket@gmail.com',
      url='https://bitbucket.org/mforbes/mmf_setup',
      description="Python Tools",
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/x-rst',

      license='GNU GPLv2 or any later version',

      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 3',
      ],

      keywords='ipython jupyter notebook setup mercurial',
      )
