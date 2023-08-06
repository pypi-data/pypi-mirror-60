import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='example-lfuncs',
      version='0.1',
      description='A few functions to teach Python and PIP',
      url='https://github.com/diging-training/example-package-lfuncs',
      author='jdamerow',
      author_email='jdamerow@asu.edu',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=setuptools.find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.6')
