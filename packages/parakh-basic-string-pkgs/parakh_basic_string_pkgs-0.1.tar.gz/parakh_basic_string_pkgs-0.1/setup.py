
from setuptools import setup
setup(name='parakh_basic_string_pkgs',
      version='0.1',
      author='parakhtayal',
      author_email="parakh.tayal@sganalytics.com",
      license='MIT',
      packages=['parakh_string_repl','parakh_num_rev'],
	  description='Basic packages which is used in basic programs while learning a language',
      long_description="First Package replaces $ in a string while passing two arguments, first giving string and second the replacement character; Second package reverses num while giving integer and receiving integer itself",
      zip_safe=False)