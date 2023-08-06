from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(name='mstatistics',
      #version='0.1.1b9',
      version='0.1.2',
      description='Provide a robust statistical library for Python to be used in conjunction with NumPy, SciPy, Pandas, and other common data science packages.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/MaxMifkovic/mstatistics',
      author='Max Mifkovic',
      author_email='maxmifkovic@gmail.com',
      license='MIT',
      #packages=['mstatistics'],
      packages=find_packages(),
      zip_safe=False)
